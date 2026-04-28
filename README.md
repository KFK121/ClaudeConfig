[English](README.md) | [中文](README_CN.md)

# Claude Settings Manager

<p align="center">
  <strong>A local desktop tool for managing Claude Code configuration with Profile switching</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#development-process">Development Process</a>
</p>

---

A lightweight desktop application built with Python + pywebview that provides a graphical interface for editing `~/.claude/settings.json`. Supports saving and switching between multiple API provider configurations (Profiles) with one click.

## Features

- **Visual Configuration Editing** — Edit all `settings.json` fields through a clean form UI instead of manually editing JSON
- **Profile System** — Save frequently used API configurations as named profiles, switch between providers with one click
- **Current Config** — Always see the active configuration and revert to it at any time
- **Token Masking** — Auth tokens are masked by default with toggle visibility
- **Atomic Writes** — Settings are written via temp file + rename to prevent corruption on failure
- **Unknown Fields Preserved** — Any unrecognized fields in settings.json are kept intact
- **Single Instance** — Prevents multiple instances from conflicting
- **Light Theme** — Clean, minimal UI in Chinese with English technical field names

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 |
| Desktop Window | pywebview (WebView2) |
| Frontend | Plain HTML / CSS / JS |
| Testing | pytest (TDD) |
| Packaging | PyInstaller |
| Dependency Management | uv |

## Project Structure

```
ClaudeConfig/
├── main.pyw              ← Entry point (double-click to launch)
├── app/
│   ├── api.py            ← pywebview js_api bridge
│   ├── settings.py       ← settings.json read/write
│   └── profiles.py       ← Profile CRUD
├── ui/
│   ├── index.html        ← Main page
│   ├── style.css         ← Light theme
│   ├── app.js            ← Frontend logic
│   └── icon.ico          ← App icon
├── tests/
│   ├── test_settings.py  ← Settings read/write tests
│   └── test_profiles.py  ← Profile CRUD tests
└── requirements.txt
```

## Getting Started

### Option 1: Run from source

```bash
# Install dependencies
pip install pywebview

# Launch
python main.pyw
```

### Option 2: Download the executable

Download `ClaudeSettingsManager-v1.0.2.exe` from [Releases](../../releases) and double-click to run.

> **Note:** Requires Windows 10+ with WebView2 runtime (pre-installed on Windows 11).

### Build from source

```bash
# Create clean environment with uv
uv venv .venv
uv pip install --python .venv/Scripts/python.exe pywebview pyinstaller

# Build
.venv/Scripts/python -m PyInstaller --noconfirm --noconsole --onefile \
  --name "ClaudeSettingsManager" --icon "ui/icon.ico" --add-data "ui;ui" main.pyw
```

## Usage

1. Launch the app — current `settings.json` values are loaded automatically
2. Edit connection config (Base URL, Token, Models) and preferences
3. Click **确认生效** to save changes to `settings.json`
4. Save frequently used configs as **Profiles** for one-click switching
5. Restart Claude Code for changes to take effect

## Development Process

This project was developed with a structured AI-assisted workflow, combining several methodologies:

### Requirements Exploration with OpenSpec

Used [OpenSpec](https://github.com/anthropics/openspec) to manage the change lifecycle:

1. **Exploration** (`/opsx:explore`) — Identified the core problem: editing JSON manually is error-prone when switching API providers. Explored the Profile concept as a solution.
2. **Proposal** (`/opsx:propose`) — Created a formal proposal defining two capabilities: `settings-editor` and `profile-manager`.
3. **Design** (`design.md`) — Made key decisions: Python + pywebview, file-based profiles, js_api communication, light theme UI.
4. **Tasks** (`tasks.md`) — Broke implementation into 10 trackable tasks with TDD steps.

### Brainstorming with Superpowers

Used the **Superpowers brainstorming skill** to refine design details before implementation:

- **Visual companion** — Rendered UI mockups in a browser to validate layout and color scheme
- **Profile load behavior** — Clarified whether selecting a Profile should write immediately or just fill the form (decided: fill + manual save)
- **UI decisions** — Light theme over dark, Chinese UI with English field names, white-on-red delete button

### TDD-Driven Development

Backend modules were developed test-first:

1. **Write failing test** → Verify it fails → **Write minimal implementation** → Verify it passes → **Commit**
2. `test_settings.py`: 9 tests covering read/write, unknown field preservation, atomic writes, error handling
3. `test_profiles.py`: 10 tests covering CRUD, filtering, duplicate detection, directory creation

### Subagent-Driven Implementation

Used the **Superpowers subagent-driven-development** skill to execute the implementation plan:

- Each task dispatched to an isolated subagent with full context
- Backend tasks (settings, profiles) ran TDD with pytest verification
- Frontend tasks (HTML, CSS, JS) ran in parallel for efficiency
- Integration testing validated the complete flow

### Bug Fixes & Iterations

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| `os.kill(pid, 0)` crashes on Windows | Signal 0 not supported on Windows | Switched to `ctypes.OpenProcess` then to `msvcrt.locking` file lock |
| Stale lock file after crash | PID-based detection unreliable (PID reuse) | Replaced with `msvcrt.locking` exclusive file lock (auto-released on exit) |
| Profile dropdown: re-clicking selected item does nothing | `<select>` change event only fires on value change | Added "当前配置" option that reads from file in real-time |

## License

MIT
