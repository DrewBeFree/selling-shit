from selling_shit.scanner import scan_catalog_folder
from selling_shit.storage import CatalogStore


def test_scan_catalog_folder_imports_item_folder_with_description(tmp_path):
    inbox = tmp_path / "catalog_inbox"
    item_folder = inbox / "oak-desk"
    item_folder.mkdir(parents=True)
    (item_folder / "description.txt").write_text(
        "Oak desk\nSolid desk with scratches.\n125\n",
        encoding="utf-8",
    )
    (item_folder / "desk.jpg").write_bytes(b"photo")

    store = CatalogStore(tmp_path / "catalog.json")
    imported = scan_catalog_folder(inbox, tmp_path / "uploads", store)

    items = store.list_items()
    assert len(imported) == 1
    assert items[0].title == "Oak desk"
    assert items[0].description == "Solid desk with scratches."
    assert items[0].price == "125"
    assert len(items[0].photo_paths) == 1
    assert (tmp_path / items[0].photo_paths[0]).read_bytes() == b"photo"


def test_scan_catalog_folder_skips_already_imported_folder(tmp_path):
    inbox = tmp_path / "catalog_inbox"
    item_folder = inbox / "lamp"
    item_folder.mkdir(parents=True)
    (item_folder / "lamp.png").write_bytes(b"photo")

    store = CatalogStore(tmp_path / "catalog.json")
    first = scan_catalog_folder(inbox, tmp_path / "uploads", store)
    second = scan_catalog_folder(inbox, tmp_path / "uploads", store)

    assert len(first) == 1
    assert second == []
    assert len(store.list_items()) == 1


def test_scan_catalog_folder_normalizes_folder_title(tmp_path):
    inbox = tmp_path / "catalog_inbox"
    item_folder = inbox / "Nintendo Switch - Zelda Controller"
    item_folder.mkdir(parents=True)
    (item_folder / "controller.jpg").write_bytes(b"photo")

    store = CatalogStore(tmp_path / "catalog.json")
    scan_catalog_folder(inbox, tmp_path / "uploads", store)

    assert store.list_items()[0].title == "Nintendo Switch Zelda Controller"


def test_scan_catalog_folder_sanitizes_copied_image_names(tmp_path):
    inbox = tmp_path / "catalog_inbox"
    item_folder = inbox / "controller"
    item_folder.mkdir(parents=True)
    (item_folder / "Nintendo Switch - {Date (YYYY)»}-10.JPG").write_bytes(b"photo")

    store = CatalogStore(tmp_path / "catalog.json")
    scan_catalog_folder(inbox, tmp_path / "uploads", store)

    photo_path = store.list_items()[0].photo_paths[0]
    assert photo_path.endswith("Nintendo_Switch_-_Date_YYYY-10.JPG")
    assert "{" not in photo_path
    assert "»" not in photo_path
    assert (tmp_path / photo_path).read_bytes() == b"photo"
