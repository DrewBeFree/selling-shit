from io import BytesIO

from selling_shit import app


def test_home_page_loads_listing_form():
    app.config.update(TESTING=True)

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"Selling Shit" in response.data
    assert b'name="title"' in response.data
    assert b'name="images"' in response.data


def test_listing_post_renders_draft_and_saves_upload(tmp_path):
    app.config.update(TESTING=True, UPLOAD_FOLDER=str(tmp_path))
    client = app.test_client()

    response = client.post(
        "/",
        data={
            "title": "Vintage desk",
            "description": "Solid wood, pickup only",
            "price": "75",
            "images": (BytesIO(b"fake image bytes"), "desk photo.jpg"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Draft received" in response.data
    assert b"Vintage desk" in response.data
    assert b"Solid wood, pickup only" in response.data
    assert b"$75" in response.data
    assert b"desk_photo.jpg" in response.data
    assert (tmp_path / "desk_photo.jpg").read_bytes() == b"fake image bytes"
