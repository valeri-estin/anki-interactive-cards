# Release guide

1. Update `human_version` in `manifest.json`, the README, and the changelog.
2. Run `just check`.
3. Install the generated archive in a backed-up Anki Desktop test profile with
   **Tools → Add-ons → Install from file…** and restart Anki.
4. Create or edit one card for every AIC note type, then review it once. Confirm
   that the native Anki answer buttons and scheduling remain unchanged.
5. Run **Interactive Cards · Vorlagen aktualisieren** only on a disposable or
   backed-up collection, because it deliberately replaces existing templates.

The package identifier in `manifest.json` is a stable upgrade identity. Do not
change it after publishing an archive. `user_files/README.txt` must remain in
the release archive so Anki retains user-created template backups on upgrade.
