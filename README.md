# Anki Interactive Cards

**Version:** 1.2.1
**Platform:** Anki Desktop (Python/Qt 6 add-on for authoring; HTML and JavaScript cards for review)
**Interface language:** English by default; German available through add-on configuration
**License:** AGPL-3.0-or-later

Anki Interactive Cards (AIC) adds interactive note types to Anki. It uses
Anki's normal scheduler, including FSRS: it never assigns ratings, rewrites
learning progress, or calls a network service. Learners still choose Anki's
native **Again**, **Hard**, **Good**, or **Easy** rating.

## Requirements and installation

No Python, Node.js, or system packages are required beyond a compatible Anki
Desktop installation. AIC uses only Anki's bundled Python/Qt runtime and the
HTML/JavaScript embedded in its card templates.

1. Back up the collection and close Anki.
2. Download `anki-interactive-cards-1.2.1.ankiaddon`.
3. In Anki Desktop, choose **Tools → Add-ons → Install from file…** (the label
   varies with Anki's interface language), select the archive, and restart
   Anki.
4. On a first installation, open **Tools → Interactive Cards · Card Workshop**
   once to create the note types.
5. In **Add**, select `AIC · Single Choice`, `AIC · Multiple Choice`, or
   `AIC · Sentence Builder`. Click **AIC · Answers** in Anki's formatting bar,
   define the answers, click **Apply**, then use Anki's normal **Add** button.

The answer dialog does not create a card by itself. It validates and prepares
the AIC fields; Anki creates or saves the note. When editing one existing AIC
note in Anki's browser, applying the dialog writes the updated AIC fields to
that note. If the toolbar button is missing, confirm that the add-on is enabled
and restart Anki.

To use German card copy, open the add-on configuration in Anki, set
`ui_language` to `"de"`, restart Anki, and choose **Tools → Interactive Cards
· Update templates**. The explicit update replaces AIC card templates so the
synced cards use the selected language. Set `ui_language` to `"en"` and repeat
the update to return to English. Note type names and stored field names never
change.

For an update from 1.1.0, create a backup first. Existing note data is
preserved; `Distractors` is added as needed. To apply the new sentence-builder
templates to existing note types, choose **Tools → Interactive Cards · Update
templates**. This deliberately replaces the affected HTML/CSS templates, after
creating a JSON backup in `user_files/template_backups/`; it does not change
field content or scheduling data. Reopen Add after an update so Anki reloads
the editor view.

## Included card types

| Type | Example | Interaction |
| --- | --- | --- |
| Single Choice / text | `das Haus` → `la casa` / `il libro` / … | Select one answer and receive immediate feedback. |
| Single Choice / images | `la casa` → four images | Select a locally stored image. |
| Multiple Choice | “Which terms are nouns?” | Select any number of answers and submit the complete set. |
| Sentence Builder | `Ich bin zu Hause` → `sono a casa` | Arrange word tiles, type an answer, or use both modes. |

Answer choices and sentence tokens are shuffled when a card is shown. Sentence
alternatives are supported. Case and terminal `.`, `!`, and `?` are ignored;
accents and spelling remain significant.

### Sentence Builder distractors

Use `AIC · Sentence Builder`, enter the prompt, open **AIC · Answers**, then
enter the target sentence. Add one wrong word tile per line under **Wrong word
tiles** and select **Word tiles and typing** or **Word tiles only**. The tiles
are shuffled; learners need not use every tile. A distractor must not have the
same text as a required correct token, otherwise the card cannot distinguish
them. Existing sentence-builder notes without distractors continue to work.

## Authoring notes

The ordinary editor keeps **Prompt**, **Explanation**, **Prompt Image**, and
**Audio** visible. Technical fields such as `Options`, `Correct`, `Media
References`, `Answer`, `Tokens`, `Alternatives`, `Mode`, `Distractors`, `UID`,
and `Source ID` remain stored but are collapsed by default. Use **AIC ·
Technical** only for diagnosis or intentional low-level editing.

The separate **Card Workshop** is an alternative authoring UI. It can create a
card manually or generate selection cards from existing vocabulary notes. For a
generation run, select the source note type, source deck, question and answer
fields, optional image/audio fields, target deck, card type, and number of
distractors. The source notes are never changed. Generated cards have a source
ID; a later run skips them by default or can update their content without
resetting scheduling. A run is limited to 5,000 source notes. Review suggested
distractors, because the simple text-length/word-count heuristic does not prove
semantic suitability.

Images selected in AIC are copied into Anki's media collection, never stored as
absolute local paths. Audio can be imported with **Choose audio…** or referred
to as `[sound:file.mp3]` if it already exists in Anki's media directory.

## Mobile, AnkiWeb, and safety boundaries

The add-on itself runs only on Anki Desktop. Cards created with it can sync to
other clients because their templates live in the note types. Complex cards are
best created and edited on Desktop. JavaScript card behaviour is not guaranteed
by every current or future Anki client, so test the card types, distractors, and
answer display on the learner's target devices before a broad rollout.

AIC has no cloud service, telemetry, or runtime third-party dependency. It does
not alter FSRS, scheduling, lapses, or card ratings. An answer judged correct by
the template does not automatically select **Good**. Import only decks from
sources you trust: Anki card templates can contain JavaScript, which is a
general Anki trust boundary rather than a special AIC permission.

## Foundation package for deck-generation agents

`templates/aic-foundation/AIC Foundation.apkg` is a version-pinned base for an
agent that builds a complete `.apkg` without using Anki's editor. It contains
the three AIC note types with their embedded templates, CSS, and JavaScript.
It also deliberately contains three notes tagged `aic-foundation::seed`, so
Anki exports the note types. A deck builder must import it into a temporary
collection, create its requested notes, remove all seed notes and the empty
`AIC Foundation` deck, then export the learner-facing deck without review
history. See the shared Anki deck-creation agent guide for the field contract.

After changing templates, run:

```bash
just build-foundation
just verify-foundation
```

## Development and release

```bash
just test          # 19 Python unit tests
python3 -m pip install playwright==1.64.1
just test-browser  # requires that package and /usr/bin/chromium
just check         # unit tests, syntax checks, and archive validation
just build
```

Playwright is a development-only test dependency. It is not required by the
installed add-on and is not included in the release archive.

The release archive has `__init__.py` and `manifest.json` at its root and
includes only runtime files, the full `LICENSE`, and the `user_files` marker.
It excludes Git metadata, tests, caches, and user-created backups. Before
sharing a release, install it into a backed-up test profile, restart Anki, and
author and review one card of each type.

Further implementation and release details are in [docs/README.md](docs/README.md).

## License

Licensed under the GNU Affero General Public License, version 3 or later
(AGPL-3.0-or-later). The complete license text is in [LICENSE](LICENSE).
