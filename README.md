# Anki Interactive Cards

**Version:** 1.2.0
**Plattform:** Anki Desktop (Python-Add-on, Qt6) zum Erstellen; HTML/JavaScript-Karten zum Lernen  
**Sprache der Oberfläche:** Deutsch  
**Lizenz:** AGPL-3.0-or-later

Ein Add-on für interaktive Anki-Karten. Die Lernkarten verwenden **Ankis normalen Scheduler einschließlich FSRS**. Es werden keine Bewertungen automatisiert, kein Lernfortschritt umgeschrieben und keine Netzwerkdienste aufgerufen.

## Änderungen in Version 1.2.0

### Aufgeräumter normaler Anki-Editor

Wenn du in **Hinzufügen** oder **Bearbeiten** einen AIC-Notiztyp wählst, sind nur
**Prompt, Explanation, Prompt Image und Audio** sichtbar. Die Datenfelder
(Options, Correct, Media References, Answer, Tokens, Alternatives, Mode,
Distractors, UID und Source ID) bleiben **erhalten und gespeichert**, werden
aber in der regulären Eingabemaske ausgeblendet. Die Antwortdaten werden über
**AIC · Antworten** konfiguriert. Über **AIC · Technik** kannst du die
versteckten Felder temporär einblenden und wieder ausblenden.

Dies ist eine *Darstellungsfunktion*, keine Datenmigration: Die Notizfelder
werden nicht gelöscht. Zusätzlich werden sie in Ankis Felddefinition als
**Collapse by default** markiert. Sollte eine zukünftige Anki-Version die
Editor-DOM-Struktur ändern, bleiben die Felder ggf. zunächst nur eingeklappt;
die Kartenfunktion ist davon unabhängig.

### Satzbau mit falschen Wortkacheln (fünfte Übungsvariante)

1. Notiztyp **AIC · Sentence Builder** auswählen.
2. In **Prompt** die deutsche Satzvorgabe eingeben: `Ich bin zu Hause.`
3. **AIC · Antworten** öffnen.
4. Als Zielsatz `sono a casa` eintragen, Wortbausteine leer lassen.
5. In **Falsche Wortkacheln** untereinander `il` und `andare` eintragen.
6. **Wortkacheln und Schreiben** oder **Nur Wortkacheln** wählen, **Übernehmen**, danach normal **Hinzufügen**.

Die Karte mischt `sono`, `a`, `casa`, `il`, `andare`. Die Lernenden müssen die
richtigen Wörter auswählen und in die korrekte Reihenfolge bringen. Nicht alle
Kacheln müssen benutzt werden. Im optionalen Schreiben-Modus erscheinen keine
Wortkacheln. **Eine falsche Kachel darf nicht den gleichen Text wie eine
benötigte richtige Kachel haben**, da sie sonst nicht unterscheidbar wäre.
Bei bestehenden Satzbaukarten sind keine falschen Kacheln hinterlegt; sie
funktionieren weiterhin wie bisher.

### Update von 1.1.0

1. Vor der Installation ein Anki-Backup anlegen.
2. `anki-interactive-cards-1.2.0.ankiaddon` über **Extras → Erweiterungen → Aus Datei installieren** installieren und Anki neu starten.
3. Die Feldmigration erfolgt beim Öffnen des Profils automatisch und erhält
   bestehende Notizen. `Distractors` wird bei Bedarf als neues Feld ergänzt.
4. **Extras → Interactive Cards · Vorlagen aktualisieren** aufrufen und
   bestätigen, damit **bereits bestehende AIC-Satzbaukarten** die zusätzlichen
   Wortkacheln anzeigen können. Das Add-on sichert zuvor die Vorlagen. Eigene
   Anpassungen an diesen Vorlagen werden beim Aktualisieren überschrieben.
5. Hinzufügen-Fenster schließen und neu öffnen, damit die Editoransicht mit
   den ausgeblendeten Feldern geladen wird.

