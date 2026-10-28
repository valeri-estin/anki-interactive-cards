"""Native editor toolbar integration, using Anki's own Add button and save hooks.

The compact Qt answer editor is accessible from the regular Add/Edit editor.
New note fields are injected by add_cards_will_add_note, which means users click
Anki's standard Hinzufügen/Save button. No private Svelte/DOM APIs are required.
"""
from __future__ import annotations
import weakref
import json
from pathlib import Path
from dataclasses import dataclass
from aqt import mw, gui_hooks
from aqt.qt import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QWidget,
                    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
                    QLineEdit, QTextEdit, QComboBox, QLabel, QFileDialog,
                    QMessageBox, QDialogButtonBox, Qt)
from aqt.utils import tooltip
from .core import from_json_field, clean_text
from .anki_bridge import media_filename
from .editor_data import (kind_for_model, fields_from_note_info, choice_fields,
                          sentence_fields, merge_aux_fields, validate_note)
from .localization import ui_text as t


@dataclass
class PendingFields:
    mid: int
    fields: dict
    applied: bool = False

# Only drafts explicitly configured by the user are tracked. Weak keys avoid
# keeping closed editors alive. Anki normally has one Add window at a time.
_pending = weakref.WeakKeyDictionary()
_reveal_technical = weakref.WeakKeyDictionary()
_VISIBILITY_JS = (Path(__file__).parent / 'web' / 'editor_visibility.js').read_text(encoding='utf-8')
# These fields remain part of Anki notes; only their editor rows are hidden.
_DISPLAY_FIELDS = {'Prompt', 'Explanation', 'Prompt Image', 'Audio'}


def _configure_visibility(editor, mid):
    try:
        model = mw.col.models.get(mid)
        kind = kind_for_model(model)
        technical = [f['name'] for f in model['flds'] if f['name'] not in _DISPLAY_FIELDS] if kind else []
        if not kind:
            _reveal_technical.pop(editor, None)
        reveal = bool(_reveal_technical.get(editor, False))
        # Install and update atomically; works if the webview has just been reloaded.
        editor.web.eval(_VISIBILITY_JS + '\nwindow.AICFieldVisibility.configure(' +
                        json.dumps(technical, ensure_ascii=False) + ', ' +
                        json.dumps(reveal) + ');')
    except Exception:
        # Cosmetic enhancement must never prevent editing notes in Anki.
        pass


def _refresh_visibility(editor):
    try:
        if hasattr(editor, 'get_note_info'):
            editor.get_note_info(lambda info: _configure_visibility(editor, info.mid) if info else None)
        elif getattr(editor, 'note', None):
            _configure_visibility(editor, editor.note.mid)
    except Exception:
        pass


def _toggle_technical(editor):
    try:
        _reveal_technical[editor] = not bool(_reveal_technical.get(editor, False))
        _refresh_visibility(editor)
        tooltip(t('editor.technical_shown') if _reveal_technical[editor] else t('editor.technical_hidden'))
    except Exception:
        pass



