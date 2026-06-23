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
