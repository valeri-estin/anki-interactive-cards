"""Centralized user-facing copy and language selection for AIC."""

from __future__ import annotations

import json
from typing import Any

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "de")
_active_language = DEFAULT_LANGUAGE

COPY = {
    "en": {
        "card.solution_label": "Solution", "card.answers_label": "Answer choices",
        "card.choice_tag": "CHOOSE ONE ANSWER", "card.multi_tag": "CHOOSE ALL CORRECT ANSWERS", "card.sentence_tag": "PUT THE SENTENCE IN THE RIGHT ORDER",
        "card.caption": "Then rate your recall with Anki's regular buttons (FSRS remains unchanged).", "card.image_option": "Image option {number}", "card.missing_tokens": "Sentence tokens are missing.", "card.remove_word": "Remove word", "card.tiles": "Word tiles", "card.typing": "Typing", "card.your_answer": "Your answer: ",
        "card.invalid": "Invalid card data. Check the note in the editor.", "card.correct": "Correct!", "card.incorrect": "Not quite. Correct: ", "card.check_choices": "Check selection", "card.sentence_placeholder": "Write the complete sentence …", "card.sentence_input": "Enter sentence", "card.distractor_hint": "Not every word has to be used.", "card.solution": "Not quite. Solution: ", "card.check_sentence": "Check sentence", "card.reset": "Reset",
        "menu.workshop": "Interactive Cards · Card Workshop", "menu.templates": "Interactive Cards · Update templates", "menu.edit_selected": "Interactive Cards · Edit selected note", "menu.select_one": "Select exactly one interactive note in the Browser.", "menu.not_aic": "The selected note is not an interactive AIC note.",
        "templates.title": "Update card templates", "templates.confirm": "The templates and CSS of all three AIC note types will be overwritten. Custom template changes will be lost. Continue?", "templates.updated": "Updated interactive card templates: {count}", "templates.backup": "\nBackup of previous templates: {path}", "common.error": "Error",
        "editor.technical_shown": "AIC: technical fields shown", "editor.technical_hidden": "AIC: technical fields hidden", "editor.title": "AIC · Edit answers", "editor.intro": "You can continue to edit the prompt, explanation, tags, deck, and media in Anki's editor.", "editor.choice_intro": "Answers: checkbox = correct. Choose an image for every image-choice option.", "editor.answer_text": "Answer text", "editor.image_file": "Image file (optional)", "editor.correct": "Correct", "editor.add_answer": "+ Answer", "editor.remove_answer": "Remove answer", "editor.choose_image": "Choose image …", "editor.single_choice": "Single Choice: exactly one correct answer. Use the AIC · Multiple Choice note type for multiple answers.", "editor.auto_tokens": "Leave empty to split the target sentence into words automatically", "editor.alternatives": "Other valid sentences, one per line", "editor.distractors": "Optional wrong word tiles, one per line.\ne.g. il\nandare", "editor.mode_both": "Word tiles and typing", "editor.mode_tiles": "Word tiles only", "editor.mode_typing": "Typing only", "editor.target": "Correct target sentence", "editor.tokens": "Word tokens", "editor.other_solutions": "Other solutions", "editor.wrong_tiles": "Wrong word tiles", "editor.input_mode": "Input mode", "editor.apply": "Apply", "editor.select_row": "Select an answer row first.", "editor.image_filter": "Images (*.png *.jpg *.jpeg *.webp *.gif *.svg)", "editor.invalid_answers": "Invalid answers", "editor.select_type": "Select an AIC · … note type first.", "editor.saved": "AIC answers saved in the existing note.", "editor.prepared": "AIC answers prepared. Now click Anki's Add button.", "editor.prepared_title": "AIC · Answers applied", "editor.prepared_message": "The answer choices are ready. Enter the prompt in the Prompt field if needed, then click Anki's regular Add button.\n\nThe JSON fields are filled automatically when adding.\nAfter adding, open AIC · Edit answers again for another card.", "editor.unsaved": "This unsaved note can only be edited in Add mode.", "editor.answers_tip": "Edit answers / sentence builder without JSON", "editor.answers_label": "AIC · Answers", "editor.technical_tip": "For AIC only: show or hide technical Anki note fields", "editor.technical_label": "AIC · Technical", "editor.multiple_add": "More than one AIC editor is open. Use only one Add dialog.",
    },
    "de": {
        "card.solution_label": "Lösung", "card.answers_label": "Antwortmöglichkeiten",
        "card.choice_tag": "WÄHLE EINE ANTWORT", "card.multi_tag": "WÄHLE ALLE RICHTIGEN ANTWORTEN", "card.sentence_tag": "BRINGE DEN SATZ IN DIE RICHTIGE REIHENFOLGE",
        "card.caption": "Bewerte deine Erinnerung anschließend mit den regulären Anki-Buttons (FSRS bleibt unverändert).", "card.image_option": "Bildoption {number}", "card.missing_tokens": "Wortbausteine fehlen.", "card.remove_word": "Wort wieder entfernen", "card.tiles": "Wortkacheln", "card.typing": "Schreiben", "card.your_answer": "Deine Antwort: ",
        "card.invalid": "Ungültige Kartendaten. Bitte Notiz im Editor prüfen.", "card.correct": "Richtig!", "card.incorrect": "Nicht ganz. Richtig: ", "card.check_choices": "Auswahl prüfen", "card.sentence_placeholder": "Schreibe den vollständigen Satz …", "card.sentence_input": "Satz eingeben", "card.distractor_hint": "Nicht alle Wörter müssen verwendet werden.", "card.solution": "Nicht ganz. Lösung: ", "card.check_sentence": "Satz prüfen", "card.reset": "Zurücksetzen",
        "menu.workshop": "Interactive Cards · Kartenwerkstatt", "menu.templates": "Interactive Cards · Vorlagen aktualisieren", "menu.edit_selected": "Interactive Cards · ausgewählte Notiz bearbeiten", "menu.select_one": "Bitte genau eine interaktive Notiz im Browser markieren.", "menu.not_aic": "Die markierte Notiz ist keine interaktive AIC-Notiz.",
        "templates.title": "Kartenvorlagen aktualisieren", "templates.confirm": "Die Vorlagen und das CSS der drei AIC-Notiztypen werden überschrieben. Eigene Anpassungen an den Vorlagen gehen dabei verloren. Fortfahren?", "templates.updated": "Interaktive Kartenvorlagen aktualisiert: {count}", "templates.backup": "\nSicherung der vorherigen Vorlagen: {path}", "common.error": "Fehler",
        "editor.technical_shown": "AIC: Technikfelder eingeblendet", "editor.technical_hidden": "AIC: Technikfelder ausgeblendet", "editor.title": "AIC · Antworten bearbeiten", "editor.intro": "Frage, Erklärung, Tags, Deck und Medien kannst du weiterhin im Anki-Editor bearbeiten.", "editor.choice_intro": "Antworten: Häkchen = richtig. Bei Bildauswahl für jede Option ein Bild wählen.", "editor.answer_text": "Antworttext", "editor.image_file": "Bilddatei (optional)", "editor.correct": "Richtig", "editor.add_answer": "+ Antwort", "editor.remove_answer": "Antwort entfernen", "editor.choose_image": "Bild auswählen …", "editor.single_choice": "Einzelauswahl: genau eine richtige Antwort. Für Mehrfachantworten den Notiztyp „AIC · Multiple Choice“ verwenden.", "editor.auto_tokens": "Leer lassen = Zielsatz automatisch in Wörter aufteilen", "editor.alternatives": "Weitere gültige Sätze, je eine Zeile", "editor.distractors": "Optionale falsche Wortkacheln, je eine pro Zeile.\nz. B. il\nandare", "editor.mode_both": "Wortkacheln und Schreiben", "editor.mode_tiles": "Nur Wortkacheln", "editor.mode_typing": "Nur Schreiben", "editor.target": "Richtiger Zielsatz", "editor.tokens": "Wortbausteine", "editor.other_solutions": "Weitere Lösungen", "editor.wrong_tiles": "Falsche Wortkacheln", "editor.input_mode": "Eingabemodus", "editor.apply": "Übernehmen", "editor.select_row": "Bitte zuerst eine Antwortzeile anklicken.", "editor.image_filter": "Bilder (*.png *.jpg *.jpeg *.webp *.gif *.svg)", "editor.invalid_answers": "Ungültige Antworten", "editor.select_type": "Bitte zuerst einen Notiztyp „AIC · …“ wählen.", "editor.saved": "AIC-Antworten in bestehender Notiz gespeichert.", "editor.prepared": "AIC-Antworten vorbereitet. Jetzt auf Ankis „Hinzufügen“ klicken.", "editor.prepared_title": "AIC · Antworten übernommen", "editor.prepared_message": "Die Antwortmöglichkeiten sind vorbereitet. Trage bei Bedarf die Frage im Feld „Prompt“ ein und klicke anschließend auf den normalen Anki-Button „Hinzufügen“.\n\nDie JSON-Felder werden beim Hinzufügen automatisch gefüllt.\nNach dem Hinzufügen für eine weitere Karte erneut „AIC · Antworten bearbeiten“ öffnen.", "editor.unsaved": "Diese ungespeicherte Notiz kann nur im Hinzufügen-Modus bearbeitet werden.", "editor.answers_tip": "Antworten / Satzbau ohne JSON bearbeiten", "editor.answers_label": "AIC · Antworten", "editor.technical_tip": "Nur bei AIC: technische Anki-Notizfelder ein- oder ausblenden", "editor.technical_label": "AIC · Technik", "editor.multiple_add": "Mehrere AIC-Editoren sind offen. Bitte nur einen Hinzufügen-Dialog verwenden.",
    },
}

