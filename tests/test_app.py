from io import BytesIO

from selling_shit import app


def test_home_page_loads_listing_form():
    app.config.update(TESTING=True)

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"Selling Shit" in response.data
    assert b"Drop photos here" in response.data
    assert b"Scan catalogue" in response.data
    assert b"Nextdoor" in response.data
    assert b"Facebook Marketplace" in response.data
    assert b'name="title"' in response.data
    assert b'name="images"' in response.data


def test_listing_post_renders_draft_and_saves_upload(tmp_path):
    app.config.update(
        TESTING=True,
        UPLOAD_FOLDER=str(tmp_path / "uploads"),
        CATALOG_PATH=str(tmp_path / "catalog.json"),
        CATALOG_INBOX=str(tmp_path / "catalog_inbox"),
    )
    client = app.test_client()

    response = client.post(
        "/items",
        data={
            "title": "Vintage desk",
            "description": "Solid wood, pickup only",
            "price": "75",
            "images": (BytesIO(b"fake image bytes"), "desk photo.jpg"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Vintage desk" in response.data
    assert b"Vintage desk" in response.data
    assert b"Solid wood, pickup only" in response.data
    assert b"$75" in response.data
    assert b"Watchers" in response.data
    assert b"Responses" in response.data
    assert b"Time left" in response.data
    assert b"eBay" in response.data
    assert b"/photos/0" in response.data
    saved_files = list((tmp_path / "uploads").glob("*/desk_photo.jpg"))
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == b"fake image bytes"


def test_scan_route_imports_catalog_folder(tmp_path):
    inbox = tmp_path / "catalog_inbox"
    item_folder = inbox / "bike-rack"
    item_folder.mkdir(parents=True)
    (item_folder / "description.txt").write_text(
        "Bike rack\nHitch rack for two bikes.\n60\n",
        encoding="utf-8",
    )
    (item_folder / "rack.jpg").write_bytes(b"photo")
    app.config.update(
        TESTING=True,
        UPLOAD_FOLDER=str(tmp_path / "uploads"),
        CATALOG_PATH=str(tmp_path / "catalog.json"),
        CATALOG_INBOX=str(inbox),
    )

    response = app.test_client().post("/scan")

    assert response.status_code == 200
    assert b"Bike rack" in response.data
    assert b"Hitch rack for two bikes." in response.data


def test_uploaded_file_route_serves_stored_catalog_filename(tmp_path):
    upload_dir = tmp_path / "uploads"
    item_dir = upload_dir / "item-1"
    item_dir.mkdir(parents=True)
    filename = "Nintendo Switch - {Date (YYYY)\u00bb}-10.JPG"
    (item_dir / filename).write_bytes(b"photo")
    app.config.update(
        TESTING=True,
        UPLOAD_FOLDER=str(upload_dir),
        CATALOG_PATH=str(tmp_path / "catalog.json"),
        CATALOG_INBOX=str(tmp_path / "catalog_inbox"),
    )

    response = app.test_client().get(f"/uploads/item-1/{filename}")

    assert response.status_code == 200
    assert response.data == b"photo"


def test_item_photo_route_serves_filename_with_url_fragments(tmp_path):
    upload_dir = tmp_path / "uploads"
    item_dir = upload_dir / "item-1"
    item_dir.mkdir(parents=True)
    filename = "Nintendo Switch - {Sequence # (001)\u00bb}.JPG"
    (item_dir / filename).write_bytes(b"photo")
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(
        """{
  "items": [
    {
      "id": "item-1",
      "title": "Controller",
      "description": "",
      "price": "",
      "photo_paths": ["uploads/item-1/Nintendo Switch - {Sequence # (001)\u00bb}.JPG"],
      "created_at": "2026-06-23T15:34:29+00:00",
      "deadline_at": null,
      "status": "drafting",
      "watch_count": 0,
      "response_count": 0,
      "source_folder": null
    }
  ]
}""",
        encoding="utf-8",
    )
    app.config.update(
        TESTING=True,
        UPLOAD_FOLDER=str(upload_dir),
        CATALOG_PATH=str(catalog_path),
        CATALOG_INBOX=str(tmp_path / "catalog_inbox"),
    )

    response = app.test_client().get("/items/item-1/photos/0")

    assert response.status_code == 200
    assert response.data == b"photo"


def test_dashboard_renders_featured_photo_carousel(tmp_path):
    from PIL import Image

    upload_dir = tmp_path / "uploads"
    item_dir = upload_dir / "item-1"
    item_dir.mkdir(parents=True)
    for index in range(5):
        Image.new("RGB", (900 + index * 100, 1200), (220, 220, 220)).save(
            item_dir / f"photo-{index}.jpg"
        )

    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(
        """{
  "items": [
    {
      "id": "item-1",
      "title": "Controller",
      "description": "",
      "price": "",
      "photo_paths": [
        "uploads/item-1/photo-0.jpg",
        "uploads/item-1/photo-1.jpg",
        "uploads/item-1/photo-2.jpg",
        "uploads/item-1/photo-3.jpg",
        "uploads/item-1/photo-4.jpg"
      ],
      "created_at": "2026-06-23T15:34:29+00:00",
      "deadline_at": null,
      "status": "drafting",
      "watch_count": 0,
      "response_count": 0,
      "source_folder": null
    }
  ]
}""",
        encoding="utf-8",
    )
    app.config.update(
        TESTING=True,
        UPLOAD_FOLDER=str(upload_dir),
        CATALOG_PATH=str(catalog_path),
        CATALOG_INBOX=str(tmp_path / "catalog_inbox"),
    )

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b'class="photo-carousel"' in response.data
    assert response.data.count(b'class="carousel-thumb') == 4
    assert b'id="imagePreviewModal"' in response.data
    assert b'data-photo-src="/items/item-1/photos/' in response.data
