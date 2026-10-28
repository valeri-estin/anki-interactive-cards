# Changelog

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased

### Changed

- Replaced the short licensing notice with the complete AGPL-3.0 license text
  in source and release archives.
- Rewrote the public README in English and documented the desktop-only trust
  boundary for executable Anki card templates.

### Added

- A reproducible minimal `.ankiaddon` builder, release guide, and preserved
  `user_files` marker for template backups.
- An importable AIC Foundation `.apkg` for automated deck builders, including
  isolated package verification and seed-removal guidance.

## 1.2.0 — 2026-10-28

- Technical note fields are collapsed by default in Anki's normal editor while
  Prompt, Explanation, Prompt Image, and Audio stay visible.
- **AIC · Technical** reveals the technical fields when required.
- Existing AIC note types receive the native Anki `collapsed` field property
  without automatically replacing their card templates.
- Sentence Builder supports optional wrong word tiles in `Distractors`, in
  both the answer editor and Card Workshop.
- Word tiles are shuffled and learners need not use every tile.
- Existing sentence-builder cards without `Distractors` remain compatible.
- A non-destructive profile-start migration adds the field where needed;
  template replacement remains explicit and creates a backup.
- Added validation, migration, browser, and editor-view tests.
- FSRS, the Anki scheduler, and native rating buttons remain unchanged.

## 1.1.0 — 2026-10-28

- Added the **AIC · Answers** toolbar button to Anki's native Add/Edit view,
  with answer rows, checkboxes, local image selection, and sentence-builder
  alternatives without manual JSON editing.
- Validated answers are applied immediately before Anki saves a new note; the
  temporary dialog state is discarded after success.
- Editing an existing note changes only AIC answer fields, not scheduling,
  FSRS, or unrelated fields.
- Technical fields are collapsed by default on new note types and during an
  explicit template update for existing note types.
- Added neutral light/dark card styling and stable `.aic-*` selectors plus
  `--aic-*` CSS variables for independent theme add-ons.
- Corrected the responsive answer grid and added template backups before an
  explicit update.
- Verified 17 Python unit tests and five browser scenarios. A manual test in a
  backed-up Anki Desktop profile remains appropriate after future upgrades.

## 1.0.0 — 2026-10-28

- First add-on package with text and image Single Choice, Multiple Choice, and
  Sentence Builder note types.
- Added the Desktop Card Workshop, image/audio import, generation from existing
  vocabulary notes, and mobile-capable embedded HTML/JavaScript templates.
- Does not modify FSRS or other scheduling values.
