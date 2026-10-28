#!/usr/bin/env python3
"""Verify the AIC foundation package in an isolated temporary collection."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.anki_bridge import new_payload  # noqa: E402
from src.templates import NOTE_TYPES  # noqa: E402


SEED_TAG = "aic-foundation::seed"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="AIC Foundation .apkg to verify")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.path.is_file():
        print("package_not_found", file=sys.stderr)
        return 2
    try:
        from anki.collection import Collection
        from anki.importing import ImportAnkiPackageOptions, ImportAnkiPackageRequest

        with tempfile.TemporaryDirectory(prefix="anki-interactive-cards-verify-") as directory:
            collection = Collection(str(Path(directory) / "verification.anki2"))
            try:
                collection.import_anki_package(
                    ImportAnkiPackageRequest(
                        package_path=str(args.path),
                        options=ImportAnkiPackageOptions(
                            merge_notetypes=True,
                            with_scheduling=False,
                            with_deck_configs=True,
                        ),
                    )
                )
                for specification in NOTE_TYPES.values():
                    model = collection.models.by_name(specification["name"])
                    if model is None:
                        raise ValueError(f"missing_note_type:{specification['name']}")
                    if [field["name"] for field in model["flds"]] != specification["fields"]:
                        raise ValueError(f"unexpected_fields:{specification['name']}")
                    if len(model["tmpls"]) != 1 or model["tmpls"][0]["name"] != "Interaktive Karte":
                        raise ValueError(f"unexpected_template:{specification['name']}")
                    if "<script>" not in model["tmpls"][0]["qfmt"]:
                        raise ValueError(f"missing_runtime:{specification['name']}")
                seed_ids = collection.find_notes(f"tag:{SEED_TAG}")
                if len(seed_ids) != 3 or collection.card_count() != 3:
                    raise ValueError("unexpected_seed_cards")
                if collection.db.scalar("select count() from revlog") != 0:
                    raise ValueError("unexpected_review_history")

                output_deck = collection.decks.id("Generated Output")
                output_model = collection.models.by_name("AIC · Single Choice")
                if output_model is None:
                    raise ValueError("missing_output_model")
                from anki.notes import Note

                output_note = Note(collection, output_model)
                for field_name, value in new_payload(
                    "choice",
                    "What is a foundation package?",
                    options=[
                        {"text": "A reusable note-type base", "image": ""},
                        {"text": "A review history", "image": ""},
                    ],
                    correct=[0],
                    uid="aicfoundationverifyoutput00000000",
                    source_id="aic-foundation:verify:output",
                ).items():
                    output_note[field_name] = value
                collection.add_note(output_note, deck_id=output_deck)

                output_path = Path(directory) / "generated-output.apkg"
                from anki.collection import NoteIdsLimit
                from anki.exporting import ExportAnkiPackageOptions

                collection.export_anki_package(
                    out_path=str(output_path),
                    options=ExportAnkiPackageOptions(
                        with_scheduling=False,
                        with_deck_configs=True,
                        with_media=True,
                        legacy=True,
                    ),
                    limit=NoteIdsLimit([int(output_note.id)]),
                )
                generated = Collection(str(Path(directory) / "generated.anki2"))
                try:
                    generated.import_anki_package(
                        ImportAnkiPackageRequest(
                            package_path=str(output_path),
                            options=ImportAnkiPackageOptions(
                                merge_notetypes=True,
                                with_scheduling=False,
                                with_deck_configs=True,
                            ),
                        )
                    )
                    if generated.note_count() != 1 or generated.card_count() != 1:
                        raise ValueError("unexpected_generated_deck")
                    if generated.find_notes(f"tag:{SEED_TAG}"):
                        raise ValueError("seed_leaked_into_generated_deck")
                    if generated.db.scalar("select count() from revlog") != 0:
                        raise ValueError("generated_deck_has_review_history")
                finally:
                    generated.close()
            finally:
                collection.close()
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("AIC Foundation package is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
