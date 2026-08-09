# AGENTS.md

## Cursor Cloud specific instructions

This repository ("OneMessage") contains a Python 3.11+ generator, `setup_unified_timeline.py`, that scaffolds the "Unified Jess Timeline" data pipeline. Running the generator emits a `unified_jess_timeline/` project (config, `requirements.txt`, and staged pipeline scripts `01_fetch_messages.py`, `02_transcribe_messages.py`, `06_merge_outputs.py`) that ingests Apple Messages, transcribes audio with `faster-whisper`, and merges multiple sources into a unified JSON/Markdown timeline.

### Environment setup

- Setup runs `.cursor/install.sh` (wired via `.cursor/environment.json`). It installs the `python3-venv` system package if `ensurepip` is missing, creates a project-local virtual environment at `.venv`, and installs `requirements.txt`. The script is idempotent.
- Activate the environment with `source .venv/bin/activate`, or invoke tools directly via `.venv/bin/python`.
- `requirements.txt` mirrors the dependencies the generator installs (`typer`, `beautifulsoup4`, `lxml`, `ijson`, `faster-whisper`, `orjson`, `jinja2`, `fastapi`, `uvicorn`). `sqlite3` is stdlib.

### Running and platform notes

- `setup_unified_timeline.py`'s `main()` is **macOS-only** and interactive: it calls `check_dependencies()` (which `sys.exit`s on non-Darwin), prompts via `input()`, uses Homebrew/`launchd`/`open`, and stage `01_fetch_messages.py` reads the local macOS Messages database (`~/Library/Messages/chat.db`). These paths cannot run unmodified in the Linux Cloud Agent VM.
- Cross-platform stages **do** run on Linux. Stage `06_merge_outputs.py` merges per-source JSONL (`messages_enriched.jsonl`, `voice_events.jsonl`, `chat_events.jsonl`, `alexa_events.jsonl`) from a project's `data/outputs/` into `unified_jess_timeline.{json,md}`. The individual scaffold-generation functions (e.g. `create_directory_structure`, `create_pipeline_scripts`) are also importable and runnable on Linux for development/testing without going through the macOS-gated `main()`.

- **No lint, type-check, or automated tests** are configured; there is no test runner or build step.
- **No package manager lockfile.** Dependencies are pinned only by `requirements.txt`. If a lockfile is later added, match it to the correct tool.