**Verification status:** Automated checks cover the supported data and browser
paths. The add-on has also been exercised in Anki Desktop; run the update once
in a backed-up test profile after upgrading Anki or combining it with editor
add-ons that modify the same interface.

## Installation

Für die Nutzung sind neben einer kompatiblen Anki-Desktop-Installation keine
zusätzlichen Python-, Node- oder Systempakete erforderlich. Das Add-on verwendet
nur Ankis mitgelieferte Python-/Qt-Laufzeit und die Browserlogik in den
Kartenvorlagen.

1. Anki Desktop schließen bzw. vor der Installation ein Backup deiner Sammlung erstellen.
2. Die Datei `anki-interactive-cards-1.2.0.ankiaddon` herunterladen.
3. Anki → **Extras → Erweiterungen → Aus Datei installieren** (Bezeichnung kann je nach Sprache/Version variieren).
4. Die `.ankiaddon`-Datei auswählen und Anki **neu starten**.
5. Beim ersten Installieren zunächst **Extras → Interactive Cards · Kartenwerkstatt** einmal öffnen, damit die drei Notiztypen angelegt werden. Danach **Anki → Hinzufügen** öffnen und als Typ `AIC · Single Choice`, `AIC · Multiple Choice` oder `AIC · Sentence Builder` auswählen. Im normalen Editor auf **AIC · Antworten** klicken. Die separate **Kartenwerkstatt** unter Extras bleibt als Alternative verfügbar.

Die `.ankiaddon`-Datei enthält eine `manifest.json`. Bei einem Upgrade von 1.0.0 auf 1.2.0 bleiben die vorhandenen Notiztypen und Karten erhalten. Die neuen Editor-Schaltflächen funktionieren nach einem Anki-Neustart. Für den **neutralen Look bereits bestehender AIC-Notiztypen** unter **Extras → Interactive Cards · Vorlagen aktualisieren** wählen. Dabei werden die bisherigen Kartenvorlagen und deren CSS überschrieben; eine JSON-Sicherung wird zuvor unter `user_files/template_backups/` angelegt. Bestehende Feldinhalte und Wiederholungsdaten bleiben unberührt.

## Enthaltene Kartentypen

| Typ | Beispiel | Interaktion |
| --- | --- | --- |
| Single Choice / Text | `das Haus` → la casa / il libro / … | Eine Antwort per Klick, sofortiges Feedback |
| Single Choice / Bilder | `la casa` → vier Bilder | Bilder wählen; Medien lokal gespeichert |
| Multiple Choice | „Welche Begriffe sind Nomen?“ | Beliebig viele Häkchen, Gesamtprüfung |
| Sentence Builder | `Ich bin zu Hause` → `sono a casa` | Wortkacheln, Texteingabe oder Wahlmöglichkeit |

Alle Auswahlantworten werden beim Anzeigen zufällig gemischt. Für Sätze werden Wortbausteine gemischt. Wortkacheln können durch Antippen zurückgenommen werden. Satz-Alternativen werden berücksichtigt; Groß-/Kleinschreibung und Satzendzeichen (`.`, `!`, `?`) werden ignoriert, **Akzente und Schreibweisen bleiben relevant**.

## Standard-Anki-Editor (empfohlen ab 1.1)

