from __future__ import annotations

import shutil
import re
from pathlib import Path

from werkzeug.utils import secure_filename

from models import ListingItem
from storage import CatalogStore

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic"}


def scan_catalog_folder(
    inbox_dir: str | Path,
    active_dir: str | Path,
    store: CatalogStore,
) -> list[ListingItem]:
    inbox = Path(inbox_dir)
    active = Path(active_dir)
    media_base = active.parent.parent
    if not inbox.exists():
        inbox.mkdir(parents=True, exist_ok=True)
        return []

    imported: list[ListingItem] = []
    for folder in sorted(path for path in inbox.iterdir() if path.is_dir()):
        source_key = str(folder.resolve())
        if store.has_source_folder(source_key):
            continue

        images = [path for path in sorted(folder.iterdir()) if path.suffix.lower() in IMAGE_EXTENSIONS]
        if not images:
            continue

        title, description, price = _read_description(folder)
        item = store.add_item(
            title=title or _title_from_folder(folder),
            description=description,
            price=price,
            photo_paths=[],
            source_folder=source_key,
        )
        item_active_dir = active / item.id
        item_active_dir.mkdir(parents=True, exist_ok=True)

        item.photo_paths = []
        for image in images:
            filename = secure_filename(image.name) or "photo"
            destination = _unique_destination(item_active_dir, filename)
            shutil.copy2(image, destination)
            item.photo_paths.append(str(destination.relative_to(media_base)).replace("\\", "/"))

        description_file = folder / "description.txt"
        if description_file.exists():
            shutil.copy2(description_file, item_active_dir / "description.txt")

        item.source_folder = str(item_active_dir.resolve())
        store.upsert_item(item)
        shutil.rmtree(folder)
        imported.append(item)

    return imported


def _read_description(folder: Path) -> tuple[str, str, str]:
    description_file = folder / "description.txt"
    if not description_file.exists():
        return "", "", ""

    lines = [line.strip() for line in description_file.read_text(encoding="utf-8").splitlines()]
    title = lines[0] if len(lines) >= 1 else ""
    description = lines[1] if len(lines) >= 2 else ""
    price = lines[2] if len(lines) >= 3 else ""
    return title, description, price


def _title_from_folder(folder: Path) -> str:
    title = re.sub(r"[_-]+", " ", folder.name)
    title = re.sub(r"\s+", " ", title).strip()
    return title.title()


def _unique_destination(folder: Path, filename: str) -> Path:
    destination = folder / filename
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    counter = 2
    while True:
        candidate = folder / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
