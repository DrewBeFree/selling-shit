## 2026-06-23 (initial Flask recovery)

**What we did:**
- Restored context from the global session log and confirmed there was no existing repo or project session log for `selling-shit`.
- Verified `G:\apps\selling-shit\selling-shit` had no commits and no app files outside the Linux `env/` virtualenv.
- Added a RED pytest baseline proving `selling_shit:app` was missing, then committed it on `dev`.
- Created the minimal Flask package, home page template, stylesheet, upload handling, `.gitignore`, and Python requirements.
- Verified with `pytest` in a local temp venv and started Flask at `http://127.0.0.1:5001/`.

**Where we stopped:**
- The repo is clean on branch `dev`; app recovery work is captured in commits `635846c` and `f68cfac`.
- Flask is running locally on port `5001` from a temp verification venv.
- No Git remote is configured for this repo.

**Next up:**
- Decide whether to keep this as the baseline app, add fuller listing-generation requirements, or configure a remote before merging/pushing.

## 2026-06-23 (marketplace drafting MVP)

**What we did:**
- Treated the user's original overnight request as the source of truth and wrote a design doc plus implementation plan under `docs/superpowers/`.
- Added tests for catalog persistence, platform-specific draft generation, folder scanning, upload intake, scan route, and dashboard rendering.
- Implemented JSON-backed catalog storage, marketplace draft generators for Nextdoor/eBay/Facebook Marketplace, and a local folder scanner for `catalog_inbox/`.
- Rebuilt the Flask dashboard with drag/drop photo intake, modal description capture, scan action, summary metrics, orange-bordered grey cards, 3D card styling, status indicators, and per-platform draft panels.
- Updated `.gitignore` so local `uploads/`, `data/`, and `catalog_inbox/` stay out of Git.

**Where we stopped:**
- The repo is clean on branch `dev`.
- Fresh verification passed: `pytest -q` reported `8 passed`.
- Flask responded with HTTP 200 at `http://127.0.0.1:5001/`.
- No Git remote is configured, so nothing was pushed.

**Next up:**
- Add real AI-assisted draft rewriting and marketplace-specific validation rules, or configure the GitHub remote and decide when to merge `dev`.

## 2026-06-23 (flatten repo folder)

**What we did:**
- Moved the Git repo root up from `G:\apps\selling-shit\selling-shit` to `G:\apps\selling-shit`.
- Kept the Python package folder as `selling_shit`, since Flask imports still use `selling_shit:app`.
- Removed the old nested `selling-shit` folder after verifying it only contained leftover Git internals.
- Restarted Flask from the new root with `--no-reload` to clear the stale deleted-path reloader process.

**Where we stopped:**
- The repo is clean on branch `dev` at `G:\apps\selling-shit`.
- Fresh verification passed: `pytest -q` reported `8 passed`.
- Flask responded with HTTP 200 at `http://127.0.0.1:5001/`.

**Next up:**
- Continue feature work from `G:\apps\selling-shit`; do not use the old nested path.

## 2026-06-23 (scanned photo preview fix)

**What we did:**
- Investigated a broken preview after scanning `catalog_inbox\Nintendo Switch - Zelda Controller`.
- Found two filename issues: scanned images kept special characters, and existing filenames included `#`, which browsers treat as a URL fragment.
- Added an indexed photo route, switched item cards to `/items/<item-id>/photos/0`, sanitized filenames for future scans, normalized folder-derived titles, and made catalog JSON reads tolerate UTF-8 BOMs.
- Updated the existing local catalog title to `Nintendo Switch Zelda Controller` without changing ignored local media into tracked files.

**Where we stopped:**
- The repo is clean on branch `dev`.
- Fresh verification passed: `pytest -q` reported `13 passed`.
- The current scanned item photo returns HTTP 200 as `image/jpeg`.

**Next up:**
- Add real description/price extraction. The current folder did not include `description.txt`, so the app can only infer the title from the folder name until AI/photo analysis or richer folder metadata is added.

## 2026-06-23 (featured photo carousel)

**What we did:**
- Added a local photo-quality selector that ranks item photos and chooses up to four featured images for display.
- Added Pillow as a dependency for lightweight image inspection, using thumbnail-sized samples and an in-process cache so large originals do not have to be fully decoded on every request.
- Replaced the single cropped item preview with an eBay-style carousel: vertical thumbnails, contained main image, and larger hover/click preview modal.
- Updated tests for photo selection and dashboard carousel rendering.

**Where we stopped:**
- The repo is clean on branch `dev` after the feature commit.
- Fresh verification passed: `pytest -q` reported `16 passed`.
- The live page responded with HTTP 200 and included the carousel plus preview modal markup.

**Next up:**
- Replace the local image-quality heuristic with real vision-assisted selection when an AI provider/key is configured.