1. Öffne **Hinzufügen** in Anki und wähle oben links `AIC · Single Choice`, `AIC · Multiple Choice` oder `AIC · Sentence Builder` sowie dein gewünschtes Deck.
2. Trage die **Frage in Prompt** ein; `Explanation`, `Prompt Image` und `Audio` sind optional. Du kannst wie gewohnt Tags hinzufügen.
3. Klicke oben in der Anki-Formatleiste auf **AIC · Antworten**. Wenn der Button fehlt, prüfe, ob das Add-on aktiv ist und starte Anki neu.
4. Für **Single/Multiple Choice**: Text und optional Bild pro Antwort eingeben, die korrekten Antworten mit Häkchen markieren (Single Choice = genau 1). Über **Bild auswählen …** wählst du die lokale Bilddatei für die gerade markierte Antwortzeile. Für **Sentence Builder**: Zielsatz, optional die Wortbausteine und alternative Lösungen sowie den Eingabemodus definieren.
5. **Übernehmen** klicken. Danach zum normalen Anki-Fenster zurückkehren und dort **Hinzufügen** klicken. **Das Popup speichert neue Karten nicht selbst.** Die Antworten werden von Anki beim Hinzufügen in die Notizfelder übertragen.

Bei bereits **gespeicherten** AIC-Notizen im Anki-Browser wird das Popup über denselben Button geöffnet; dann werden die Antwortfelder beim Übernehmen sofort in der bestehenden Notiz gespeichert.

**Hinweis für den Standardeditor:** Die technischen Felder `Options`, `Correct`, `Tokens`, `Alternatives`, `Distractors` und weitere werden standardmäßig **eingeklappt**, nicht gelöscht/versteckt. Öffne sie nur für technische Diagnose oder wenn du sie bewusst von Hand editieren willst. Die Feld-Einklappung kann Anki jederzeit per Pfeilsymbol geändert werden.

**Fehlervermeidung:** Wenn kein gültiger Antwortsatz hinterlegt ist, lehnt das Add-on das Hinzufügen einer AIC-Notiz mit einer Fehlermeldung ab. Du kannst die Antworten danach über **AIC · Antworten** korrigieren. Wenn ein neues Anki-Formular angelegt wird, müssen die Antwortoptionen erneut eingegeben werden; sie werden nicht auf die nächste Karte übertragen. Es werden ausschließlich AIC-Notizen validiert.

## Eine Karte manuell erstellen

1. Kartenwerkstatt öffnen und unter **Karte erstellen / bearbeiten** den Typ wählen.
2. Das Zieldeck und den Fragetext auswählen bzw. eingeben.
3. Für Auswahlkarten: pro Zeile Antworttext eintragen, **Richtig** anhaken und bei Bildauswahl die Bilddatei wählen. Bei Mehrfachauswahl dürfen mehrere Häkchen gesetzt werden.
4. Für Satzbau: gewünschten Zielsatz eintragen. Optional eigene Wortbausteine (durch Leerzeichen getrennt) und Alternativlösungen, je eine pro Zeile, eintragen.
5. **Karte erstellen** klicken.

Bilder werden in die **Anki-Mediensammlung** kopiert, nicht als absolute lokale Dateipfade in der Karte gespeichert. Audio kann mit **Audio wählen …** importiert oder als `[sound:datei.mp3]` angegeben werden, wenn die Datei bereits in Ankis Mediaverzeichnis existiert.

**Bearbeiten:** Browser öffnen → exakt eine interaktive AIC-Notiz markieren → Menü **Notizen → Interactive Cards · ausgewählte Notiz bearbeiten**. Die Änderung an den Notizfeldern verändert keine Schedulingwerte.

## Aus bestehenden Notizen generieren

Kartenwerkstatt → **Aus bestehenden Vokabeln erzeugen**:

1. **Quell-Notiztyp** und **Quell-Deck** wählen.
2. Das Feld für **Frage** und das Feld für **Antwort** zuordnen.
3. Für Bildauswahl zusätzlich das **Bildfeld** angeben; dieses Bild sollte zur Antwort der jeweiligen Vokabel gehören. Optional ein Audiofeld wählen.
4. Zieldeck, gewünschte Kartensorte und Anzahl falscher Antwortmöglichkeiten einstellen.
5. **Quelle prüfen**, dann **Karten erzeugen**.

