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
