from pathlib import Path

from PIL import Image

from models import ListingItem
from photos import select_featured_photo_indices


def _write_image(path: Path, size: tuple[int, int], color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path)


def test_select_featured_photo_indices_picks_best_four_and_skips_tiny(tmp_path):
    photo_specs = [
        ("uploads/item/tiny.jpg", (120, 120), (120, 120, 120)),
        ("uploads/item/front.jpg", (1200, 1600), (235, 235, 235)),
        ("uploads/item/back.jpg", (1400, 1400), (215, 215, 215)),
        ("uploads/item/side.jpg", (1600, 1200), (200, 200, 200)),
        ("uploads/item/angle.jpg", (1300, 1500), (225, 225, 225)),
    ]
    for relative_path, size, color in photo_specs:
        _write_image(tmp_path / relative_path, size, color)

    item = ListingItem(
        id="item",
        title="Controller",
        description="",
        price="",
        photo_paths=[relative_path for relative_path, _, _ in photo_specs],
    )

    selected = select_featured_photo_indices(item, tmp_path, limit=4)

    assert len(selected) == 4
    assert 0 not in selected
    assert set(selected) == {1, 2, 3, 4}


def test_select_featured_photo_indices_falls_back_to_first_four_when_files_missing(tmp_path):
    item = ListingItem(
        id="item",
        title="Controller",
        description="",
        price="",
        photo_paths=[
            "uploads/item/one.jpg",
            "uploads/item/two.jpg",
            "uploads/item/three.jpg",
            "uploads/item/four.jpg",
            "uploads/item/five.jpg",
        ],
    )

    assert select_featured_photo_indices(item, tmp_path, limit=4) == [0, 1, 2, 3]