# Transitional source-key map for the large authoring dialog. Keeping the
# translations here still gives reviewers one authoritative UI-copy catalog.
LEGACY_EN = {
    "Anki Interactive Cards · Kartenwerkstatt": "Anki Interactive Cards · Card Workshop",
    "Lokale Kartenvorlagen · keine Cloud · kein Eingriff in FSRS": "Local card templates · no cloud · no FSRS changes",
    "Schließen": "Close", "Default": "Default", "Einzelauswahl · Text": "Single Choice · text",
    "Einzelauswahl · Bilder": "Single Choice · images", "Mehrfachauswahl · Checkboxen": "Multiple Choice · checkboxes",
    "Satzbau": "Sentence Builder", "Kartentyp": "Card type", "Ziel-Deck": "Target deck",
    "Frage / Übersetzung": "Prompt / translation", "Zielsatz (Satzbau)": "Target sentence (Sentence Builder)",
    "Satz-Modus": "Sentence mode", "Wortbausteine": "Word tokens", "Alternative Lösungen": "Alternative solutions",
    "Falsche Wortkacheln (optional)": "Wrong word tiles (optional)", "Erklärung (optional)": "Explanation (optional)",
    "Fragebild": "Prompt image", "Audio": "Audio", "Bild wählen …": "Choose image …", "Audio wählen …": "Choose audio …",
    "Antwortmöglichkeiten · pro Zeile eine Möglichkeit, Häkchen = korrekt": "Answer choices · one option per row, checkbox = correct",
    "Text / Bildbeschreibung": "Text / image description", "Bilddatei (optional)": "Image file (optional)", "Richtig": "Correct",
    "+ Antwort": "+ Answer", "– Auswahl entfernen": "– Remove option", "Bild für Auswahl …": "Image for option …",
    "Vorschläge aus Quellnotizen": "Suggestions from source notes", "Änderungen speichern": "Save changes", "Karte erstellen": "Create card",
    "Karte erstellen / bearbeiten": "Create / edit card", "Aus bestehenden Vokabeln erzeugen": "Generate from existing vocabulary",
    "Wortkacheln und Texteingabe": "Word tiles and typing", "Nur Wortkacheln": "Word tiles only", "Nur Texteingabe": "Typing only",
    "Antwortmöglichkeiten – mehrere Häkchen erlaubt": "Answer choices – multiple selections allowed", "Bildoptionen – pro Antwort ein Bild": "Image options – one image per answer", "Antwortmöglichkeiten – genau ein Häkchen": "Answer choices – exactly one selection",
    "Interaktive Karte aktualisiert.": "Interactive card updated.", "Interaktive Karte erstellt.": "Interactive card created.",
    "Karte nicht gespeichert": "Card not saved", "Kein unterstützter interaktiver Notiztyp.": "No supported interactive note type.",
    "Text-Einzelauswahl": "Text Single Choice", "Bild-Einzelauswahl": "Image Single Choice", "Satzbau mit Schreiben & Wortkacheln": "Sentence Builder with typing and word tiles",
    "Bereits erzeugte Karten aktualisieren (Lernfortschritt bleibt erhalten)": "Update already generated cards (keep learning progress)",
    "Quell-Notiztyp": "Source note type", "Quell-Deck": "Source deck", "Frage-Feld": "Prompt field", "Antwort-Feld": "Answer field", "Bildfeld (Bild der Antwort)": "Image field (answer image)", "Audiofeld (optional)": "Audio field (optional)", "Erzeugter Kartentyp": "Generated card type", "Falsche Antwortoptionen": "Wrong answer options", "Vorschau der Quellnotizen …": "Source-note preview …", "Quelle prüfen": "Check source", "Karten erzeugen": "Generate cards",
    "Bilder (*.png *.jpg *.jpeg *.gif *.webp *.svg)": "Images (*.png *.jpg *.jpeg *.gif *.webp *.svg)", "Audio (*.mp3 *.ogg *.wav *.m4a *.flac)": "Audio (*.mp3 *.ogg *.wav *.m4a *.flac)",
    "Nicht unterstütztes Audioformat.": "Unsupported audio format.", "Bildauswahl": "Image selection", "Bitte zuerst eine Antwortzeile markieren.": "Select an answer row first.", "Antwortbild auswählen": "Choose answer image",
    "Für jede Bildantwort muss eine Bilddatei hinterlegt sein.": "Every image answer needs an image file.",
    "Hinweis: Die Reihenfolge wird während des Lernens zufällig gemischt. Einzelauswahl benötigt exakt ein Häkchen.": "Note: choices are shuffled during review. Single Choice needs exactly one selection.", "Erzeuge interaktive Karten aus bestehenden Anki-Vokabelnotizen. Quellnotizen bleiben unverändert.": "Generate interactive cards from existing Anki vocabulary notes. Source notes remain unchanged.", "Hinweis: Bildzuordnung benötigt je Quellnotiz ein Bild zur Antwort.\nTexte werden als Momentaufnahme übernommen. Zur Aktualisierung erneut importieren.": "Note: image choice needs one answer image per source note.\nText is copied as a snapshot; import again to update it.", "Keine passenden Notizen gefunden. Bitte Quelltyp und Felder prüfen.": "No matching notes found. Check the source note type and fields.", "Vorschläge": "Suggestions", "Keine gültigen Quellnotizen vorhanden.": "No valid source notes are available.",
    "z. B. das Haus / Welche Wörter sind Nomen?": "e.g. das Haus / Which words are nouns?", "Leer lassen für automatische Trennung des Zielsatzes": "Leave empty to split the target sentence automatically", "{count} gültige Quellnotizen (höchstens 5000 pro Durchlauf)": "{count} valid source notes (maximum 5,000 per run)", "{count} Antwortvorschläge ergänzt. Bitte fachlich prüfen.": "Added {count} answer suggestions. Review them for correctness.", "{count} Quellnotizen prüfen und interaktive Karten im Deck \"{deck}\" erzeugen?\nDies erstellt zusätzliche Karten; bestehende Quellnotizen bleiben bestehen.": "Review {count} source notes and create interactive cards in deck \"{deck}\"?\nThis adds cards; existing source notes remain unchanged.", "Erstellt: {created}\nAktualisiert: {updated}\nÜbersprungen: {skipped}": "Created: {created}\nUpdated: {updated}\nSkipped: {skipped}", "Notiztyp {name} hat fehlende Felder: {fields}. Bitte manuell prüfen.": "Note type {name} is missing fields: {fields}. Check it manually.",
    "Erforderlich sind 2 bis 24 Antwortmöglichkeiten.": "2 to 24 answer choices are required.", "Antwortoptionen benötigen unterschiedliche Bezeichnungen.": "Answer choices need distinct labels.", "Jede Antwort benötigt Text oder ein Bild.": "Every answer needs text or an image.", "Mindestens eine korrekte Auswahl muss gesetzt sein.": "Select at least one correct answer.", "Korrekte Indizes müssen eindeutig sein.": "Correct indexes must be unique.", "Single Choice benötigt genau eine richtige Antwort.": "Single Choice needs exactly one correct answer.", "Der Zielsatz darf nicht leer sein.": "The target sentence cannot be empty.", "Der Satz benötigt mindestens einen Wortbaustein.": "The sentence needs at least one word token.", "Die Wortbausteine müssen zusammen den Zielsatz ergeben.": "The word tokens must form the target sentence.", "Falsche Wortkacheln müssen eine Liste von Texten sein.": "Wrong word tiles must be a list of text values.", "Leere falsche Wortkacheln sind nicht erlaubt.": "Wrong word tiles cannot be empty.", "Maximal 60 Wortkacheln insgesamt (richtige und falsche).": "At most 60 word tiles are allowed in total.", "Falsche Wortkacheln dürfen nicht doppelt vorkommen.": "Wrong word tiles cannot be duplicated.", "Eine falsche Wortkachel darf nicht identisch mit einer richtigen sein.": "A wrong word tile cannot equal a required tile.", "Ungültiger Satzmodus.": "Invalid sentence mode.",
    "Nicht unterstütztes Bildformat: ": "Unsupported image format: ", "Nicht unterstützter Importmodus.": "Unsupported import mode.", "Bildauswahl benötigt mindestens zwei Quellnotizen mit Bildern.": "Image choice needs at least two source notes with images.", "Feldanzahl der Anki-Notiz hat sich geändert. Bitte erneut öffnen.": "The Anki note field count changed. Open it again.", "Bitte „AIC · Antworten bearbeiten“ öffnen und Antworten festlegen.": "Open AIC · Edit answers and define the answers.", "Bitte Satzbausteine über „AIC · Antworten bearbeiten“ konfigurieren.": "Configure sentence tokens in AIC · Edit answers.", "Falsche Wortkacheln müssen eine Liste sein.": "Wrong word tiles must be a list.", "Bitte einen gültigen Satzmodus wählen.": "Choose a valid sentence mode.",
}


def language_from_config(config: object) -> str:
    value = config.get("ui_language") if isinstance(config, dict) else None
    return value if value in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def set_language(config: object) -> str:
    """Set the process-local UI language after Anki loads add-on configuration."""
    global _active_language
    _active_language = language_from_config(config)
    return _active_language


def active_language() -> str:
    return _active_language


def text(key: str, language: str = DEFAULT_LANGUAGE, **values: Any) -> str:
    return COPY.get(language, COPY[DEFAULT_LANGUAGE]).get(key, COPY[DEFAULT_LANGUAGE][key]).format(**values)


def ui_text(key: str, **values: Any) -> str:
    return text(key, _active_language, **values)


def legacy_text(source: str) -> str:
    return LEGACY_EN.get(source, source) if _active_language == "en" else source


def legacy_format(source: str, **values: Any) -> str:
    return legacy_text(source).format(**values)


def card_copy(language: str) -> str:
    """Serialize only card-rendering strings for the offline card template."""
    return json.dumps(COPY.get(language, COPY[DEFAULT_LANGUAGE]), ensure_ascii=False)
