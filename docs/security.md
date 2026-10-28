# Security review: AIC Foundation package

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
