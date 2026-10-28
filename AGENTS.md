# Project instructions

This repository is an Anki Desktop add-on. Keep the repository root as the
add-on root: release archives must contain `__init__.py` and `manifest.json`
directly at their root, without an enclosing project directory.

Keep repository documentation and code comments in English. Keep portable
card-template and menu copy in `src/localization.py`: English is the default
and German is available through the `ui_language` add-on configuration.

Run `just check` after changing runtime code, tests, or packaging logic. Do not
package Git metadata, Python caches, or user-created template backups.
