# AIC Foundation source assets

`AIC Foundation.apkg` is a small, importable basis for a tool or agent that
creates a complete Anki package without access to this add-on's source code.
It carries the exact version 1.2.0 note types, card templates, inline CSS, and
inline JavaScript for:

- `AIC · Single Choice`
- `AIC · Multiple Choice`
- `AIC · Sentence Builder`

The package contains three deliberately obvious seed notes, all tagged
`aic-foundation::seed`, because Anki packages only carry note types that are
referenced by exported notes. It has no review history and no media.

## Agent workflow

1. Create a temporary Anki collection and import this foundation package.
2. Retain the three note types and their templates unchanged.
3. Create the requested AIC notes with the schema in the deck-agent guide.
4. Delete every note tagged `aic-foundation::seed` and remove the empty `AIC
   Foundation` deck before exporting the final deck package.
5. Export only the requested deck(s), without scheduling history. Verify that
   no seed notes appear in the result.

The AIC templates are self-contained in the note types. The learner's final
collection therefore does not need this source package or the Python add-on to
render already-created cards, although Anki Desktop with the add-on remains the
recommended way to edit their structured fields.
