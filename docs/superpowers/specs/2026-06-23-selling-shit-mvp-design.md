# Selling Shit MVP Design

## Goal

Build a local Flask web app under `apps\selling-shit` for turning item photos and short descriptions into marketplace-ready draft listings. The MVP should feel like an operational dashboard: drag in photos, add the description in a modal, scan a local catalog folder, and see each item with status indicators, timing, and platform-specific drafts.

## Scope

The MVP does not post to Nextdoor, eBay, or Facebook Marketplace APIs. It prepares clean drafts for each platform and tracks workflow state locally. This keeps the app useful immediately while leaving real API posting for a later integration.

## Architecture

The app stays intentionally small and file-backed:

- `selling_shit/models.py` defines item and draft dataclasses.
- `selling_shit/storage.py` owns JSON persistence in `data/catalog.json`.
- `selling_shit/drafts.py` creates platform-specific drafts for Nextdoor, eBay, and Facebook Marketplace.
- `selling_shit/scanner.py` imports folders from `catalog_inbox/`, using photos plus optional `description.txt`.
- `selling_shit/__init__.py` wires Flask routes and upload handling.
- `selling_shit/templates/home.html` and `selling_shit/static/style.css` provide the dashboard UI.

## User Experience

The first screen is the app itself, not a landing page. It opens with a drag/drop intake zone and a catalogue scan action. Dropping a photo opens a description modal; submitting the modal creates an item and platform drafts.

Items appear as grey cards with fresh orange borders and a restrained 3D effect. Each card shows title, description, photos, created time, time left, watch count, response count, workflow state, and platform drafts.

## Platform Draft Rules

- Nextdoor: friendly local title, neighborhood pickup language, shorter body, category hint, price.
- eBay: search-friendly title, condition field, shipping/local pickup note, item specifics, price.
- Facebook Marketplace: casual title, concise body, category, condition, pickup message, price.

## Local Data Rules

- Uploaded images are stored in `uploads/<item-id>/`.
- Scanned folder images are copied into `uploads/<item-id>/`.
- Local catalog state is stored in `data/catalog.json`.
- `uploads/`, `data/`, and `catalog_inbox/` are ignored by Git.

## Testing

Tests cover draft generation, catalog persistence, folder scanning, upload intake, and dashboard rendering. The app should run with `python -m flask --app selling_shit:app --debug run --host=127.0.0.1 --port=5001`.
