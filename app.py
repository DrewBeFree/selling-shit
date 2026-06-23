from __future__ import annotations

import shutil
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from drafts import generate_platform_drafts
from photos import select_featured_photo_indices
from scanner import scan_catalog_folder
from storage import CatalogStore

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_CATALOGUE_DIR = BASE_DIR / "catalogue"
DEFAULT_CATALOG_INBOX = DEFAULT_CATALOGUE_DIR / "inbox"
DEFAULT_CATALOG_ACTIVE = DEFAULT_CATALOGUE_DIR / "active"
DEFAULT_CATALOG_ARCHIVE = DEFAULT_CATALOGUE_DIR / "archive"
DEFAULT_LEGACY_UPLOAD_DIR = BASE_DIR / "uploads"
APP_VERSION = "0.2.0"
COPYRIGHT_YEAR = 2026

app = Flask(__name__)
app.config.update(
    UPLOAD_FOLDER=str(DEFAULT_CATALOG_ACTIVE),
    CATALOG_PATH=str(DEFAULT_DATA_DIR / "catalog.json"),
    CATALOG_INBOX=str(DEFAULT_CATALOG_INBOX),
    CATALOG_ACTIVE=str(DEFAULT_CATALOG_ACTIVE),
    CATALOG_ARCHIVE=str(DEFAULT_CATALOG_ARCHIVE),
)


@app.context_processor
def app_metadata():
    return {
        "app_version": APP_VERSION,
        "copyright_year": COPYRIGHT_YEAR,
    }


@app.route("/", methods=["GET"])
def home():
    return _render_dashboard()


@app.route("/archive", methods=["GET"])
def archive():
    store = _store()
    archived_items = store.list_archived_items()
    featured_photos = {
        item.id: select_featured_photo_indices(item, _media_base_dir())
        for item in archived_items
    }
    return render_template(
        "archive.html",
        items=archived_items,
        featured_photos=featured_photos,
    )


@app.route("/items", methods=["POST"])
def create_item():
    store = _store()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    price = request.form.get("price", "").strip()
    files = [file for file in request.files.getlist("images") if file and file.filename]

    if not title and files:
        title = Path(files[0].filename).stem.replace("-", " ").replace("_", " ").title()

    item = store.add_item(
        title=title or "Untitled item",
        description=description,
        price=price,
        photo_paths=[],
    )
    item_upload_dir = _catalog_active() / item.id
    item_upload_dir.mkdir(parents=True, exist_ok=True)

    item.photo_paths = []
    for uploaded_file in files:
        filename = secure_filename(uploaded_file.filename)
        if not filename:
            continue
        destination = item_upload_dir / filename
        uploaded_file.save(destination)
        item.photo_paths.append(str(destination.relative_to(_media_base_dir())).replace("\\", "/"))
    item.source_folder = str(item_upload_dir.resolve())

    store.upsert_item(item)
    return _render_dashboard(active_item_id=item.id)


@app.route("/scan", methods=["POST"])
def scan_catalog():
    scan_catalog_folder(_catalog_inbox(), _catalog_active(), _store())
    return _render_dashboard()


@app.route("/items/<item_id>/archive", methods=["POST"])
def archive_item(item_id: str):
    store = _store()
    item = store.archive_item(item_id)
    if item is None:
        abort(404)
    _move_item_folder(item, _catalog_active(), _catalog_archive(), "catalogue/archive")
    store.upsert_item(item)
    return redirect(url_for("home"))


@app.route("/items/<item_id>/restore", methods=["POST"])
def restore_item(item_id: str):
    store = _store()
    item = store.restore_item(item_id)
    if item is None:
        abort(404)
    _move_item_folder(item, _catalog_archive(), _catalog_active(), "catalogue/active")
    store.upsert_item(item)
    return redirect(url_for("archive"))


@app.route("/uploads/<item_id>/<filename>")
def uploaded_file(item_id: str, filename: str):
    item_folder = secure_filename(item_id)
    for root in (_catalog_active(), Path(app.config["UPLOAD_FOLDER"]), _legacy_upload_dir()):
        candidate = root / item_folder / filename
        if candidate.exists():
            return send_from_directory(candidate.parent, candidate.name)
    abort(404)


@app.route("/items/<item_id>/photos/<int:photo_index>")
def item_photo(item_id: str, photo_index: int):
    item = _store().get_item(item_id)
    if item is None or photo_index < 0 or photo_index >= len(item.photo_paths):
        abort(404)

    photo_path = (_media_base_dir() / item.photo_paths[photo_index]).resolve()
    allowed_roots = [
        _catalogue_dir().resolve(),
        Path(app.config["UPLOAD_FOLDER"]).resolve(),
        _legacy_upload_dir().resolve(),
    ]
    if not any(root == photo_path or root in photo_path.parents for root in allowed_roots):
        abort(404)

    return send_from_directory(photo_path.parent, photo_path.name)


def _store() -> CatalogStore:
    return CatalogStore(app.config["CATALOG_PATH"])


def _upload_dir() -> Path:
    path = _catalog_active()
    path.mkdir(parents=True, exist_ok=True)
    return path


def _catalogue_dir() -> Path:
    configured = app.config.get("CATALOGUE_FOLDER")
    if configured:
        path = Path(configured)
    else:
        active = Path(app.config.get("CATALOG_ACTIVE", DEFAULT_CATALOG_ACTIVE))
        path = active.parent
    path.mkdir(parents=True, exist_ok=True)
    return path


def _catalog_inbox() -> Path:
    path = Path(app.config.get("CATALOG_INBOX", _catalogue_dir() / "inbox"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _catalog_active() -> Path:
    path = Path(app.config.get("CATALOG_ACTIVE", _catalogue_dir() / "active"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _catalog_archive() -> Path:
    path = Path(app.config.get("CATALOG_ARCHIVE", _catalogue_dir() / "archive"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _legacy_upload_dir() -> Path:
    return Path(app.config.get("LEGACY_UPLOAD_FOLDER", DEFAULT_LEGACY_UPLOAD_DIR))


def _media_base_dir() -> Path:
    return _catalogue_dir().parent


def _move_item_folder(item, source_root: Path, destination_root: Path, destination_prefix: str) -> None:
    source = source_root / item.id
    if not source.exists():
        source = _legacy_upload_dir() / item.id
    destination = destination_root / item.id

    if source.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(source), str(destination))

    item.photo_paths = [
        _move_photo_path(photo_path, item.id, destination_prefix)
        for photo_path in item.photo_paths
    ]
    item.source_folder = str(destination.resolve())


def _move_photo_path(photo_path: str, item_id: str, destination_prefix: str) -> str:
    filename = Path(photo_path).name
    return f"{destination_prefix}/{item_id}/{filename}"


def _render_dashboard(active_item_id: str | None = None):
    store = _store()
    items = store.list_items()
    platform_drafts = {item.id: generate_platform_drafts(item) for item in items}
    featured_photos = {
        item.id: select_featured_photo_indices(item, _media_base_dir())
        for item in items
    }
    return render_template(
        "home.html",
        items=items,
        platform_drafts=platform_drafts,
        featured_photos=featured_photos,
        summary=store.summary(),
        platforms=["Nextdoor", "eBay", "Facebook Marketplace"],
        catalog_inbox=_catalog_inbox(),
        active_item_id=active_item_id,
    )


def reset_local_catalog() -> None:
    data_path = Path(app.config["CATALOG_PATH"])
    catalogue_path = _catalogue_dir()
    if data_path.exists():
        data_path.unlink()
    if catalogue_path.exists():
        shutil.rmtree(catalogue_path)