class AnswerEditor(QDialog):
    """Structured answers while leaving the regular Anki editor in charge of fields."""
    def __init__(self, model_kind, values, col, parent=None):
        super().__init__(parent)
        self.kind = model_kind
        self.values = values
        self.col = col
        self.setWindowTitle(t('editor.title'))
        self.resize(700, 470)
        outer = QVBoxLayout(self)
        outer.addWidget(QLabel(t('editor.intro')))
        if model_kind in ('choice', 'multi'):
            outer.addWidget(QLabel(t('editor.choice_intro')))
            self.table = QTableWidget(0, 3)
            self.table.setHorizontalHeaderLabels([t('editor.answer_text'), t('editor.image_file'), t('editor.correct')])
            self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            outer.addWidget(self.table, 1)
            row = QHBoxLayout()
            row.addWidget(self._button(t('editor.add_answer'), self._add_blank))
            row.addWidget(self._button(t('editor.remove_answer'), self._remove))
            row.addWidget(self._button(t('editor.choose_image'), self._choose_image))
            row.addStretch()
            outer.addLayout(row)
            try:
                options = from_json_field(values.get('Options', ''), [])
                correct = from_json_field(values.get('Correct', ''), [])
            except Exception:
                options, correct = [], []
            if not isinstance(options, list): options = []
            if not isinstance(correct, list): correct = []
            for i, item in enumerate(options):
                if isinstance(item, dict):
                    self._add_row(item.get('text',''), item.get('image',''), i in correct)
            if self.table.rowCount() == 0:
                for i in range(4): self._add_row('', '', i == 0)
            if model_kind == 'choice':
                outer.addWidget(QLabel(t('editor.single_choice')))
        else:
            form = QFormLayout()
            self.answer = QLineEdit(clean_text(values.get('Answer', '')))
            self.answer.setPlaceholderText('z. B. sono a casa')
            self.tokens = QLineEdit(' '.join(from_json_field(values.get('Tokens', ''), [])))
            self.tokens.setPlaceholderText(t('editor.auto_tokens'))
            self.alternatives = QTextEdit()
            self.alternatives.setPlaceholderText(t('editor.alternatives'))
            self.alternatives.setPlainText('\n'.join(from_json_field(values.get('Alternatives', ''), [])))
            self.distractors = QTextEdit()
            self.distractors.setPlaceholderText(t('editor.distractors'))
            self.distractors.setMaximumHeight(100)
            self.distractors.setPlainText('\n'.join(from_json_field(values.get('Distractors', ''), [])))
            self.mode = QComboBox()
            for label, value in [(t('editor.mode_both'), 'both'), (t('editor.mode_tiles'),'tiles'), (t('editor.mode_typing'),'typing')]:
                self.mode.addItem(label, value)
            idx = self.mode.findData(values.get('Mode','both'))
            self.mode.setCurrentIndex(max(0, idx))
            form.addRow(t('editor.target'), self.answer)
            form.addRow(t('editor.tokens'), self.tokens)
            form.addRow(t('editor.other_solutions'), self.alternatives)
            form.addRow(t('editor.wrong_tiles'), self.distractors)
            form.addRow(t('editor.input_mode'), self.mode)
            outer.addLayout(form)
            outer.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(t('editor.apply'))
        buttons.accepted.connect(self._validate_then_accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)
        self.aux = None

    def _button(self, label, callback):
        button = QPushButton(label)
        button.clicked.connect(callback)
        return button

    def _add_row(self, title='', image='', correct=False):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(title))
        self.table.setItem(row, 1, QTableWidgetItem(image))
        check = QTableWidgetItem('')
        check.setFlags(check.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        check.setCheckState(Qt.CheckState.Checked if correct else Qt.CheckState.Unchecked)
        self.table.setItem(row, 2, check)

    def _add_blank(self): self._add_row()
    def _remove(self):
        if self.table.currentRow() >= 0: self.table.removeRow(self.table.currentRow())

    def _choose_image(self):
        idx = self.table.currentRow()
        if idx < 0:
            QMessageBox.information(self, t('editor.choose_image'), t('editor.select_row'))
            return
        filename, _ = QFileDialog.getOpenFileName(self, t('editor.choose_image'), '', t('editor.image_filter'))
        if filename: self.table.item(idx,1).setText(filename)

    def _validate_then_accept(self):
        try:
            if self.kind in ('choice','multi'):
                options, correct = [], []
                for i in range(self.table.rowCount()):
                    title = self.table.item(i,0).text().strip()
                    image = self.table.item(i,1).text().strip()
                    if not title and not image: continue
                    options.append({'text':title, 'image':image})
                    if self.table.item(i,2).checkState() == Qt.CheckState.Checked:
                        correct.append(len(options)-1)
                # Do checks before importing files to minimize avoidable side effects.
                from .core import validate_choices
                validate_choices(options, correct, multi=self.kind == 'multi')
                for option in options:
                    if option['image']: option['image'] = media_filename(self.col, option['image'])
                self.aux = choice_fields(options, correct, multi=self.kind == 'multi')
            else:
                answer = self.answer.text().strip()
                tokens = self.tokens.text().split() if self.tokens.text().strip() else None
                alternatives = [x.strip() for x in self.alternatives.toPlainText().splitlines() if x.strip()]
                distractors = [x.strip() for x in self.distractors.toPlainText().splitlines() if x.strip()]
                self.aux = sentence_fields(answer, tokens, alternatives, self.mode.currentData(), distractors)
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, t('editor.invalid_answers'), str(exc))


