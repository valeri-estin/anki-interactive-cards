"""Centralized user-facing copy and language selection for AIC."""

from __future__ import annotations

import json
from typing import Any

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "de")

COPY = {
    "en": {
        "card.solution_label": "Solution", "card.answers_label": "Answer choices",
        "card.choice_tag": "CHOOSE ONE ANSWER", "card.multi_tag": "CHOOSE ALL CORRECT ANSWERS", "card.sentence_tag": "PUT THE SENTENCE IN THE RIGHT ORDER",
        "card.caption": "Then rate your recall with Anki's regular buttons (FSRS remains unchanged).", "card.image_option": "Image option {number}", "card.missing_tokens": "Sentence tokens are missing.", "card.remove_word": "Remove word", "card.tiles": "Word tiles", "card.typing": "Typing", "card.your_answer": "Your answer: ",
        "card.invalid": "Invalid card data. Check the note in the editor.", "card.correct": "Correct!", "card.incorrect": "Not quite. Correct: ", "card.check_choices": "Check selection", "card.sentence_placeholder": "Write the complete sentence …", "card.sentence_input": "Enter sentence", "card.distractor_hint": "Not every word has to be used.", "card.solution": "Not quite. Solution: ", "card.check_sentence": "Check sentence", "card.reset": "Reset",
        "menu.workshop": "Interactive Cards · Card Workshop", "menu.templates": "Interactive Cards · Update templates", "menu.edit_selected": "Interactive Cards · Edit selected note", "menu.select_one": "Select exactly one interactive note in the Browser.", "menu.not_aic": "The selected note is not an interactive AIC note.",
        "templates.title": "Update card templates", "templates.confirm": "The templates and CSS of all three AIC note types will be overwritten. Custom template changes will be lost. Continue?", "templates.updated": "Updated interactive card templates: {count}", "templates.backup": "\nBackup of previous templates: {path}", "common.error": "Error",
    },
    "de": {
        "card.solution_label": "Lösung", "card.answers_label": "Antwortmöglichkeiten",
        "card.choice_tag": "WÄHLE EINE ANTWORT", "card.multi_tag": "WÄHLE ALLE RICHTIGEN ANTWORTEN", "card.sentence_tag": "BRINGE DEN SATZ IN DIE RICHTIGE REIHENFOLGE",
        "card.caption": "Bewerte deine Erinnerung anschließend mit den regulären Anki-Buttons (FSRS bleibt unverändert).", "card.image_option": "Bildoption {number}", "card.missing_tokens": "Wortbausteine fehlen.", "card.remove_word": "Wort wieder entfernen", "card.tiles": "Wortkacheln", "card.typing": "Schreiben", "card.your_answer": "Deine Antwort: ",
        "card.invalid": "Ungültige Kartendaten. Bitte Notiz im Editor prüfen.", "card.correct": "Richtig!", "card.incorrect": "Nicht ganz. Richtig: ", "card.check_choices": "Auswahl prüfen", "card.sentence_placeholder": "Schreibe den vollständigen Satz …", "card.sentence_input": "Satz eingeben", "card.distractor_hint": "Nicht alle Wörter müssen verwendet werden.", "card.solution": "Nicht ganz. Lösung: ", "card.check_sentence": "Satz prüfen", "card.reset": "Zurücksetzen",
        "menu.workshop": "Interactive Cards · Kartenwerkstatt", "menu.templates": "Interactive Cards · Vorlagen aktualisieren", "menu.edit_selected": "Interactive Cards · ausgewählte Notiz bearbeiten", "menu.select_one": "Bitte genau eine interaktive Notiz im Browser markieren.", "menu.not_aic": "Die markierte Notiz ist keine interaktive AIC-Notiz.",
        "templates.title": "Kartenvorlagen aktualisieren", "templates.confirm": "Die Vorlagen und das CSS der drei AIC-Notiztypen werden überschrieben. Eigene Anpassungen an den Vorlagen gehen dabei verloren. Fortfahren?", "templates.updated": "Interaktive Kartenvorlagen aktualisiert: {count}", "templates.backup": "\nSicherung der vorherigen Vorlagen: {path}", "common.error": "Fehler",
    },
}


def language_from_config(config: object) -> str:
    value = config.get("ui_language") if isinstance(config, dict) else None
    return value if value in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def text(key: str, language: str = DEFAULT_LANGUAGE, **values: Any) -> str:
    return COPY.get(language, COPY[DEFAULT_LANGUAGE]).get(key, COPY[DEFAULT_LANGUAGE][key]).format(**values)


def card_copy(language: str) -> str:
    """Serialize only card-rendering strings for the offline card template."""
    return json.dumps(COPY.get(language, COPY[DEFAULT_LANGUAGE]), ensure_ascii=False)
