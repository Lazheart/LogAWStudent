<!-- .github/copilot-instructions.md -->
# Copilot / AI agent instructions for LogAWStudent

Purpose: help an AI agent be immediately productive in this repo by describing the architecture, key files, run/debug flows, and project-specific conventions.

- Project summary: `LogAWStudent` automates logging into AWS Academy and launching a lab using Selenium and Chrome. Main logic lives under `src/logawstudent`.

- Entrypoints & commands
  - CLI entrypoint (installed script): `awstudent` → defined in `pyproject.toml` as `logawstudent.cli:app`.
  - The README also documents a helper shell `loginUpAWS.sh` (project root) which sets up a venv, installs deps and runs the bot. Use that for reproducible runs.
  - You can run the CLI directly during development with: `python -m pip install -e .` and then `awstudent start` or `python -m logawstudent.cli`.

- Key files to inspect
  - `src/logawstudent/cli.py` — Typer-based CLI. Commands: `login`, `url`, `start`, `status`, `logout`.
  - `src/logawstudent/core.py` — Selenium logic: ChromeOptions, ChromeDriverManager, iframe handling, resource blocking and state polling.
  - `src/logawstudent/utils.py` — Small .env management helpers (load/set/update/unset/clear/validate). `.env` file is created in project root.
  - `pyproject.toml` / `requirements.txt` — dependency list: selenium, webdriver-manager, python-dotenv, typer.

- Important project-specific patterns & behaviors (do not change without tests)
  - Environment storage: `utils.set_env/update_env/unset_env` write a file named `.env` in project root. Missing keys are omitted (only non-empty values are written). `validate_credentials()` raises ValueError listing missing keys.
  - CLI UX: `cli.py` masks passwords via `typer.prompt(..., hide_input=True)` and intentionally shows truncated values when listing credentials. Preserve that pattern when adding features that display secrets.
  - Selenium patterns:
    - `core.block_heavy_resources(driver)` uses CDP `Network.setBlockedURLs` to speed runs. CDP calls may fail depending on Chrome/driver combination — catch and continue.
    - Many operations are inside iframes: the code repeatedly switches into frames and calls `driver.switch_to.default_content()` in finally blocks. Follow the same approach when interacting with the lab page.
    - Uses `webdriver_manager.chrome.ChromeDriverManager().install()` to obtain a compatible driver at runtime. Network access is required for first run.

- Typical developer workflows (fast reference)
  - Setup (recommended): run `./loginUpAWS.sh` (project root) which creates venv and installs `requirements.txt`.
  - Run CLI directly (dev): `python -m pip install -e .` then `awstudent login`, `awstudent url --set`, `awstudent start`.
  - If you prefer not to install: run `python -m logawstudent.cli` from repo root (Typer app will run).

- Troubleshooting notes (observed/likely issues)
  - If ChromeDriver fails: ensure Chrome is installed and compatible with the driver downloaded by `webdriver-manager`.
  - If Selenium cannot find elements: lab pages use heavy iframe nesting — check `core.check_lab_status` and `click_start_lab_fast` for the patterns to follow.
  - CDP calls (resource blocking) are best-effort; they are wrapped in try/except.

- Quick examples (use these exact locations in suggestions)
  - Show how to validate credentials before running: reference `src/logawstudent/utils.py::validate_credentials()` and `src/logawstudent/cli.py::start` where it's called.
  - To change headless behavior: edit `src/logawstudent/core.py` where `options.add_argument("--headless=new")` is added; remove/comment to see the browser.

- Conventions
  - Config is stored in `.env` at repo root. Use `python-dotenv` semantics when reading/writing.
  - Keep user-facing CLI strings in `cli.py` (do not move to core.py). `core.py` should remain implementation-only and return logs via `log()` helper.
  - Avoid printing sensitive data; follow existing truncation/masking in `cli.py` when showing values.

- Gaps / discrepancies found (ask maintainers)
  - README mentions running `python -m main` and editing `main.py`. There is no `main.py` in the repository; the actual entrypoint is the `awstudent` script (`pyproject.toml`). Confirm which is intended and update README or add a small `main.py` shim if desired.

If anything is unclear, tell me which area you'd like expanded (run flows, more examples, suggested unit tests, or merging with an existing copilot file). I'll update this file accordingly.
