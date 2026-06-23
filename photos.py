from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageFilter, ImageStat

from models import ListingItem


def select_featured_photo_indices(
    item: ListingItem,
    base_dir: str | Path,
    limit: int = 4,
) -> list[int]:
    if not item.photo_paths:
        return []

    base_path = Path(base_dir)
    scored: list[tuple[float, int]] = []
    for index, photo_path in enumerate(item.photo_paths):
        path = base_path / photo_path
        try:
            stat = path.stat()
        except OSError:
            score = None
        else:
            score = _score_photo_cached(str(path), stat.st_mtime_ns, stat.st_size)
        if score is not None:
            scored.append((score, index))

    if not scored:
        return list(range(min(limit, len(item.photo_paths))))

    scored.sort(key=lambda entry: entry[0], reverse=True)
    return [index for _, index in scored[:limit]]


@lru_cache(maxsize=512)
def _score_photo_cached(path: str, mtime_ns: int, size: int) -> float | None:
    return _score_photo(Path(path))


def _score_photo(path: Path) -> float | None:
    try:
        with Image.open(path) as image:
            width, height = image.size
            if width <= 0 or height <= 0:
                return None

            area_score = min((width * height) / 1_800_000, 1.6)
            aspect_ratio = max(width, height) / max(min(width, height), 1)
            aspect_score = max(0.0, 1.2 - abs(aspect_ratio - 1.25) * 0.28)

            image.draft("RGB", (96, 96))
            sample = image.convert("RGB")
            sample.thumbnail((96, 96))
            stat = ImageStat.Stat(sample)
            brightness = sum(stat.mean) / 3
            brightness_score = max(0.0, 1.0 - abs(brightness - 200) / 200)
            contrast_score = min(sum(stat.stddev) / 3 / 70, 1.0)

            edges = sample.filter(ImageFilter.FIND_EDGES)
            sharpness_score = min(sum(ImageStat.Stat(edges).mean) / 3 / 24, 1.0)

            return (
                area_score * 4
                + aspect_score * 1.4
                + brightness_score
                + contrast_score * 0.8
                + sharpness_score * 0.8
            )
    except OSError:
        return None
