from __future__ import annotations

import json
import re
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import uuid4

from models import ListingItem, format_time_delta, utc_now


PLATFORM_KEYS = ("nextdoor", "ebay", "facebook")


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

    def summary(self) -> dict[str, object]:
        items = self.list_items()
        all_items = self.list_all_items()
        live_items = [item for item in items if item.status != "sold"]
        sold_items = [item for item in all_items if _is_sold(item)]
        sellable_items = [item for item in all_items if _is_sellable(item)]
        oldest_live = min((item.created_at for item in live_items), default=None)
        platform_gap_total, platform_gaps = _platform_gaps(items)
        auction_due_items = _auction_due_items(live_items)
        next_auction_deadline = min(
            (
                item.auction_ends_at
                for item in live_items
                if item.listing_type == "auction"
                and item.auction_ends_at is not None
                and item.auction_ends_at > utc_now()
            ),
            default=None,
        )
        return {
            "total": len(items),
            "drafting": sum(1 for item in items if item.status == "drafting"),
            "ready": sum(1 for item in items if item.status == "ready"),
            "listed": sum(1 for item in items if item.status == "listed"),
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
            "needs_photos": sum(1 for item in live_items if not item.photo_paths),
            "needs_details": sum(1 for item in live_items if _needs_details(item)),
            "stale_drafts": sum(1 for item in items if _is_stale_draft(item)),
            "platform_gap_total": platform_gap_total,
            "platform_gaps": platform_gaps,
            "auction_due": len(auction_due_items),
            "auction_ended": sum(
                1
                for item in auction_due_items
                if item.auction_ends_at is not None and item.auction_ends_at <= utc_now()
            ),
            "next_auction_deadline": (
                format_time_delta(next_auction_deadline, expired_label="Ended")
                if next_auction_deadline
                else "None scheduled"
            ),
            "avg_live_age": _format_days_average(_average_live_age_days(live_items)),
            "conversion_rate": _percent(len(sold_items), len(sellable_items)),
            "sold_30d": sum(1 for item in sold_items if _sold_within_days(item, 30)),
            "response_rate": _percent(
                sum(1 for item in live_items if item.response_count > 0),
                len(live_items),
            ),
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


def _needs_details(item: ListingItem) -> bool:
    title = item.title.strip()
    description = item.description.strip()
    normalized_description = description.lower()
    return (
        not title
        or title.lower().startswith("untitled")
        or not description
        or normalized_description in {"description needed.", "description needed"}
        or len(description) < 12
        or not item.price.strip()
        or _money_value(item.price) <= 0
    )


def _is_stale_draft(item: ListingItem) -> bool:
    return item.status == "drafting" and utc_now() - item.created_at >= timedelta(days=7)


def _platform_gaps(items: list[ListingItem]) -> tuple[int, dict[str, int]]:
    eligible_items = [item for item in items if item.status in {"ready", "listed"}]
    gaps = {
        platform: sum(
            1 for item in eligible_items if not item.posted_platforms.get(platform, False)
        )
        for platform in PLATFORM_KEYS
    }
    total = sum(
        1
        for item in eligible_items
        if any(not item.posted_platforms.get(platform, False) for platform in PLATFORM_KEYS)
    )
    return total, gaps


def _auction_due_items(items: list[ListingItem]) -> list[ListingItem]:
    return [
        item
        for item in items
        if item.listing_type == "auction"
        and item.auction_ends_at is not None
        and item.auction_ends_at - utc_now() <= timedelta(hours=48)
    ]


def _average_live_age_days(items: list[ListingItem]) -> float | None:
    if not items:
        return None
    seconds_per_day = 24 * 60 * 60
    return sum(
        (utc_now() - item.created_at).total_seconds() / seconds_per_day
        for item in items
    ) / len(items)


def _format_days_average(days: float | None) -> str:
    if days is None:
        return "No live listings"
    if days < 1:
        return "<1d"
    return f"{int(days)}d avg"


def _percent(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0%"
    return f"{round((numerator / denominator) * 100)}%"


def _is_sellable(item: ListingItem) -> bool:
    return item.status in {"ready", "listed", "sold"} or (
        item.status == "archived" and item.previous_status in {"ready", "listed", "sold"}
    )


def _sold_within_days(item: ListingItem, days: int) -> bool:
    return item.sold_at is not None and item.sold_at >= utc_now() - timedelta(days=days)


def _is_sold(item: ListingItem) -> bool:
    return item.status == "sold" or (
        item.status == "archived" and item.previous_status == "sold"
    )
