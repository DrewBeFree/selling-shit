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

## 2026-06-23 (flatten Python app files)

**What we did:**
- Moved the Flask app and helper modules out of the `selling_shit` package folder into the repo root.
- Renamed the Flask entrypoint from `selling_shit:app` to `app:app`, because the repo folder name `selling-shit` cannot be imported as a Python module.
- Moved `templates/` and `static/` to the repo root and removed the leftover generated `selling_shit` directory.
- Updated tests and docs for the flat layout.

**Where we stopped:**
- The repo root is `G:\apps\selling-shit`.
- The app entry command is now `python -m flask --app app:app --debug run --host=127.0.0.1 --port=5001`.
- Fresh verification passed: `pytest -q` reported `16 passed`.

**Next up:**
- Continue feature work against root files such as `app.py`, `models.py`, `photos.py`, `templates/home.html`, and `static/style.css`.

## 2026-06-23 (listing summary and marketplace badges)

**What we did:**
- Added listing value summary metrics for live value, sold value, and time since the oldest live listing.
- Added item fields for sold price/date, listing type, and auction end time.
- Added eBay auction time remaining to the eBay draft card when an item is marked as an auction.
- Added marketplace icon badges for Nextdoor, eBay, and Facebook Marketplace draft cards.
- Updated tests for the summary calculations, auction time labels, and dashboard rendering.

**Where we stopped:**
- The repo is clean on branch `dev` after the feature commit.
- Fresh verification passed: `pytest -q` reported `19 passed`.
- The live page responded with HTTP 200 and showed the listing value summary plus marketplace icon badges.

**Next up:**
- Add UI controls or metadata import rules to mark an item as sold or auction-based without editing `data/catalog.json` manually.

## 2026-06-23 (compact analytics panel)

**What we did:**
- Moved `Live value` and `Sold value` into the compact top-right analytics panel with the other dashboard counters.
- Removed the global `Since listing` card because listing age only makes sense per item.
- Kept item-level `Created`, `Time left`, and eBay auction time as the places where timing context appears.

**Where we stopped:**
- The repo is clean on branch `dev` after the analytics layout commit.
- Fresh verification passed: `pytest -q` reported `19 passed`.
- The live page responded with HTTP 200, showed `analytics-panel`, and no longer rendered global `Since listing`.

**Next up:**
- Add item-level controls for sold/auction metadata so those analytics can be edited from the UI.

## 2026-06-23 (archive workflow)

**What we did:**
- Added archive state to listing items with `archived_at` and `previous_status`.
- Added storage methods to archive and restore items while hiding archived items from the main dashboard and summary.
- Added `POST /items/<id>/archive`, `POST /items/<id>/restore`, and `GET /archive`.
- Added archive buttons to dashboard cards and a dedicated archive page with restore actions.
- Updated tests for archive/restore storage behavior and route behavior.

**Where we stopped:**
- The repo is clean on branch `dev` after the archive feature commit.
- Fresh verification passed: `pytest -q` reported `22 passed`.
- The live dashboard and `/archive` page both returned HTTP 200.

**Next up:**
- Add item-level edit controls for sold state, auction metadata, and archived item notes.

## 2026-06-23 (GitHub and Atlas publish)

**What we did:**
- Created the public GitHub repo `DrewBeFree/selling-shit`.
- Pushed both `dev` and `main`, set `main` as the default branch, and set the repo homepage to `https://sell.drewbefree.com`.
- Added Gunicorn plus `deploy/selling-shit.service` so the Flask app can run as a user-level Atlas service.
- Installed requirements on Atlas, enabled `selling-shit.service`, and verified Gunicorn returns HTTP 200 on `127.0.0.1:5055`.
- Added `sell.drewbefree.com` to the Atlas `cloudflared` ingress config and restarted the active tunnel service.
- Added a README with local development, catalog intake, and Atlas deployment notes.

**Where we stopped:**
- The repo is clean on branch `dev`; `main`, `dev`, and both remotes point at `bba637a`.
- Local verification passed: `pytest -q` reported `22 passed`.
- Atlas verification passed: `selling-shit.service` and `cloudflared.service` are active, and `curl http://127.0.0.1:5055/` returns HTTP 200.
- `sell.drewbefree.com` is still NXDOMAIN because the available `cloudflared` cert created the wrong Kybernet-zone record instead of a DrewBeFree-zone DNS record.

**Next up:**
- In Cloudflare DNS for `drewbefree.com`, create a proxied CNAME/Tunnel record: `sell` -> `188e5c59-c931-49a2-84c9-6646aadcd3c9.cfargotunnel.com`.
- Add `sell.drewbefree.com` to the Drew-only Cloudflare Access app before use.
- Delete the accidental Kybernet-zone DNS record `sell.drewbefree.com.kybernet.tech`.

## 2026-06-23 (sell domain live)

**What we did:**
- Verified `sell.drewbefree.com` now resolves through Cloudflare.
- Verified `https://sell.drewbefree.com/` returns HTTP 200.
- Rechecked Atlas service health: `selling-shit.service` and `cloudflared.service` are active, and the local Gunicorn endpoint still returns HTTP 200.

**Where we stopped:**
- The public hostname is live at `https://sell.drewbefree.com/`.
- The app is served from Atlas via the existing Cloudflare tunnel.

