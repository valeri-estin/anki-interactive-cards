"""Build a minimal, installable Anki add-on archive."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATHS = ("__init__.py", "LICENSE", "manifest.json", "config.json", "src", "user_files")


def runtime_files() -> list[Path]:
    files: list[Path] = []
    for relative_path in RUNTIME_PATHS:
        path = ROOT / relative_path
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file()
                and "__pycache__" not in candidate.parts
                and candidate.suffix not in {".pyc", ".pyo"}
            )
    return sorted(files)


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    version = manifest["human_version"]
    output = ROOT / "dist" / f"anki-interactive-cards-{version}.ankiaddon"
    output.parent.mkdir(exist_ok=True)

    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for file in runtime_files():
            archive.write(file, file.relative_to(ROOT).as_posix())

    with ZipFile(output) as archive:
        names = set(archive.namelist())
    required = {"__init__.py", "LICENSE", "manifest.json"}
    if not required.issubset(names):
        raise RuntimeError(f"Invalid add-on archive; missing {sorted(required - names)}")
    print(output)


if __name__ == "__main__":
    main()