def _open_editor(editor):
    """Called by editor.addButton; current fields are saved/read by Anki first."""
    try:
        # Current editor introduced in Anki 26; legacy editor has editor.note.
        if hasattr(editor, 'get_note_info'):
            editor.get_note_info(lambda info: _handle_note_info(editor, info))
        else:
            note = editor.note
            if note is None: return
            class Info:
                id = note.id or None
                mid = note.mid
                fields = list(note.fields)
            _handle_note_info(editor, Info())
    except Exception as exc:
        QMessageBox.warning(editor.parentWindow, 'AIC', str(exc))


def _handle_note_info(editor, info):
    try:
        model = mw.col.models.get(info.mid)
        kind = kind_for_model(model)
        if not kind:
            QMessageBox.information(editor.parentWindow, 'AIC', t('editor.select_type'))
            return
        values = fields_from_note_info(model, info.fields)
        # Reopening the dialog before clicking Add should preserve the pending draft.
        if editor.addMode:
            pending = _pending.get(editor)
            if pending and pending.mid == int(info.mid):
                values.update(pending.fields)
        dialog = AnswerEditor(kind, values, mw.col, editor.parentWindow)
        if dialog.exec() != QDialog.DialogCode.Accepted: return
        aux = dialog.aux
        if info.id and not editor.addMode:
            # Existing note: native editor button saves pending rich text first.
            note = mw.col.get_note(info.id)
            merged = merge_aux_fields({key:note[key] for key in values}, aux)
            for key in aux:
                note[key] = merged[key]
            if not note['UID']: note['UID'] = merged['UID']
            mw.col.update_note(note)
            editor.reload_note()
            tooltip(t('editor.saved'))
        elif editor.addMode:
            # The actual note is added by Anki's own Add button, not here.
            _pending[editor] = PendingFields(int(info.mid), aux)
            tooltip(t('editor.prepared'))
            QMessageBox.information(editor.parentWindow, t('editor.prepared_title'), t('editor.prepared_message'))
        else:
            QMessageBox.warning(editor.parentWindow, 'AIC', t('editor.unsaved'))
    except Exception as exc:
        QMessageBox.warning(editor.parentWindow, 'AIC', str(exc))


def register_button(buttons, editor):
    """Make AIC action available in Anki's normal add/edit editor toolbar."""
    _refresh_visibility(editor)
    buttons.append(editor.addButton(icon=None, cmd='aic_edit_answers', func=_open_editor,
        tip=t('editor.answers_tip'), label=t('editor.answers_label'),
        id='aic_answers_button'))
    buttons.append(editor.addButton(icon=None, cmd='aic_toggle_technical', func=_toggle_technical,
        tip=t('editor.technical_tip'), label=t('editor.technical_label'), id='aic_technical_button'))


def on_will_add(problem, note):
    """Apply pending data before Anki persists a new note; native Add stays owner."""
    if problem: return problem
    kind = kind_for_model(note.note_type())
    if not kind: return problem
    matches = [(ed, entry) for ed,entry in list(_pending.items())
               if entry.mid == int(note.mid) and ed.addMode]
    if len(matches) > 1:
        return t('editor.multiple_add')
    if matches:
        _, entry = matches[0]
        merged = merge_aux_fields({key:note[key] for key in note.keys()}, entry.fields)
        for field in entry.fields: note[field] = merged[field]
        if not note['UID']: note['UID'] = merged['UID']
    try:
        validate_note(kind, {key:note[key] for key in note.keys()})
    except Exception as exc:
        return 'AIC: ' + str(exc)
    if matches: matches[0][1].applied = True
    return problem


def on_did_add(note):
    """Don't reuse options on the next note after a successful native Add."""
    for ed, entry in list(_pending.items()):
        if entry.applied and entry.mid == int(note.mid):
            _pending.pop(ed, None)


def register():
    gui_hooks.editor_did_init_buttons.append(register_button)
    gui_hooks.editor_did_init.append(_refresh_visibility)
    gui_hooks.editor_did_load_note.append(_refresh_visibility)
    # The 2026 editor may not send editor_did_load_note on initial Add.
    if hasattr(gui_hooks, 'add_cards_did_init'):
        gui_hooks.add_cards_did_init.append(lambda parent: _refresh_visibility(parent.editor))
    gui_hooks.add_cards_will_add_note.append(on_will_add)
    gui_hooks.add_cards_did_add_note.append(on_did_add)
