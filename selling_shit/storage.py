from __future__ import annotations

import json
import re
from pathlib import Path
from uuid import uuid4

from .models import ListingItem


class CatalogStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def list_items(self) -> list[ListingItem]:
        data = self._read()
        items = [ListingItem.from_dict(item) for item in data.get("items", [])]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    def add_item(
        self,
        *,
        title: str,
        description: str,
        price: str,
        photo_paths: list[str],
        status: str = "drafting",
        source_folder: str | None = None,
    ) -> ListingItem:
        item = ListingItem(
            id=self._new_item_id(title),
            title=title.strip() or "Untitled item",
            description=description.strip(),
            price=price.strip(),
            photo_paths=photo_paths,
            status=status,
            source_folder=source_folder,
        )
        self.upsert_item(item)
        return item

    def upsert_item(self, item: ListingItem) -> None:
        items = [existing for existing in self.list_items() if existing.id != item.id]
        items.append(item)
        self._write({"items": [existing.to_dict() for existing in items]})

    def has_source_folder(self, folder: str) -> bool:
        return any(item.source_folder == folder for item in self.list_items())

    def summary(self) -> dict[str, int]:
        items = self.list_items()
        return {
            "total": len(items),
            "drafting": sum(1 for item in items if item.status == "drafting"),
            "ready": sum(1 for item in items if item.status == "ready"),
            "responses": sum(item.response_count for item in items),
        }

    def _read(self) -> dict[str, list[dict]]:
        if not self.path.exists():
            return {"items": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict[str, list[dict]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _new_item_id(self, title: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "item"
        return f"{slug}-{uuid4().hex[:8]}"