Die Quellnotizen werden dabei **nicht verändert**. Für Auswahlkarten werden abweichende Antworten anderer Quellnotizen als Distraktoren vorgeschlagen; eine einfache Längen-/Wortanzahl-Heuristik sortiert diese. Diese Methode überprüft **keine semantische Gleichwertigkeit**. Distraktoren bitte kontrollieren; bei Synonymen oder mehrdeutigen Fragen manuell korrigieren.

Ausgangsnotizen müssen mindestens zwei geeignete, verschiedene Antworten enthalten; für Bildauswahl mindestens zwei gültige Bildzuordnungen. Die Stapelerstellung ist auf **maximal 5.000 Quellnotizen pro Durchlauf** begrenzt.

Bei erneutem Durchlauf werden bereits erzeugte Karten per Herkunfts-ID erkannt und standardmäßig übersprungen. Mit **Bereits erzeugte Karten aktualisieren** werden deren Inhalte aktualisiert, ohne die Karten zu entfernen oder ihren Lernstatus zurückzusetzen. Bereits manuell geänderte Antworten solcher Karten werden dadurch wieder überschrieben. **Die Aktualisierung läuft nicht permanent im Hintergrund**; sie muss manuell gestartet werden.

## Theme-Schnittstelle (Design separat)

Dieses Add-on nutzt ein **neutrales Design**. Es enthält keine Duolingo-/WoW-Optik, Soundeffekte, XP, Erfolge oder Gamification. Mit `.aic-root` und den untergeordneten `.aic-*`-Klassen sowie `--aic-color-text`, `--aic-color-surface`, `--aic-color-border`, `--aic-color-accent`, `--aic-color-accent-bg`, `--aic-color-success`, `--aic-color-danger`, `--aic-radius`, `--aic-spacing` und `--aic-font-family` stehen Theme-Anknüpfungspunkte zur Verfügung.

Fremde Add-ons können diese CSS-Variablen für den Desktop überschreiben, ohne Kartendaten oder Auswertung zu ändern. Für **AnkiDroid/AnkiMobile** muss ein Theme seine Stildefinitionen in den synchronisierten Notiztypen bzw. Medien bereitstellen, da Desktop-Python-Hooks auf mobilen Geräten nicht verfügbar sind.

## Mobil und AnkiWeb

Das Add-on selbst läuft **nur auf Anki Desktop**. Einmal erstellte Karten können über Anki-Synchronisierung auf andere Clients übertragen werden, weil die HTML-/CSS-/JavaScript-Kartenvorlagen in den Notiztypen gespeichert sind. **Auf Smartphones erstellst bzw. bearbeitest du die komplexen Karten am besten am Desktop.**

JavaScript in Karten ist von Anki **nicht für alle Clients und zukünftigen Versionen garantiert**. Das Paket wurde hier mit Chromium (Browser-Tests) getestet, **nicht in einer echten Anki-Desktop-, AnkiDroid- oder AnkiMobile-Installation**. Vor produktivem Einsatz alle Kartentypen, die falschen Wortkacheln und die Antwortseite auf deinen Geräten prüfen. Für AnkiWeb ebenfalls keine Garantie.

## Daten, Speicher und Grenzen

- Keine Cloud, Telemetrie oder externe Pakete zur Laufzeit.
- Keine Änderungen an FSRS, Wiederholungsplanung, Lapses, Kartenbewertungen oder Deck-Algorithmen.
- Anki-Bewertung **Again / Hard / Good / Easy erfolgt weiterhin durch den Nutzer**; eine im Kartentemplate als richtig erkannte Antwort führt nicht zu `Good`.
- Bei Multiple Choice wird ein Versuch nur dann als vollständig richtig gewertet, wenn **exakt die richtigen Optionen** markiert wurden.
- Im Satzbaustein-Modus werden Wörter anhand von Leerzeichen getrennt; komplexe Tokenisierung (z. B. Interpunktion als eigene Kachel) wird nicht automatisch geleistet. Eigene Wortbausteine sind möglich.
- Die Übertragung von Antwortversuchen auf die Rückseite ist eine optionale Komfortanzeige über Sitzungszustand; bei Clients mit getrennten WebViews kann die letzte Antwort fehlen, **die korrekte Lösung bleibt sichtbar**.
- Die Bildreferenzen werden explizit in einem Medienfeld vorgehalten, damit Anki die Dateien auch beim Export erkennen kann.
- Anki selbst erlaubt das direkte Editieren der JSON-Felder; für `Options`, `Correct`, `Tokens`, `Alternatives`, `Distractors` möglichst den AIC-Editor verwenden.

