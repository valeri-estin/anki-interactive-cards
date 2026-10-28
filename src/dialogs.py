"""Desktop creation, editing, and source-note batch generation dialogs."""
from __future__ import annotations
import html
from pathlib import Path
from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget, QWidget,
    QComboBox, QLineEdit, QTextEdit, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QFileDialog, QCheckBox, QSpinBox, QMessageBox,
    QHeaderView, Qt
)
from aqt.utils import tooltip
from .anki_bridge import (
    ensure_types, media_filename, image_html, new_payload, add_card, source_rows,
    generate_from_rows
)
from .core import from_json_field, tokenize_sentence, choose_distractors, clean_text
from .templates import NOTE_TYPES
from .localization import legacy_format as lf, legacy_text as l


def field_names(col, note_type):
    model = col.models.by_name(note_type)
    return [f['name'] for f in model['flds']] if model else []


def button(label, clicked):
    b = QPushButton(label)
    b.clicked.connect(clicked)
    return b


class InteractiveDialog(QDialog):
    def __init__(self, parent=None, edit_note=None):
        super().__init__(parent or mw)
        self.col = mw.col
        self.edit_note = edit_note
        self.setWindowTitle(l('Anki Interactive Cards · Kartenwerkstatt'))
        self.setMinimumSize(850, 710)
        outer = QVBoxLayout(self)
        self.tabs = QTabWidget()
        outer.addWidget(self.tabs, 1)
        self._make_manual()
        self._make_batch()
        line = QHBoxLayout()
        line.addWidget(QLabel(l('Lokale Kartenvorlagen · keine Cloud · kein Eingriff in FSRS')))
        line.addStretch(1)
        line.addWidget(button(l('Schließen'), self.close))
        outer.addLayout(line)
        if self.edit_note is not None:
            self._load_note()
            self.tabs.setTabEnabled(1, False)

    def _deck_selector(self):
        cb = QComboBox()
        for deck in self.col.decks.all_names_and_ids(include_filtered=False):
            cb.addItem(deck.name,deck.id)
        if cb.count() == 0:
            cb.addItem(l('Default'),1)
        return cb

    def _make_manual(self):
        tab = QWidget(); outer = QVBoxLayout(tab)
        form = QFormLayout()
        self.kind = QComboBox()
        for label, value in [('Einzelauswahl · Text','choice'),('Einzelauswahl · Bilder','image'),
                             ('Mehrfachauswahl · Checkboxen','multi'),('Satzbau','sentence')]:
            self.kind.addItem(l(label),value)
        self.deck = self._deck_selector()
        self.prompt = QLineEdit(); self.prompt.setPlaceholderText(l('z. B. das Haus / Welche Wörter sind Nomen?'))
        self.answer = QLineEdit(); self.answer.setPlaceholderText('z. B. sono a casa')
        self.mode = QComboBox()
        for label,value in [('Wortkacheln und Texteingabe','both'),('Nur Wortkacheln','tiles'),('Nur Texteingabe','typing')]: self.mode.addItem(l(label),value)
        self.tokens = QLineEdit(); self.tokens.setPlaceholderText(l('Leer lassen für automatische Trennung des Zielsatzes'))
        self.alternatives = QTextEdit(); self.alternatives.setMaximumHeight(70)
        self.alternatives.setPlaceholderText('Je eine ebenfalls korrekte Schreibweise pro Zeile')
        self.distractors = QTextEdit(); self.distractors.setMaximumHeight(80)
        self.distractors.setPlaceholderText('Falsche Wortkacheln, je eine pro Zeile (z. B. il, andare)')
        self.explanation = QTextEdit(); self.explanation.setMaximumHeight(65)
        self.image_prompt = QLineEdit(); self.image_prompt.setPlaceholderText('Optional: lokale Bilddatei')
        self.audio = QLineEdit(); self.audio.setPlaceholderText('Optional: [sound:datei.mp3] oder lokale .mp3/.ogg/.wav-Datei')
        form.addRow(l('Kartentyp'),self.kind); form.addRow(l('Ziel-Deck'),self.deck)
        form.addRow(l('Frage / Übersetzung'),self.prompt); form.addRow(l('Zielsatz (Satzbau)'),self.answer)
        form.addRow(l('Satz-Modus'),self.mode); form.addRow(l('Wortbausteine'),self.tokens)
        form.addRow(l('Alternative Lösungen'),self.alternatives); form.addRow(l('Falsche Wortkacheln (optional)'),self.distractors)
        form.addRow(l('Erklärung (optional)'),self.explanation)
        row = QHBoxLayout(); row.addWidget(self.image_prompt,1); row.addWidget(button(l('Bild wählen …'),lambda:self._pick_image(self.image_prompt)))
        form.addRow(l('Fragebild'),row)
        audio_row = QHBoxLayout(); audio_row.addWidget(self.audio,1)
        audio_row.addWidget(button(l('Audio wählen …'),self._pick_audio)); form.addRow(l('Audio'),audio_row)
        outer.addLayout(form)
        self.options_title = QLabel(l('Antwortmöglichkeiten · pro Zeile eine Möglichkeit, Häkchen = korrekt'))
        outer.addWidget(self.options_title)
        self.table = QTableWidget(0,3)
        self.table.setHorizontalHeaderLabels([l('Text / Bildbeschreibung'),l('Bilddatei (optional)'),l('Richtig')])
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeMode.ResizeToContents)
        self.table.setMinimumHeight(170)
        outer.addWidget(self.table,1)
        row = QHBoxLayout()
        row.addWidget(button(l('+ Antwort'),lambda:self._add_option('', '', False)))
        row.addWidget(button(l('– Auswahl entfernen'),self._remove_option)); row.addWidget(button(l('Bild für Auswahl …'),self._pick_table_image))
        row.addWidget(button(l('Vorschläge aus Quellnotizen'),self._suggest))
        row.addStretch(1); outer.addLayout(row)
        outer.addWidget(QLabel(l('Hinweis: Die Reihenfolge wird während des Lernens zufällig gemischt. Einzelauswahl benötigt exakt ein Häkchen.')))
        row = QHBoxLayout(); row.addStretch(1)
        row.addWidget(button(l('Änderungen speichern') if self.edit_note else l('Karte erstellen'),self._save))
        outer.addLayout(row)
        self.kind.currentIndexChanged.connect(self._refresh_mode)
        for i in range(4):self._add_option('', '', i == 0)
        self._refresh_mode()
        self.tabs.addTab(tab,l('Karte erstellen / bearbeiten'))

    def _add_option(self, label='', image='', correct=False):
        row = self.table.rowCount(); self.table.insertRow(row)
        self.table.setItem(row,0,QTableWidgetItem(label))
        self.table.setItem(row,1,QTableWidgetItem(image))
        check = QTableWidgetItem('')
        check.setFlags(check.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        check.setCheckState(Qt.CheckState.Checked if correct else Qt.CheckState.Unchecked)
        self.table.setItem(row,2,check)

    def _remove_option(self):
        r = self.table.currentRow()
        if r>=0: self.table.removeRow(r)

    def _pick_image(self,target):
        filename,_ = QFileDialog.getOpenFileName(self,l('Bild auswählen'),'', l('Bilder (*.png *.jpg *.jpeg *.gif *.webp *.svg)'))
        if filename: target.setText(filename)

    def _pick_audio(self):
        filename,_ = QFileDialog.getOpenFileName(self,l('Audio auswählen'),'', l('Audio (*.mp3 *.ogg *.wav *.m4a *.flac)'))
        if filename:self.audio.setText(filename)

    def _audio_value(self):
        text=self.audio.text().strip()
        if not text:return ''
        path=Path(text).expanduser()
        if path.is_file():
            if path.suffix.lower() not in ('.mp3','.ogg','.wav','.m4a','.flac'):
                raise ValueError(l('Nicht unterstütztes Audioformat.'))
            return '[sound:%s]' % self.col.media.add_file(str(path))
        return text

    def _pick_table_image(self):
        r = self.table.currentRow()
        if r<0:
            QMessageBox.information(self,l('Bildauswahl'),l('Bitte zuerst eine Antwortzeile markieren.'))
            return
        filename,_ = QFileDialog.getOpenFileName(self,l('Antwortbild auswählen'),'', l('Bilder (*.png *.jpg *.jpeg *.gif *.webp *.svg)'))
        if filename: self.table.item(r,1).setText(filename)

    def _refresh_mode(self):
        is_sentence = self.kind.currentData() == 'sentence'
        is_image = self.kind.currentData() == 'image'
        self.answer.setEnabled(is_sentence); self.mode.setEnabled(is_sentence)
        self.tokens.setEnabled(is_sentence); self.alternatives.setEnabled(is_sentence); self.distractors.setEnabled(is_sentence)
        self.table.setEnabled(not is_sentence)
        self.table.setColumnHidden(1,not is_image)
        self.options_title.setText(l('Antwortmöglichkeiten – mehrere Häkchen erlaubt') if self.kind.currentData()=='multi'
                                   else l('Bildoptionen – pro Antwort ein Bild') if is_image else l('Antwortmöglichkeiten – genau ein Häkchen'))

    def _options(self):
        opts=[]; correct=[]
        for i in range(self.table.rowCount()):
            label = self.table.item(i,0).text().strip() if self.table.item(i,0) else ''
            img = self.table.item(i,1).text().strip() if self.table.item(i,1) else ''
            if not label and not img:
                continue
            is_correct = self.table.item(i,2).checkState()==Qt.CheckState.Checked
            opts.append({'text':label,'image':media_filename(self.col,img) if img else ''})
            if is_correct: correct.append(len(opts)-1)
        if self.kind.currentData() == 'image' and any(not o['image'] for o in opts):
            raise ValueError(l('Für jede Bildantwort muss eine Bilddatei hinterlegt sein.'))
        return opts,correct

    def _save(self):
        try:
            kind = self.kind.currentData()
            note_kind = 'choice' if kind=='image' else kind
            image_name = media_filename(self.col,self.image_prompt.text()) if self.image_prompt.text().strip() else ''
            common = dict(explanation=self.explanation.toPlainText(),
                          prompt_image=image_html(image_name),audio=self._audio_value())
            if note_kind=='sentence':
                answer = self.answer.text().strip()
                tokens = self.tokens.text().split() if self.tokens.text().strip() else tokenize_sentence(answer)
                alternatives = [x.strip() for x in self.alternatives.toPlainText().splitlines() if x.strip()]
                distractors = [x.strip() for x in self.distractors.toPlainText().splitlines() if x.strip()]
                payload = new_payload('sentence',self.prompt.text(),answer=answer,tokens=tokens,
                                       alternatives=alternatives,distractors=distractors,
                                       mode=self.mode.currentData(),**common)
            else:
                opts,corr=self._options()
                payload = new_payload(note_kind,self.prompt.text(),options=opts,correct=corr,**common)
            if self.edit_note is not None:
                payload['Source ID']=self.edit_note['Source ID']
                add_card(self.col,note_kind,self.deck.currentData(),payload,self.edit_note)
                tooltip(l('Interaktive Karte aktualisiert.'))
                self.close()
            else:
                add_card(self.col,note_kind,self.deck.currentData(),payload)
                tooltip(l('Interaktive Karte erstellt.'))
                self.prompt.clear(); self.answer.clear(); self.tokens.clear()
                self.alternatives.clear(); self.distractors.clear(); self.explanation.clear(); self.image_prompt.clear(); self.audio.clear()
                self.table.setRowCount(0)
                for i in range(4):self._add_option('', '', i==0)
        except Exception as exc:
            QMessageBox.warning(self,l('Karte nicht gespeichert'),str(exc))

    def _load_note(self):
        note=self.edit_note; name=note.note_type()['name']
        kind = next((k for k,v in NOTE_TYPES.items() if v['name']==name),None)
        if kind is None:raise ValueError(l('Kein unterstützter interaktiver Notiztyp.'))
        opts=from_json_field(note['Options'],[]) if kind!='sentence' else []
        if kind=='choice' and any(x.get('image') for x in opts):
            idx=self.kind.findData('image')
        else:idx=self.kind.findData(kind)
        self.kind.setCurrentIndex(idx);self.kind.setEnabled(False)
        self.prompt.setText(clean_text(note['Prompt']))
        self.explanation.setPlainText(clean_text(note['Explanation']))
        self.audio.setText(note['Audio'])
        from .core import detect_media
        self.image_prompt.setText(detect_media(note['Prompt Image']))
        if kind=='sentence':
            self.answer.setText(clean_text(note['Answer']))
            self.tokens.setText(' '.join(from_json_field(note['Tokens'],[])))
            self.alternatives.setPlainText('\n'.join(from_json_field(note['Alternatives'],[])))
            self.distractors.setPlainText('\n'.join(from_json_field(note['Distractors'],[])))
            self.mode.setCurrentIndex(max(0,self.mode.findData(note['Mode'])))
        else:
            correct=from_json_field(note['Correct'],[])
            self.table.setRowCount(0)
            for i,x in enumerate(opts):self._add_option(x.get('text',''),x.get('image',''),i in correct)

    def _make_batch(self):
        tab=QWidget();outer=QVBoxLayout(tab)
        outer.addWidget(QLabel(l('Erzeuge interaktive Karten aus bestehenden Anki-Vokabelnotizen. Quellnotizen bleiben unverändert.')))
        form=QFormLayout()
        self.source_type=QComboBox()
        for n in self.col.models.all_names_and_ids():
            if not n.name.startswith('AIC ·'):
                self.source_type.addItem(n.name,n.name)
        self.source_deck=self._deck_selector();self.target_deck=self._deck_selector()
        self.front_field=QComboBox();self.back_field=QComboBox()
        self.source_image_field=QComboBox();self.source_audio_field=QComboBox()
        self.batch_type=QComboBox()
        for label,kind in [('Text-Einzelauswahl','choice'),('Bild-Einzelauswahl','image'),
                           ('Satzbau mit Schreiben & Wortkacheln','sentence')]: self.batch_type.addItem(l(label),kind)
        self.num_distractors=QSpinBox();self.num_distractors.setRange(1,10);self.num_distractors.setValue(3)
        self.batch_update=QCheckBox(l('Bereits erzeugte Karten aktualisieren (Lernfortschritt bleibt erhalten)'))
        form.addRow(l('Quell-Notiztyp'),self.source_type); form.addRow(l('Quell-Deck'),self.source_deck)
        form.addRow(l('Frage-Feld'),self.front_field); form.addRow(l('Antwort-Feld'),self.back_field)
        form.addRow(l('Bildfeld (Bild der Antwort)'),self.source_image_field); form.addRow(l('Audiofeld (optional)'),self.source_audio_field)
        form.addRow(l('Ziel-Deck'),self.target_deck); form.addRow(l('Erzeugter Kartentyp'),self.batch_type)
        form.addRow(l('Falsche Antwortoptionen'),self.num_distractors)
        form.addRow('',self.batch_update)
        outer.addLayout(form)
        self.source_type.currentIndexChanged.connect(self._source_type_change)
        self._source_type_change()
        self.preview=QTextEdit(); self.preview.setReadOnly(True)
        self.preview.setPlaceholderText(l('Vorschau der Quellnotizen …'))
        outer.addWidget(self.preview,1)
        row=QHBoxLayout()
        row.addWidget(button(l('Quelle prüfen'),self._preview_source))
        row.addStretch(1)
        row.addWidget(button(l('Karten erzeugen'),self._generate))
        outer.addLayout(row)
        outer.addWidget(QLabel(l('Hinweis: Bildzuordnung benötigt je Quellnotiz ein Bild zur Antwort.\nTexte werden als Momentaufnahme übernommen. Zur Aktualisierung erneut importieren.')))
        self.tabs.addTab(tab,l('Aus bestehenden Vokabeln erzeugen'))

    def _source_type_change(self):
        fields=field_names(self.col,self.source_type.currentData())
        for combo in (self.front_field,self.back_field,self.source_image_field,self.source_audio_field):
            combo.clear()
            if combo in (self.source_image_field,self.source_audio_field):combo.addItem('— keines —','')
            for f in fields:combo.addItem(f,f)
        if len(fields)>1:self.back_field.setCurrentIndex(1)
        if self.source_image_field.count()>0:
            for i in range(self.source_image_field.count()):
                if 'bild' in self.source_image_field.itemText(i).lower() or 'image' in self.source_image_field.itemText(i).lower():
                    self.source_image_field.setCurrentIndex(i);break

    def _rows(self):
        return source_rows(self.col,self.source_type.currentData(),self.source_deck.currentText(),
                           self.front_field.currentData(),self.back_field.currentData(),
                           self.source_image_field.currentData(),self.source_audio_field.currentData())

    def _preview_source(self):
        try:
            rows=self._rows()
            lines=[lf('{count} gültige Quellnotizen (höchstens 5000 pro Durchlauf)', count=len(rows)), '']
            for row in rows[:20]:
                lines.append(f"• {row['prompt']}  →  {row['answer']}" + ('  [Bild]' if row['image'] else ''))
            if len(rows)>20:lines.append('…')
            self.preview.setPlainText('\n'.join(lines))
        except Exception as exc:QMessageBox.warning(self,'Quellnotizen',str(exc))

    def _suggest(self):
        try:
            rows=self._rows()
            if not rows:raise ValueError(l('Keine passenden Notizen gefunden. Bitte Quelltyp und Felder prüfen.'))
            # First correct checked item, if present; otherwise use first filled item.
            correct = next((self.table.item(i,0).text().strip() for i in range(self.table.rowCount())
                             if self.table.item(i,2).checkState()==Qt.CheckState.Checked and self.table.item(i,0).text().strip()),'')
            if not correct:
                raise ValueError('Zuerst die richtige Antwort in der Tabelle eintragen und anhaken.')
            proposed=choose_distractors(correct,[r['answer'] for r in rows],3)
            for word in proposed:self._add_option(word,'',False)
            tooltip(lf('{count} Antwortvorschläge ergänzt. Bitte fachlich prüfen.', count=len(proposed)))
        except Exception as exc:QMessageBox.warning(self,l('Vorschläge'),str(exc))

    def _generate(self):
        try:
            rows=self._rows()
            if not rows:raise ValueError(l('Keine gültigen Quellnotizen vorhanden.'))
            result = QMessageBox.question(self,'Batch creation', lf(
                '{count} Quellnotizen prüfen und interaktive Karten im Deck "{deck}" erzeugen?\nDies erstellt zusätzliche Karten; bestehende Quellnotizen bleiben bestehen.',
                count=len(rows), deck=self.target_deck.currentText()))
            if result != QMessageBox.StandardButton.Yes:return
            ensure_types(self.col)
            summary=generate_from_rows(self.col,rows,self.batch_type.currentData(),
                self.target_deck.currentText(),self.num_distractors.value(),self.batch_update.isChecked())
            QMessageBox.information(self,'Batch complete', lf(
                'Erstellt: {created}\nAktualisiert: {updated}\nÜbersprungen: {skipped}', **summary))
        except Exception as exc:QMessageBox.warning(self,'Stapel fehlgeschlagen',str(exc))
