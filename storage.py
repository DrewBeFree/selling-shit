from __future__ import annotations

import json
import re
from pathlib import Path
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from models import ListingItem, utc_now


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
        live_items = [item for item in items if item.status != "sold"]
        sold_items = [item for item in items if item.status == "sold"]
        oldest_live = min((item.created_at for item in live_items), default=None)
        return {
            "total": len(items),
            "drafting": sum(1 for item in items if item.status == "drafting"),
            "ready": sum(1 for item in items if item.status == "ready"),
            "sold": len(sold_items),
            "responses": sum(item.response_count for item in items),
            "live_value": _money(sum((_money_value(item.price) for item in live_items), Decimal("0"))),
            "sold_value": _money(
                sum(
                    (
                        _money_value(item.sold_price or item.price)
                        for item in sold_items
                    ),
                    Decimal("0"),
                )
            ),
            "listing_age": _age_label(oldest_live),
        }

    def _read(self) -> dict[str, list[dict]]:
        if not self.path.exists():
            return {"items": []}
        return json.loads(self.path.read_text(encoding="utf-8-sig"))

    def _write(self, data: dict[str, list[dict]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _new_item_id(self, title: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "item"
        return f"{slug}-{uuid4().hex[:8]}"


def _money_value(value: str) -> Decimal:
    cleaned = re.sub(r"[^0-9.]", "", value or "")
    if not cleaned:
        return Decimal("0")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return Decimal("0")


def _money(value: Decimal) -> str:
    if value == value.to_integral():
        return f"${value.quantize(Decimal('1'))}"
    return f"${value.quantize(Decimal('0.01'))}"


def _age_label(started_at) -> str:
    if started_at is None:
        return "No live listings"

    delta = utc_now() - started_at
    if delta.total_seconds() <= 0:
        return "Just listed"

    days = delta.days
    hours = delta.seconds // 3600
    if days:
        return f"{days}d {hours}h"
    return f"{hours}h"
