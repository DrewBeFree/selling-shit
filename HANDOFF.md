# Selling Shit Handoff

## Current State

- Repo: `G:\apps\selling-shit`
- GitHub: `https://github.com/DrewBeFree/selling-shit`
- Branches: `dev` and `main` are synced.
- Hosted app: `https://sell.drewbefree.com/`
- Local app: `http://127.0.0.1:5001/`
- Current version: `v0.2.1`
- Footer: `Selling Shit v0.2.1` and `© 2026 Andrew Webb`
- Current local catalogue data is intentionally empty after test item cleanup.

## Run Commands

Local development:

```powershell
$venv = Join-Path $env:TEMP 'selling-shit-publish-venv'
& "$venv\Scripts\python.exe" -m flask --app app:app --debug run --host=127.0.0.1 --port=5001
```

Tests:

```powershell
$venv = Join-Path $env:TEMP 'selling-shit-publish-venv'
& "$venv\Scripts\python.exe" -m pytest -q
```

Atlas service:

```bash
systemctl --user restart selling-shit.service
systemctl --user status selling-shit.service --no-pager
```

## App Layout

- `catalogue/inbox/` - folders waiting to be scanned.
- `catalogue/active/` - current active item folders and drag/drop uploads.
- `catalogue/archive/` - archived item folders.
- `data/catalog.json` - local JSON catalog, ignored by Git.
- `app.py` - Flask routes, app metadata, and media movement helpers.
- `scanner.py` - imports folder contents from inbox to active.
- `storage.py` - JSON persistence, summary metrics, archive/restore state.
- `templates/home.html` - dashboard UI, carousel, drafts, footer.
- `templates/archive.html` - archive UI and footer.
- `static/style.css` - app styling.

## Recent Changes

- Published repo to GitHub and deployed to Atlas through Cloudflare Tunnel.
- Added `sell.drewbefree.com`.
- Flattened app files to the repo root with Flask entrypoint `app:app`.
- Added marketplace draft cards for Nextdoor, eBay, and Facebook Marketplace.
- Added photo carousel with thumbnail hover updating the main image and main-image click opening a dimmed modal.
- Added archive/restore workflow and archive page.
- Added all-time sold count/value across active and archived sold listings.
- Added `catalogue/inbox`, `catalogue/active`, and `catalogue/archive` folder lifecycle.
- Added footer/versioning, currently `v0.2.1`.
- Reverted the duplicate metrics dashboard idea and moved it to Hermes kanban task `t_866ef6cf`.

## Known Follow-Ups

- Decide whether to delete old fallback local folders after visual confirmation:
  - `G:\apps\data`
  - `G:\apps\uploads`
  - `G:\apps\catalog_inbox`
  - `G:\apps\selling-shit\uploads`
  - `G:\apps\selling-shit\catalog_inbox`
- Delete accidental Kybernet-zone DNS record `sell.drewbefree.com.kybernet.tech` if it still exists.
- Decide whether `sell.drewbefree.com` should stay behind Drew-only Cloudflare Access or be public.
- Add UI controls for sold state, sold price, auction metadata, deadlines, and listing notes.
- Hermes kanban `default` board task `t_866ef6cf`: rethink useful listing metrics only if they add new value beyond the existing summary cards.
- Replace local photo-quality heuristic and draft text generation with real AI/Atlas assistance.
- Bump `APP_VERSION` within `0.2.x` for future small visible changes.

## Verification At Last Handoff

- `pytest -q` passed with `27 passed`.
- `http://127.0.0.1:5001/` rendered `v0.2.1` and `Andrew Webb`.
- `https://sell.drewbefree.com/` rendered `v0.2.1` and `Andrew Webb`.
- Atlas `selling-shit.service` was active and returned HTTP 200 through Gunicorn.