## Entwicklung / Tests

Ordnerstruktur:

```
anki_interactive_cards/
├── __init__.py                  # Anki-Menü und Browser-Eintrag
├── src/
│   ├── core.py                  # Validierung, Distraktoren, Textregeln
│   ├── anki_bridge.py           # Notiztypen, Medien, Batch-Generierung
│   ├── dialogs.py               # Kartenwerkstatt und Stapelgenerierung
│   ├── native_editor.py         # Native Editor-Schaltfläche / Anki-Speicherhooks
│   ├── editor_data.py           # Pure Validierung und Feldaufbereitung
│   ├── templates.py             # HTML/JS/CSS-Kartenvorlagen
│   └── web/card.js, card.css
├── tests/
└── examples/
```

**Unit-Tests:** `just test` (derzeit 19 Tests)
**Browser-Tests:** `just test-browser` (benötigt Python Playwright + lokales Chromium)
**Syntaxprüfung:** `python -m compileall -q .` und `node --check src/web/card.js`.

Für die Tests braucht man kein installiertes Anki, solange man nur die Kernlogik testet. Die tatsächliche Qt- und Anki-Integration erfordert einen separaten Test in einer Anki-Installation.

## Build a distributable add-on

Run the following command from the repository root:

```bash
just build
```

It creates `dist/anki-interactive-cards-1.2.0.ankiaddon`. The archive contains
only runtime files, with `__init__.py` and `manifest.json` at its root, and
excludes tests, Git metadata, caches, and local template backups. Before
sharing it, install it in a backed-up test profile through **Tools → Add-ons →
Install from file…**, restart Anki, and create or review one card of each AIC
note type. The `user_files/` marker is intentionally included so Anki retains
template backups during future add-on upgrades.

## Foundation package for automated deck builders

An agent that creates a complete `.apkg` without opening Anki's editor can use
`templates/aic-foundation/AIC Foundation.apkg` as a version-pinned base. It
contains the three complete AIC note types, including their embedded card
templates, CSS, and JavaScript.

The package intentionally includes three obvious seed notes tagged
`aic-foundation::seed`, because Anki only exports note types referenced by
notes. An automated builder imports the foundation into a temporary collection,
creates the requested notes, deletes every seed note and the now-empty `AIC
Foundation` deck, then exports the learner-facing deck without scheduling
history. The full field-serialization contract is in the shared **Anki deck
creation agent guide**.

Rebuild and verify the foundation after a template change:

```bash
just build-foundation
just verify-foundation
```

## Entwicklerhinweise

- `src/templates.py` speichert CSS und JS **inline im Notiztyp**; dadurch sind Karten selbsttragend und brauchen keine `/_addons`-Dateien auf mobilen Geräten.
- `Source ID` identifiziert automatisch erzeugte Karten, `UID` identifiziert den temporären Versuch im WebView.
- Die von Nutzern angepassten Kartenvorlagen werden bei normalem Start **nicht überschrieben**.
- Weitere Möglichkeiten: UI-Sprachen, semantische Distraktorprüfung, Quellenfeld-Live-Sync, separate Theme-Add-ons.

Siehe `CHANGELOG.md` und `LICENSE`. Dieses Projekt ist unter der GNU Affero
General Public License, Version 3 oder neuer (AGPL-3.0-or-later), lizenziert.
