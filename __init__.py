"""Anki Interactive Cards - desktop authoring for portable interactive flashcards.

Registers only menu entries; no review hooks or FSRS/scheduler changes.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from aqt import mw, gui_hooks
from aqt.qt import QAction, QMessageBox
from aqt.utils import showInfo
from .src.anki_bridge import ensure_types
from .src.dialogs import InteractiveDialog
from .src.templates import NOTE_TYPES
from .src.native_editor import register as register_native_editor


def open_workshop(edit_note=None):
    try:
        ensure_types(mw.col)
        dialog=InteractiveDialog(mw,edit_note=edit_note)
        dialog.exec()
    except Exception as exc:
        QMessageBox.warning(mw,'Anki Interactive Cards',str(exc))


def update_templates():
    answer=QMessageBox.question(mw,'Kartenvorlagen aktualisieren',
        'Die Vorlagen und das CSS der drei AIC-Notiztypen werden überschrieben, damit die falschen Satzbaukacheln funktionieren. '
        'Eigene Anpassungen an den Vorlagen gehen dabei verloren. Fortfahren?')
    if answer!=QMessageBox.StandardButton.Yes:return
    try:
        # Preserve any custom templates before replacing V1.0 styling.
        backup = {}
        for spec in NOTE_TYPES.values():
            model = mw.col.models.by_name(spec['name'])
            if model:
                backup[spec['name']] = {
                    'css': model['css'],
                    'templates': [{'name': t['name'], 'qfmt': t['qfmt'], 'afmt': t['afmt']}
                                  for t in model['tmpls']],
                }
        path = None
        if backup:
            folder = Path(__file__).parent / 'user_files' / 'template_backups'
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / ('aic_before_v1_2_' + datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f') + '.json')
            path.write_text(json.dumps(backup, ensure_ascii=False, indent=2), encoding='utf-8')
        installed=ensure_types(mw.col,update=True)
        showInfo('Interaktive Kartenvorlagen aktualisiert: '+str(len(installed)) +
                 ('\nSicherung der vorherigen Vorlagen: '+str(path) if path else ''))
    except Exception as exc:QMessageBox.warning(mw,'Fehler',str(exc))


def migrate_existing_types():
    """Non-destructive migration on profile open (only if AIC is installed)."""
    if mw.col and any(mw.col.models.by_name(spec['name']) for spec in NOTE_TYPES.values()):
        try:
            ensure_types(mw.col, update=False)
        except Exception as exc:
            # Avoid interrupting the user's startup. Expose the error for diagnosis.
            print('Anki Interactive Cards: note type migration failed:', exc)


def setup_menu():
    action=QAction('Interactive Cards · Kartenwerkstatt',mw)
    action.triggered.connect(lambda _checked=False: open_workshop())
    mw.form.menuTools.addAction(action)
    action2=QAction('Interactive Cards · Vorlagen aktualisieren',mw)
    action2.triggered.connect(update_templates)
    mw.form.menuTools.addAction(action2)


def browser_menu(browser):
    action=QAction('Interactive Cards · ausgewählte Notiz bearbeiten',browser)
    def edit_selected():
        selected=browser.selected_notes()
        if len(selected)!=1:
            showInfo('Bitte genau eine interaktive Notiz im Browser markieren.')
            return
        note=mw.col.get_note(selected[0])
        if note.note_type()['name'] not in (v['name'] for v in NOTE_TYPES.values()):
            showInfo('Die markierte Notiz ist keine interaktive AIC-Notiz.')
            return
        open_workshop(note)
    action.triggered.connect(edit_selected)
    browser.form.menu_Notes.addAction(action)


setup_menu()
register_native_editor()
gui_hooks.browser_menus_did_init.append(browser_menu)
gui_hooks.profile_did_open.append(migrate_existing_types)
