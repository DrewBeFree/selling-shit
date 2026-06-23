from datetime import datetime, timedelta, timezone

from drafts import generate_platform_drafts
from models import ListingItem
from storage import CatalogStore


def test_generate_platform_drafts_have_marketplace_specific_fields():
    item = ListingItem(
        id="item-1",
        title="Oak desk",
        description="Solid oak desk with a drawer and light scratches.",
        price="125",
        photo_paths=["uploads/item-1/desk.jpg"],
        created_at=datetime(2026, 6, 23, 12, 0, tzinfo=timezone.utc),
    )

    drafts = generate_platform_drafts(item)

    assert {draft.platform for draft in drafts} == {
        "Nextdoor",
        "eBay",
        "Facebook Marketplace",
    }
    ebay = next(draft for draft in drafts if draft.platform == "eBay")
    nextdoor = next(draft for draft in drafts if draft.platform == "Nextdoor")
    facebook = next(draft for draft in drafts if draft.platform == "Facebook Marketplace")

    assert ebay.fields["condition"] == "Used"
    assert "Item specifics" in ebay.body
    assert "neighbors" in nextdoor.body
    assert "Pickup" in facebook.fields["fulfillment"]


def test_catalog_store_persists_items_with_metrics(tmp_path):
    store = CatalogStore(tmp_path / "catalog.json")
    item = store.add_item(
        title="Camp chairs",
        description="Two folding chairs in good condition.",
        price="30",
        photo_paths=["uploads/camp-chairs/chair.jpg"],
        status="drafting",
    )

    reloaded = CatalogStore(tmp_path / "catalog.json")
    saved_item = reloaded.list_items()[0]

    assert saved_item.id == item.id
    assert saved_item.title == "Camp chairs"
    assert saved_item.watch_count == 0
    assert saved_item.response_count == 0
    assert saved_item.status == "drafting"
    assert saved_item.time_left_label == "No deadline"


def test_catalog_store_summary_counts_statuses(tmp_path):
    store = CatalogStore(tmp_path / "catalog.json")
    store.add_item(title="Lamp", description="Working lamp", price="15", photo_paths=[])
    store.add_item(
        title="Table",
        description="Small table",
        price="40",
        photo_paths=[],
        status="ready",
    )

    summary = store.summary()

    assert summary["total"] == 2
    assert summary["drafting"] == 1
    assert summary["ready"] == 1
    assert summary["responses"] == 0


def test_catalog_store_summary_tracks_live_sold_value_and_listing_age(tmp_path):
    store = CatalogStore(tmp_path / "catalog.json")
    live_item = ListingItem(
        id="live-1",
        title="Live controller",
        description="",
        price="125.50",
        photo_paths=[],
        status="ready",
        created_at=datetime.now(timezone.utc) - timedelta(days=2, hours=3),
    )
    sold_item = ListingItem(
        id="sold-1",
        title="Sold lamp",
        description="",
        price="40",
        sold_price="35",
        photo_paths=[],
        status="sold",
        created_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    store.upsert_item(live_item)
    store.upsert_item(sold_item)

    summary = store.summary()

    assert summary["live_value"] == "$125.50"
    assert summary["sold_value"] == "$35"
    assert summary["listing_age"] == "2d 3h"


def test_listing_item_tracks_auction_time_remaining():
    item = ListingItem(
        id="auction-1",
        title="Auction controller",
        description="",
        price="15",
        photo_paths=[],
        listing_type="auction",
        auction_ends_at=datetime.now(timezone.utc) + timedelta(days=1, hours=2),
    )

    assert item.auction_time_left_label == "1d 2h"


def test_catalog_store_reads_json_with_utf8_bom(tmp_path):
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text('\ufeff{"items": []}', encoding="utf-8")

    store = CatalogStore(catalog_path)

    assert store.list_items() == []
