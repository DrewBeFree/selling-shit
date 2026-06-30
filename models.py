from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


@dataclass
class PlatformDraft:
    platform: str
    title: str
    body: str
    fields: dict[str, str]
    icon_label: str
    icon_class: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ListingItem:
    id: str
    title: str
    description: str
    price: str
    photo_paths: list[str]
    created_at: datetime = field(default_factory=utc_now)
    deadline_at: datetime | None = None
    auction_ends_at: datetime | None = None
    sold_at: datetime | None = None
    archived_at: datetime | None = None
    status: str = "drafting"
    previous_status: str = ""
    listing_type: str = "fixed_price"
    sold_price: str = ""
    notes: str = ""
    watch_count: int = 0
    response_count: int = 0
    source_folder: str | None = None

    @property
    def created_label(self) -> str:
        return (
            f"{self.created_at.strftime('%b')} {self.created_at.day}, "
            f"{self.created_at.year} {self.created_at.strftime('%I:%M %p').lstrip('0')}"
        )

    @property
    def time_left_label(self) -> str:
        if self.deadline_at is None:
            return "No deadline"

        return format_time_delta(self.deadline_at, expired_label="Expired")

    @property
    def auction_time_left_label(self) -> str:
        if self.listing_type != "auction" or self.auction_ends_at is None:
            return ""

        return format_time_delta(self.auction_ends_at, expired_label="Ended")

    @property
    def deadline_form_value(self) -> str:
        return datetime_local_value(self.deadline_at)

    @property
    def auction_ends_form_value(self) -> str:
        return datetime_local_value(self.auction_ends_at)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "photo_paths": self.photo_paths,
            "created_at": self.created_at.isoformat(),
            "deadline_at": self.deadline_at.isoformat() if self.deadline_at else None,
            "auction_ends_at": self.auction_ends_at.isoformat() if self.auction_ends_at else None,
            "sold_at": self.sold_at.isoformat() if self.sold_at else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
            "status": self.status,
            "previous_status": self.previous_status,
            "listing_type": self.listing_type,
            "sold_price": self.sold_price,
            "notes": self.notes,
            "watch_count": self.watch_count,
            "response_count": self.response_count,
            "source_folder": self.source_folder,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ListingItem":
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            description=data.get("description", ""),
            price=data.get("price", ""),
            photo_paths=list(data.get("photo_paths", [])),
            created_at=parse_datetime(data.get("created_at")) or utc_now(),
            deadline_at=parse_datetime(data.get("deadline_at")),
            auction_ends_at=parse_datetime(data.get("auction_ends_at")),
            sold_at=parse_datetime(data.get("sold_at")),
            archived_at=parse_datetime(data.get("archived_at")),
            status=data.get("status", "drafting"),
            previous_status=data.get("previous_status", ""),
            listing_type=data.get("listing_type", "fixed_price"),
            sold_price=data.get("sold_price", ""),
            notes=data.get("notes", ""),
            watch_count=int(data.get("watch_count", 0)),
            response_count=int(data.get("response_count", 0)),
            source_folder=data.get("source_folder"),
        )


def datetime_local_value(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.strftime("%Y-%m-%dT%H:%M")


def format_time_delta(target: datetime, expired_label: str) -> str:
    delta = target - utc_now()
    if delta.total_seconds() <= 0:
        return expired_label

    days = delta.days
    hours = delta.seconds // 3600
    if days:
        return f"{days}d {hours}h"
    return f"{hours}h"
