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
        items = [item for item in items if item.status != "archived"]
        return sorted(items, key=lambda item: item.created_at, reverse=True)

    def list_archived_items(self) -> list[ListingItem]:
        data = self._read()
        items = [ListingItem.from_dict(item) for item in data.get("items", [])]
        archived = [item for item in items if item.status == "archived"]
        return sorted(archived, key=lambda item: item.archived_at or item.created_at, reverse=True)

    def list_all_items(self) -> list[ListingItem]:
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
        items = [existing for existing in self.list_all_items() if existing.id != item.id]
        items.append(item)
        self._write({"items": [existing.to_dict() for existing in items]})

    def has_source_folder(self, folder: str) -> bool:
        return any(item.source_folder == folder for item in self.list_all_items())

    def archive_item(self, item_id: str) -> ListingItem | None:
        item = self.get_item(item_id)
        if item is None:
            return None

        if item.status != "archived":
            item.previous_status = item.status
            item.status = "archived"
            item.archived_at = utc_now()
            self.upsert_item(item)
        return item

    def restore_item(self, item_id: str) -> ListingItem | None:
        item = self.get_item(item_id)
        if item is None:
            return None

        if item.status == "archived":
            item.status = item.previous_status or "drafting"
            item.previous_status = ""
            item.archived_at = None
            self.upsert_item(item)
        return item

    def get_item(self, item_id: str) -> ListingItem | None:
        return next((item for item in self.list_all_items() if item.id == item_id), None)

    def summary(self) -> dict[str, int | str]:
        items = self.list_items()
        all_items = self.list_all_items()
        live_items = [item for item in items if item.status != "sold"]
        sold_items = [item for item in all_items if _is_sold(item)]
        archived_items = [item for item in all_items if item.status == "archived"]
        live_prices = [_money_value(item.price) for item in live_items if _money_value(item.price) > 0]
        oldest_live = min((item.created_at for item in live_items), default=None)
        return {
            "total": len(items),
            "all_items": len(all_items),
            "archived": len(archived_items),
            "drafting": sum(1 for item in items if item.status == "drafting"),
            "ready": sum(1 for item in items if item.status == "ready"),
            "sold": len(sold_items),
            "responses": sum(item.response_count for item in items),
            "no_photo": sum(1 for item in items if not item.photo_paths),
            "photo_count": sum(len(item.photo_paths) for item in all_items),
            "average_live_price": _money(
                sum(live_prices, Decimal("0")) / len(live_prices)
                if live_prices
                else Decimal("0")
            ),
            "sell_through": _percent(len(sold_items), len(all_items)),
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


def _percent(part: int, whole: int) -> str:
    if whole <= 0:
        return "0%"
    return f"{round((part / whole) * 100)}%"


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


def _is_sold(item: ListingItem) -> bool:
    return item.status == "sold" or (
        item.status == "archived" and item.previous_status == "sold"
    )
