# Claude Settings Manager — Design Spec

## Overview

A local desktop tool for editing `~/.claude/settings.json` with a Profile system for one-click switching between API providers. Built with Python + pywebview, launched by double-clicking a `.pyw` file or packaged `.exe`.

## Problem

Switching API providers in Claude Code requires manually editing 5+ JSON fields (endpoint, token, three model mappings). This is error-prone and slow when frequently switching between providers like Volcengine ARK, Anthropic official, DeepSeek, etc.

## Goals

- Double-click to launch a native desktop window with a form-based UI
- Edit all fields in `~/.claude/settings.json` (env, plugins, marketplaces)
- Profile system: save/load/delete named configuration presets for quick switching
- Changes written directly to settings.json; user restarts Claude Code manually

## Non-Goals

- Project-level `.claude/settings.local.json` editing
- Hot reload / auto-restart Claude Code
- Installer / auto-update
- Cloud sync
- API connectivity validation

## Architecture

```
main.pyw ──→ pywebview window (800x600)
              ├── ui/index.html  (frontend: forms, profile selector)
              ├── ui/style.css   (light theme)
              ├── ui/app.js      (interaction logic)
              └── app/api.py     (js_api bridge → Python backend)
                  ├── app/settings.py  (read/write settings.json)
                  └── app/profiles.py  (CRUD profiles/)
```

**Communication**: pywebview `js_api` — frontend JS calls Python methods directly, no HTTP server needed.

## UI Layout

Light theme, single-page three-section layout:

```
┌──────────────────────────────────────────┐
│  Toolbar: [Profile ▼] [Save As] [Update]│
│           [Delete]        [Save Config]   │
├──────────────────────────────────────────┤
│  🔗 连接配置                              │
│  Base URL / Auth Token (masked) /        │
│  3 Model fields / Timeout                │
├──────────────────────────────────────────┤
│  ⚙️ 偏好开关                              │
│  Disable Telemetry / Error Reporting /   │
│  Non-essential Traffic                   │
├──────────────────────────────────────────┤
│  🧩 插件与市场                            │
│  Plugin checkboxes / Marketplace list    │
└──────────────────────────────────────────┘
```

**Color scheme**: White/light background, #333 text, #666 labels, #2563eb primary button (Save Config), #dc2626 danger button (Delete, white text on red).

**Chinese UI** with technical field names in English.

## Profile System

**Storage**: Each profile is one JSON file in `~/.claude/profiles/`, named in kebab-case.

```json
{
  "name": "火山引擎 ARK",
  "env": {
    "ANTHROPIC_BASE_URL": "...",
    "ANTHROPIC_AUTH_TOKEN": "...",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "...",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "...",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "..."
  }
}
```

**Scope**: Profiles save only connection config (URL, token, 3 models). Preference switches, timeout, and plugin settings are global — not affected by profile switching.

**Load behavior**: Selecting a profile fills the connection config form fields. User must click "Save Config" to write to settings.json. This gives users a chance to review/adjust before committing.

**Operations**: Save new, update existing (with overwrite confirmation), delete (with confirmation dialog).

## Key Behaviors

- **Unknown fields preserved**: Any fields in settings.json not recognized by the tool are kept as-is on save.
- **Token masking**: Auth token field is masked by default; eye icon toggles visibility.
- **Timeout validation**: Only numeric input allowed for API_TIMEOUT_MS.
- **Preference switches**: Checked = env value "1", unchecked = field removed from env.
- **Single instance**: Second launch activates the existing window instead of opening a new one.
- **Write safety**: IO/permission errors are caught and shown as error messages; original file is not modified.

## File Structure

```
ClaudeConfig/
├── main.pyw              ← Entry point (no console window)
├── app/
│   ├── __init__.py
│   ├── api.py            ← pywebview js_api class
│   ├── settings.py       ← settings.json read/write
│   └── profiles.py       ← Profile CRUD
├── ui/
│   ├── index.html        ← Main page
│   ├── style.css         ← Light theme styles
│   └── app.js            ← Frontend logic
└── requirements.txt      ← pywebview
```

## Risks

- **WebView2 dependency**: Windows 11 ships it; Windows 10 users may need to install it manually.
- **Concurrent writes**: Single-instance check prevents multiple instances from conflicting.
- **Settings format changes**: Unknown fields are preserved; only known fields are modified on write.
