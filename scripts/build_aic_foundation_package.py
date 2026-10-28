#!/usr/bin/env python3
"""Build an importable AIC foundation package in an isolated collection."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.anki_bridge import new_payload  # noqa: E402
from src.templates import CSS, NOTE_TYPES, make_template  # noqa: E402


FOUNDATION_DECK = "AIC Foundation"
SEED_TAG = "aic-foundation::seed"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="destination .apkg file")
    return parser.parse_args()


def add_note_type(collection, kind: str):
    specification = NOTE_TYPES[kind]
    model = collection.models.new(specification["name"])
    for field_name in specification["fields"]:
        collection.models.add_field(model, collection.models.new_field(field_name))
    template = collection.models.new_template("Interaktive Karte")
    template.update(make_template(kind))
    collection.models.add_template(model, template)
    model["css"] = CSS
    collection.models.add(model)
    result = collection.models.by_name(specification["name"])
    if result is None:
        raise RuntimeError(f"note_type_not_created:{specification['name']}")
    return result


def add_seed_note(collection, model, fields: dict[str, str], deck_id: int) -> int:
    from anki.notes import Note

    note = Note(collection, model)
    for field_name, value in fields.items():
        note[field_name] = value
    note.add_tag(SEED_TAG)
    collection.add_note(note, deck_id=deck_id)
    return int(note.id)


def main() -> int:
    args = parse_args()
    from anki.collection import Collection, NoteIdsLimit
    from anki.exporting import ExportAnkiPackageOptions

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="anki-interactive-cards-foundation-") as directory:
        collection = Collection(str(Path(directory) / "AIC Foundation.anki2"))
        try:
            deck_id = collection.decks.id(FOUNDATION_DECK)
            seed_ids = []
            choice_model = add_note_type(collection, "choice")
            seed_ids.append(
                add_seed_note(
                    collection,
                    choice_model,
                    new_payload(
                        "choice",
                        "Foundation seed — delete before export.",
                        options=[
                            {"text": "Keep no seed cards", "image": ""},
                            {"text": "Delete this note", "image": ""},
                        ],
                        correct=[1],
                        source_id="aic-foundation:seed:choice",
                        uid="aicfoundationseedchoice0000000000",
                    ),
                    deck_id,
                )
            )
            multi_model = add_note_type(collection, "multi")
            seed_ids.append(
                add_seed_note(
                    collection,
                    multi_model,
                    new_payload(
                        "multi",
                        "Foundation seed — delete before export.",
                        options=[
                            {"text": "Delete this note", "image": ""},
                            {"text": "Do not export it", "image": ""},
                            {"text": "Keep it in the final deck", "image": ""},
                        ],
                        correct=[0, 1],
                        source_id="aic-foundation:seed:multi",
                        uid="aicfoundationseedmulti00000000000",
                    ),
                    deck_id,
                )
            )
            sentence_model = add_note_type(collection, "sentence")
            seed_ids.append(
                add_seed_note(
                    collection,
                    sentence_model,
                    new_payload(
                        "sentence",
                        "Foundation seed — delete before export.",
                        answer="delete this note",
                        tokens=["delete", "this", "note"],
                        alternatives=[],
                        mode="both",
                        distractors=["keep"],
                        source_id="aic-foundation:seed:sentence",
                        uid="aicfoundationseedsentence000000000",
                    ),
                    deck_id,
                )
            )
            options = ExportAnkiPackageOptions(
                with_scheduling=False,
                with_deck_configs=True,
                with_media=True,
                legacy=True,
            )
            collection.export_anki_package(
                out_path=str(args.output), options=options, limit=NoteIdsLimit(seed_ids)
            )
        finally:
            collection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
