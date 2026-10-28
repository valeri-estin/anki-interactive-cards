# AnkiWeb description

**Published add-on ID:** `334923313`  
**Release archive:** `anki-interactive-cards-1.2.1.ankiaddon`  
**Last reviewed:** 2026-10-28

Copy the content below, starting at the next heading, into AnkiWeb's
**Description** field. Keep it synchronized with the released archive.

## Create interactive choice and sentence-building cards

Anki Interactive Cards (AIC) adds guided authoring tools and self-contained
interactive card templates to Anki Desktop.

Create text or image choice cards, multiple-choice exercises, and
sentence-building cards with word tiles, typing, or both. Cards provide
immediate feedback, but only you choose **Again**, **Hard**, **Good**, or
**Easy**.

### Included card types

- **AIC · Single Choice** — choose one correct text or image answer.
- **AIC · Multiple Choice** — select every correct answer; the full selection
  must be exact.
- **AIC · Sentence Builder** — build a target sentence with shuffled word tiles,
  typing, or both. Optional distractor tiles are supported.

### Requirements

- Anki Desktop
- No additional Python packages, Node packages, system libraries, accounts, or
  cloud services

AIC uses Anki's included Python/Qt runtime. The interactive HTML, CSS, and
JavaScript are embedded in the note types, so created cards can sync to other
Anki clients.

### First-time setup

1. Back up your Anki collection.
2. Install the add-on and restart Anki.
3. Open **Tools → Interactive Cards · Card Workshop** once. This creates the
   three AIC note types.
4. Open Anki's **Add** window and select an AIC note type.
5. Enter the prompt, then click **AIC · Answers** in the editor toolbar.
6. Configure the answers and click **Apply**.
7. Return to Anki's normal Add window and click **Add** to save the note.

The AIC answer dialog prepares note fields; it does not create a separate Anki
note itself.

### Interface language

The interface and newly created card templates use English by default.

To use German, open the add-on configuration and set:

```json
{
  "ui_language": "de"
}
```

Restart Anki, then choose **Tools → Interactive Cards · Update templates**.
This explicit update applies the selected language to the AIC card templates
that sync with your decks.

Set `"ui_language"` to `"en"` and repeat the template update to return to
English.

### Daily authoring workflow

- Create a card in Anki's normal **Add** window.
- Use **AIC · Answers** to configure options, correct answers, sentence tokens,
  alternatives, modes, and optional distractors.
- Add an explanation, prompt image, audio, and tags in Anki's normal editor.
- To edit one existing AIC note, select it in Anki's Browser and choose
  **Notes → Interactive Cards · Edit selected note**.
- To generate exercises from existing vocabulary, open **Interactive Cards ·
  Card Workshop → Generate from existing vocabulary**.

Review generated distractors carefully, especially where answers may be
synonyms or ambiguous.

### Important behavior

- No cloud service, telemetry, or external runtime dependency is used.
- AIC does not alter FSRS, scheduling, review history, or card ratings.
- Choice options and word tiles are shuffled when shown.
- Sentence alternatives are supported. Letter case and final punctuation are
  ignored; spelling and accents remain meaningful.
- Creation and editing require Anki Desktop. Test interactive behavior on every
  target client before broad use.

### Updating existing templates

**Interactive Cards · Update templates** replaces existing AIC templates and
may overwrite personal template customizations. A template backup is created
first. Use a backup or disposable profile when updating.

### License

Licensed under the GNU Affero General Public License, version 3 or later
(AGPL-3.0-or-later).

### Source code and issues

Source code, installation guidance, and issue reports are available through the
Support Page.
