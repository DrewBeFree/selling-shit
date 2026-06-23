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
    status: str = "drafting"
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

        delta = self.deadline_at - utc_now()
        if delta.total_seconds() <= 0:
            return "Expired"

        days = delta.days
        hours = delta.seconds // 3600
        if days:
            return f"{days}d {hours}h"
        return f"{hours}h"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "photo_paths": self.photo_paths,
            "created_at": self.created_at.isoformat(),
            "deadline_at": self.deadline_at.isoformat() if self.deadline_at else None,
            "status": self.status,
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
            status=data.get("status", "drafting"),
            watch_count=int(data.get("watch_count", 0)),
            response_count=int(data.get("response_count", 0)),
            source_folder=data.get("source_folder"),
        )
