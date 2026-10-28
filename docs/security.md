# Security review

## Add-on scope

The add-on runs locally inside Anki Desktop. It has no accounts, network
service, telemetry, secret configuration, or runtime third-party dependency.
The relevant trust boundaries are imported card data, local media files, Anki's
collection/media APIs, and the HTML/JavaScript card templates.

- **A05 injection:** Card prompt/explanation values are HTML-escaped before
  field serialization. The browser templates create visible content with
  `textContent`, and media filenames reject URL schemes and path traversal.
- **A06 insecure design:** AIC never changes FSRS, Anki scheduling, ratings, or
  source notes during card generation. It bounds a generation run to 5,000
  source notes.
- **A08 integrity:** The archive builder whitelists runtime files and validates
  its root layout. User template backups are kept under Anki's preserved
  `user_files/` directory.
- **A10 exceptional conditions:** Invalid answer payloads, unsupported media,
  missing fields, and duplicate generation sources fail before an AIC note is
  written.

Anki card templates can execute JavaScript. This is an inherent Anki deck trust
boundary: users and deck-generation agents must import only trusted deck
sources. The AIC source does not fetch external scripts or media.

## Foundation package scope

## Scope

The AIC Foundation package is a fixed local `.apkg` produced from the
repository's existing note-type templates. It is intended only as a temporary
input to an automated deck builder. The builder removes its seed notes before
exporting the learner-facing package.

## Trust boundaries and controls

- **A08 integrity:** The builder creates an isolated collection and exports
  only three fixed, tagged seed notes. The verifier imports the artifact into a
  second temporary collection and checks the exact three note types, template
  presence, seed count, and absence of review history.
- **A05 injection:** The foundation contains no generated learner content,
  media, external URLs, or shell input. Its templates are copied from the
  reviewed local AIC source; a deck generator remains responsible for escaping
  its own prompt, explanation, and JSON field content as documented.
- **A03 supply chain:** The build uses the locally installed Anki runtime and
  repository source only. It adds no third-party package or network download.
- **A10 exceptional conditions:** The builder and verifier fail on missing
  models, fields, templates, seed cards, or unexpected review history. They
  never open or modify a user Anki profile.

## Focused review result

No finding in scope. Verification is limited to isolated collection imports;
manual review in a backed-up Anki Desktop profile remains appropriate after a
future Anki or template upgrade.
