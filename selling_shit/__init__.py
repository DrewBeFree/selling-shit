from __future__ import annotations

import shutil
from pathlib import Path

from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from .drafts import generate_platform_drafts
from .scanner import scan_catalog_folder
from .storage import CatalogStore

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_UPLOAD_DIR = BASE_DIR / "uploads"
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_CATALOG_INBOX = BASE_DIR / "catalog_inbox"

app = Flask(__name__)
app.config.update(
    UPLOAD_FOLDER=str(DEFAULT_UPLOAD_DIR),
    CATALOG_PATH=str(DEFAULT_DATA_DIR / "catalog.json"),
    CATALOG_INBOX=str(DEFAULT_CATALOG_INBOX),
)


@app.route("/", methods=["GET"])
def home():
    return _render_dashboard()


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
    item_upload_dir = _upload_dir() / item.id
    item_upload_dir.mkdir(parents=True, exist_ok=True)

    item.photo_paths = []
    for uploaded_file in files:
        filename = secure_filename(uploaded_file.filename)
        if not filename:
            continue
        destination = item_upload_dir / filename
        uploaded_file.save(destination)
        item.photo_paths.append(str(destination.relative_to(_upload_dir().parent)).replace("\\", "/"))

    store.upsert_item(item)
    return _render_dashboard(active_item_id=item.id)


@app.route("/scan", methods=["POST"])
def scan_catalog():
    scan_catalog_folder(_catalog_inbox(), _upload_dir(), _store())
    return _render_dashboard()


@app.route("/uploads/<item_id>/<filename>")
def uploaded_file(item_id: str, filename: str):
    return send_from_directory(_upload_dir() / secure_filename(item_id), secure_filename(filename))


def _store() -> CatalogStore:
    return CatalogStore(app.config["CATALOG_PATH"])


def _upload_dir() -> Path:
    path = Path(app.config["UPLOAD_FOLDER"])
    path.mkdir(parents=True, exist_ok=True)
    return path


def _catalog_inbox() -> Path:
    path = Path(app.config["CATALOG_INBOX"])
    path.mkdir(parents=True, exist_ok=True)
    return path


def _render_dashboard(active_item_id: str | None = None):
    store = _store()
    items = store.list_items()
    platform_drafts = {item.id: generate_platform_drafts(item) for item in items}
    return render_template(
        "home.html",
        items=items,
        platform_drafts=platform_drafts,
        summary=store.summary(),
        platforms=["Nextdoor", "eBay", "Facebook Marketplace"],
        catalog_inbox=_catalog_inbox(),
        active_item_id=active_item_id,
    )


def reset_local_catalog() -> None:
    data_path = Path(app.config["CATALOG_PATH"])
    upload_path = _upload_dir()
    if data_path.exists():
        data_path.unlink()
    if upload_path.exists():
        shutil.rmtree(upload_path)
