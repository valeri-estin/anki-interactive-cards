# Changelog

## Unreleased

- Added a reproducible minimal `.ankiaddon` builder, release guide, and a
  preserved `user_files` marker for template backups.

## 1.2.0 – 2026-10-28

- Technische Notizfelder im normalen Anki-Editor standardmäßig ausgeblendet;
  Prompt, Explanation, Prompt Image und Audio bleiben sichtbar.
- `AIC · Technik` blendet alle technischen Felder bei Bedarf wieder ein.
- Native Anki-Feldeigenschaft `collapsed` wird auch bei vorhandenen AIC-Typen
  aktualisiert, ohne die Kartenvorlagen automatisch zu überschreiben.
- Sentence Builder: optionale falsche Wortkacheln im Feld `Distractors`, mit
  Unterstützung im normalen Antworteditor und in der Kartenwerkstatt.
- Alle Wortkacheln werden gemischt; überflüssige müssen nicht verwendet werden.
- Rückwärtskompatibel zu bestehenden Satzbaukarten ohne Distractors-Feld.
- Bestehende Notiztypen erhalten das neue Feld durch eine nicht-destruktive
  Migration beim Profilstart; Vorlagenupdate weiterhin explizit mit Backup.
- Neue Validierungs-, Migrations-, Browser- und Editoransicht-Tests.
- FSRS, Anki-Scheduler und standardmäßige Bewertungsbuttons unverändert.

## 1.1.0 — 2026-10-28

- **Standard-Anki-Editor:** neuer Toolbar-Button **AIC · Antworten** im nativen Add-/Bearbeiten-Fenster. Antwortzeilen mit Checkboxen und Bildauswahl, sowie Wortkacheln/alternative Lösungen für Satzbau; kein manuelles JSON erforderlich.
- **Standard-Anki-Hinzufügen bleibt zuständig:** Bei neuen Notizen werden validierte Antworten über `add_cards_will_add_note` unmittelbar vor dem Speichern eingefügt. Nach Erfolg wird der zwischengespeicherte Dialogzustand verworfen. Ein erneutes Öffnen vor dem Hinzufügen übernimmt die aktuelle Entwurfsfassung.
- **Bearbeiten vorhandener Notizen:** Nur AIC-Antwortfelder werden aktualisiert, Anki-Scheduler/FSRS und übrige Felder bleiben erhalten.
- **Eingeklappte Technikfelder:** `Options`, `Correct`, `Media References`, `Tokens`, `Alternatives`, `Mode`, `UID`, `Source ID` sind bei neu angelegten Notiztypen standardmäßig eingeklappt; Bestandsnotiztypen beim expliziten Vorlagenupdate.
- **Neutrales Kartendesign:** Keine Duolingo-/WoW-Farben oder geschützte Markenoptik. Standard-Light-/Dark-Mode, zurückhaltende Feedbackfarben, einfaches Layout.
- **Theme-API:** konsistente `.aic-*`-Selektoren und `--aic-*`-CSS-Variablen. Duolingo-/WoW-Themes sind eigenständige zukünftige Add-ons.
- **Grid-Korrektur:** Antwortoptionen nutzen nun tatsächlich ein responsives Grid.
- **Vorlagen-Sicherung:** Vor explizitem Vorlagenupdate werden die bisherigen HTML-/CSS-Definitionen unter `user_files/template_backups/` gesichert.
- Rückwärtskompatibel zu den drei Notiztypen und allen bisher erstellten Anki-Notizen; keine Feldumbenennungen.
- 17 Python-Unit-Tests und 5 Browser-Szenarien erfolgreich (keine reale Anki-/Mobil-Integration verfügbar).

## 1.0.0 — 2026-10-28

- Erstes Add-on-Paket mit text- und bildbasiertem Single Choice, Multiple Choice und Sentence Builder.
- Desktop-Kartenwerkstatt, Bild-/Audioimport, Stapelgenerierung aus bestehenden Vokabelnotizen, mobile-fähige HTML/JS-Kartenvorlagen.
- Keine Eingriffe in FSRS oder andere Schedulingwerte.
