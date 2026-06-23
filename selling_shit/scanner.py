from __future__ import annotations

import shutil
from pathlib import Path

from .models import ListingItem
from .storage import CatalogStore

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic"}


def scan_catalog_folder(
    inbox_dir: str | Path,
    uploads_dir: str | Path,
    store: CatalogStore,
) -> list[ListingItem]:
    inbox = Path(inbox_dir)
    uploads = Path(uploads_dir)
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
            title=title or folder.name.replace("-", " ").title(),
            description=description,
            price=price,
            photo_paths=[],
            source_folder=source_key,
        )
        item_upload_dir = uploads / item.id
        item_upload_dir.mkdir(parents=True, exist_ok=True)

        item.photo_paths = []
        for image in images:
            destination = item_upload_dir / image.name
            shutil.copy2(image, destination)
            item.photo_paths.append(str(destination.relative_to(uploads.parent)).replace("\\", "/"))

        store.upsert_item(item)
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
