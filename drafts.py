from __future__ import annotations

from models import ListingItem, PlatformDraft


def _price_text(item: ListingItem) -> str:
    return f"${item.price}" if item.price else "Price TBD"


def generate_platform_drafts(item: ListingItem) -> list[PlatformDraft]:
    price = _price_text(item)
    title = item.title or "Untitled item"
    description = item.description or "Description needed."

    return [
        PlatformDraft(
            platform="Nextdoor",
            title=f"{title} available nearby",
            body=(
                f"Hi neighbors, I am selling {title} for {price}. "
                f"{description} Local pickup preferred. Message me with questions."
            ),
            fields={
                "category": "For Sale & Free",
                "price": price,
                "pickup": "Local pickup",
            },
        ),
        PlatformDraft(
            platform="eBay",
            title=f"{title} - used - local pickup available",
            body=(
                f"{description}\n\n"
                "Item specifics: used condition, photos show the actual item, "
                "buyer should review all images before purchase.\n\n"
                "Fulfillment: local pickup or shipping quote by request."
            ),
            fields={
                "category": "General merchandise",
                "condition": "Used",
                "price": price,
                "fulfillment": "Local pickup / shipping quote",
            },
        ),
        PlatformDraft(
            platform="Facebook Marketplace",
            title=title,
            body=(
                f"{description}\n\n"
                f"Asking {price}. Pickup available. Send a message if interested."
            ),
            fields={
                "category": "Miscellaneous",
                "condition": "Used - good",
                "price": price,
                "fulfillment": "Pickup available",
            },
        ),
    ]