**Next up:**
- Confirm whether `sell.drewbefree.com` should stay behind Drew-only Cloudflare Access or be public.
- Delete the accidental Kybernet-zone DNS record `sell.drewbefree.com.kybernet.tech` if it still exists.

## 2026-06-23 (catalogue folder lifecycle)

**What we did:**
- Changed the app's default local media layout to `catalogue/inbox`, `catalogue/active`, and `catalogue/archive`.
- Fixed the flattened app base path so default data/media now lives under the repo instead of one level up in `G:\apps`.
- Updated scans so imported item folders move from `catalogue/inbox` into `catalogue/active`.
- Updated uploads so new drag/drop listings save under `catalogue/active`.
- Updated archive/restore routes so item folders physically move between `catalogue/active` and `catalogue/archive`, with photo paths rewritten.
- Added a visible `Sold` analytics card and changed sold count/value to include archived sold items.
- Migrated the existing local catalog/media into `G:\apps\selling-shit\catalogue` non-destructively.

**Where we stopped:**
- The repo is clean on branch `dev`; `main`, `dev`, and both remotes point at `188a11e`.
- Fresh verification passed: `pytest -q` reported `25 passed`.
- Local Flask at `http://127.0.0.1:5001/` and hosted `https://sell.drewbefree.com/` both returned HTTP 200 and rendered the new Sold/catalogue UI.
- Atlas `selling-shit.service` was restarted and returned HTTP 200 through Gunicorn.

**Next up:**
- Decide whether to delete the old fallback local folders `G:\apps\data`, `G:\apps\uploads`, `G:\apps\catalog_inbox`, `G:\apps\selling-shit\uploads`, and `G:\apps\selling-shit\catalog_inbox` after a quick visual check.

## 2026-06-23 (carousel preview interaction)

**What we did:**
- Changed carousel thumbnail hover/focus so it only updates the main image pane.
- Changed the main image pane click so it opens the larger image preview modal.
- Changed preview modal behavior so clicking outside the modal content closes it.
- Added a stronger dimmed backdrop for the image preview modal.
- Added a regression test covering the new preview hooks and removal of hover-to-modal behavior.

**Where we stopped:**
- The interaction fix is committed and pushed to both `dev` and `main` at `5c2edb8`.
- Atlas `selling-shit.service` was restarted after the push.

**Next up:**
- Do a visual click-through in the browser if further polish is needed on the preview modal size or backdrop feel.

## 2026-06-23 (version footer)

**What we did:**
- Added app metadata constants for `APP_VERSION = "0.2.0"` and copyright year `2026`.
- Added a shared footer to dashboard and archive pages showing `Selling Shit v0.2.0` and `© 2026 DrewBeFree`.
- Styled the footer as a compact, muted utility row.
- Added a regression test proving both pages render the version and copyright footer.

**Where we stopped:**
- The version footer is committed and pushed to both `dev` and `main` at `dad94c5`.
- Atlas `selling-shit.service` was restarted after the push.

**Next up:**
- Bump `APP_VERSION` for future user-visible changes in the `0.2.x` series.

## 2026-06-23 (footer copyright polish)

**What we did:**
- Updated the footer copyright from `DrewBeFree` to `Andrew Webb`.
- Bumped the app version from `0.2.0` to `0.2.1`.
- Added more top and bottom spacing so the footer reads as a real footer rather than tight metadata.
- Updated the footer regression test for the new version/name.

**Where we stopped:**
- The footer polish is committed and pushed to both `dev` and `main` at `d886370`.
- Atlas `selling-shit.service` was restarted after the push.

**Next up:**
- Continue bumping `APP_VERSION` within `0.2.x` for future small visible changes.

## 2026-06-23 (handoff checkpoint)

**What we did:**
- Added `HANDOFF.md` with the current repo state, run commands, app layout, recent changes, verification status, and known follow-ups.
- Confirmed `dev`, `main`, `origin/dev`, and `origin/main` were synced before the handoff update.

**Where we stopped:**
- Current app version is `v0.2.1`.
- Local URL is `http://127.0.0.1:5001/`.
- Hosted URL is `https://sell.drewbefree.com/`.
- Atlas service is `selling-shit.service`.

**Next up:**
- Start the next session by reading `HANDOFF.md`, this `SESSION_LOG.md`, and `~/.Codex/projects/selling-shit/memory/session_log.md`.

## 2026-06-23 (revert duplicate metrics dashboard)

**What we did:**
- Reverted the duplicate Grafana-style metrics dashboard and `v0.2.2` version bump.
- Kept the fresh empty catalogue data state from the test cleanup.
- Added Hermes kanban task `t_866ef6cf` on the `default` board in triage for a future, non-duplicative metrics pass.
- Updated `HANDOFF.md` with the empty catalogue note and Hermes card reference.

**Where we stopped:**
- App code is back to `v0.2.1`; the duplicate `ops-dashboard` block is gone.
- `pytest -q` passed with `27 passed`.
- Local `http://127.0.0.1:5001/` returned HTTP 200, rendered `v0.2.1`, did not render `ops-dashboard`, and showed the empty catalogue state.

**Next up:**
- Push the revert/log commits through `main` and restart Atlas if not already done.
