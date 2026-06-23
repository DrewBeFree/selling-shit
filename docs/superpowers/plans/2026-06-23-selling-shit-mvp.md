# Selling Shit MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first useful local marketplace-drafting dashboard for photo intake, catalog folder scanning, item cards, and platform-specific drafts.

**Architecture:** Keep Flask as the app shell and split behavior into focused modules for models, JSON storage, draft generation, and folder scanning. Use file-backed persistence so the MVP runs locally without database setup.

**Tech Stack:** Python 3.12+/3.13, Flask 3.1.3, pytest 9.0.3, vanilla HTML/CSS/JavaScript.

## Global Constraints

- App package remains importable as `selling_shit:app`.
- The app runs on `127.0.0.1:5001` with Flask debug mode.
- Uploaded and scanned photos are local-only and ignored by Git.
- Platform drafts are generated locally and do not post to external APIs.
- UI uses grey item cards, fresh orange borders, and a subtle 3D effect.
- Git commits do not include `Co-Authored-By:` lines.

---

### Task 1: Domain Modules

**Files:**
- Create: `selling_shit/models.py`
- Create: `selling_shit/drafts.py`
- Create: `selling_shit/storage.py`
- Test: `tests/test_catalog_core.py`

**Interfaces:**
- Produces: `ListingItem`, `PlatformDraft`, `CatalogStore`, `generate_platform_drafts(item)`.

- [x] **Step 1: Write failing tests**
- [x] **Step 2: Run tests and confirm missing modules fail**
- [x] **Step 3: Implement dataclasses, draft generation, and JSON storage**
- [x] **Step 4: Run tests and confirm pass**
- [x] **Step 5: Commit**

### Task 2: Folder Scanner

**Files:**
- Create: `selling_shit/scanner.py`
- Test: `tests/test_scanner.py`

**Interfaces:**
- Consumes: `CatalogStore.add_item(...)`.
- Produces: `scan_catalog_folder(inbox_dir, uploads_dir, store)`.

- [x] **Step 1: Write failing scanner tests**
- [x] **Step 2: Run tests and confirm scanner missing/behavior fails**
- [x] **Step 3: Implement scanner for one folder per item with optional `description.txt`**
- [x] **Step 4: Run tests and confirm pass**
- [x] **Step 5: Commit**

### Task 3: Flask Routes

**Files:**
- Modify: `selling_shit/__init__.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: `CatalogStore`, `generate_platform_drafts`, `scan_catalog_folder`.
- Produces: `GET /`, `POST /items`, `POST /scan`.

- [x] **Step 1: Update failing Flask route tests**
- [x] **Step 2: Run tests and confirm failures**
- [x] **Step 3: Implement app factory helpers and routes**
- [x] **Step 4: Run tests and confirm pass**
- [x] **Step 5: Commit**

### Task 4: Dashboard UI

**Files:**
- Modify: `selling_shit/templates/home.html`
- Modify: `selling_shit/static/style.css`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: `items`, `platform_drafts`, `summary`, and `platforms` template variables.
- Produces: Drag/drop photo intake, description modal, scan button, item cards, status metrics, and draft panels.

- [x] **Step 1: Add dashboard rendering assertions**
- [x] **Step 2: Run tests and confirm assertions fail**
- [x] **Step 3: Implement template, CSS, and minimal JavaScript**
- [x] **Step 4: Run tests and confirm pass**
- [x] **Step 5: Commit**

### Task 5: Verification and Logs

**Files:**
- Modify: `SESSION_LOG.md`
- Modify: `C:\Users\drewb\.Codex\projects\selling-shit\memory\session_log.md`

**Interfaces:**
- Produces: Final test evidence, running app URL, and session log entry.

- [x] **Step 1: Run full pytest suite**
- [x] **Step 2: Start or refresh Flask on port `5001`**
- [x] **Step 3: Verify `GET /` returns 200**
- [x] **Step 4: Update session logs**
- [x] **Step 5: Commit repo-visible docs/log changes**
