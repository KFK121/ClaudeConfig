# Claude Settings Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local desktop tool with pywebview that lets users edit `~/.claude/settings.json` through a form UI and switch between saved API provider profiles.

**Architecture:** Python backend reads/writes settings.json and manages profiles; pywebview's js_api exposes backend methods to a pure HTML/CSS/JS frontend in a native window. No HTTP server, no build tools.

**Tech Stack:** Python 3.12, pywebview, pytest (for backend tests), plain HTML/CSS/JS

---

## File Structure

```
ClaudeConfig/
├── main.pyw                  ← Entry point (double-click to launch)
├── requirements.txt          ← pywebview, pytest
├── app/
│   ├── __init__.py           ← Empty, makes app a package
│   ├── settings.py           ← Read/write ~/.claude/settings.json
│   ├── profiles.py           ← CRUD for ~/.claude/profiles/*.json
│   └── api.py                ← pywebview js_api bridge class
├── ui/
│   ├── index.html            ← Main page (form layout)
│   ├── style.css             ← Light theme styles
│   └── app.js                ← Frontend interaction logic
└── tests/
    ├── __init__.py            ← Empty
    ├── test_settings.py       ← Tests for settings.py
    └── test_profiles.py       ← Tests for profiles.py
```

---

### Task 1: Project scaffold and dependencies

**Files:**
- Create: `requirements.txt`
- Create: `app/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
pywebview>=5.0
pytest>=8.0
```

- [ ] **Step 2: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: pywebview and pytest installed successfully

- [ ] **Step 3: Create package init files**

Create `app/__init__.py` (empty) and `tests/__init__.py` (empty).

- [ ] **Step 4: Verify pytest runs**

Run: `pytest --version`
Expected: pytest 8.x

- [ ] **Step 5: Commit**

```bash
git add requirements.txt app/__init__.py tests/__init__.py
git commit -m "feat: scaffold project structure and dependencies"
```

---

### Task 2: settings.py — Read settings.json

**Files:**
- Create: `app/settings.py`
- Create: `tests/test_settings.py`

- [ ] **Step 1: Write failing tests for read behavior**

```python
# tests/test_settings.py
import json
import pytest
from pathlib import Path
from app.settings import load_settings, get_settings_path


class TestLoadSettings:
    def test_load_existing_file(self, tmp_path, monkeypatch):
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({
            "env": {"ANTHROPIC_BASE_URL": "https://example.com"},
            "enabledPlugins": {"plugin-a": True}
        }))
        monkeypatch.setattr("app.settings.get_settings_path", lambda: settings_file)
        result = load_settings()
        assert result["env"]["ANTHROPIC_BASE_URL"] == "https://example.com"
        assert result["enabledPlugins"]["plugin-a"] is True

    def test_load_missing_file_returns_default(self, tmp_path, monkeypatch):
        missing = tmp_path / "nonexistent" / "settings.json"
        monkeypatch.setattr("app.settings.get_settings_path", lambda: missing)
        result = load_settings()
        assert result == {"env": {}, "enabledPlugins": {}, "extraKnownMarketplaces": {}}

    def test_load_preserves_unknown_fields(self, tmp_path, monkeypatch):
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({
            "env": {"ANTHROPIC_BASE_URL": "https://example.com"},
            "customSection": {"foo": "bar"}
        }))
        monkeypatch.setattr("app.settings.get_settings_path", lambda: settings_file)
        result = load_settings()
        assert result["customSection"] == {"foo": "bar"}

    def test_load_invalid_json_raises(self, tmp_path, monkeypatch):
        settings_file = tmp_path / "settings.json"
        settings_file.write_text("not json{{{")
        monkeypatch.setattr("app.settings.get_settings_path", lambda: settings_file)
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_settings()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_settings.py -v`
Expected: 4 failures (module import error)

- [ ] **Step 3: Implement settings.py read logic**

```python
# app/settings.py
import json
from pathlib import Path


def get_settings_path() -> Path:
    """Return path to ~/.claude/settings.json"""
    return Path.home() / ".claude" / "settings.json"


DEFAULT_SETTINGS = {
    "env": {},
    "enabledPlugins": {},
    "extraKnownMarketplaces": {},
}


def load_settings() -> dict:
    """Load settings.json. Return default structure if file missing.
    Raise ValueError if file exists but contains invalid JSON."""
    path = get_settings_path()
    if not path.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise ValueError(f"Cannot read settings file: {e}") from e

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in settings file: {e}") from e

    # Ensure top-level keys exist (preserve any extra keys)
    result = DEFAULT_SETTINGS.copy()
    result.update(data)
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_settings.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add app/settings.py tests/test_settings.py
git commit -m "feat: implement settings.json read logic with tests"
```

---

### Task 3: settings.py — Write settings.json

**Files:**
- Modify: `app/settings.py`
- Modify: `tests/test_settings.py`

- [ ] **Step 1: Write failing tests for save behavior**

Add to `tests/test_settings.py`:

```python
class TestSaveSettings:
    def test_save_creates_file(self, tmp_path, monkeypatch):
        settings_file = tmp_path / "settings.json"
        monkeypatch.setattr("app.settings.get_settings_path", lambda: settings_file)
        data = {"env": {"ANTHROPIC_BASE_URL": "https://example.com"}, "enabledPlugins": {}, "extraKnownMarketplaces": {}}
        save_settings(data)
        written = json.loads(settings_file.read_text(encoding="utf-8"))
        assert written["env"]["ANTHROPIC_BASE_URL"] == "https://example.com"

    def test_save_preserves_unknown_fields(self, tmp_path, monkeypatch):
        settings_file = tmp_path / "settings.json"
        settings_file.write_text(json.dumps({
            "env": {},
            "customSection": {"foo": "bar"}
        }))
        monkeypatch.setattr("app.settings.get_settings_path", lambda: settings_file)
        data = load_settings()
        save_settings(data)
        written = json.loads(settings_file.read_text(encoding="utf-8"))
        assert written["customSection"] == {"foo": "bar"}

    def test_save_uses_2_space_indent(self, tmp_path, monkeypatch):
        settings_file = tmp_path / "settings.json"
        monkeypatch.setattr("app.settings.get_settings_path", lambda: settings_file)
        save_settings({"env": {}, "enabledPlugins": {}, "extraKnownMarketplaces": {}})
        content = settings_file.read_text(encoding="utf-8")
        assert '  "env"' in content

    def test_save_returns_error_on_write_failure(self, tmp_path, monkeypatch):
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        settings_file = readonly_dir / "settings.json"
        # Make directory read-only after creating a file
        settings_file.write_text("{}")
        monkeypatch.setattr("app.settings.get_settings_path", lambda: settings_file)
        # We'll test that the function returns an error message string on failure
        # For this test, we'll mock the write to raise OSError
        from unittest.mock import patch
        with patch("app.settings.Path.write_text", side_effect=PermissionError("denied")):
            result = save_settings({"env": {}, "enabledPlugins": {}, "extraKnownMarketplaces": {}})
        assert isinstance(result, str)
        assert "denied" in result or "PermissionError" in result

    def test_save_atomic_does_not_corrupt_on_failure(self, tmp_path, monkeypatch):
        settings_file = tmp_path / "settings.json"
        original = {"env": {"ANTHROPIC_BASE_URL": "https://original.com"}, "enabledPlugins": {}}
        settings_file.write_text(json.dumps(original))
        monkeypatch.setattr("app.settings.get_settings_path", lambda: settings_file)
        # Verify original is intact after failed save
        from unittest.mock import patch
        with patch("app.settings.Path.write_text", side_effect=PermissionError("denied")):
            save_settings({"env": {"ANTHROPIC_BASE_URL": "https://new.com"}, "enabledPlugins": {}})
        # Original file should be unchanged
        still_there = json.loads(settings_file.read_text(encoding="utf-8"))
        assert still_there["env"]["ANTHROPIC_BASE_URL"] == "https://original.com"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_settings.py::TestSaveSettings -v`
Expected: 5 failures (save_settings not defined)

- [ ] **Step 3: Implement save_settings**

Add to `app/settings.py`:

```python
def save_settings(data: dict) -> str | None:
    """Save data to settings.json with 2-space indent.
    Writes to a temp file first, then renames (atomic on same filesystem).
    Returns error message string on failure, None on success.
    Original file is preserved if write fails."""
    path = get_settings_path()
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    temp_path = path.with_suffix(".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(path)
        return None
    except OSError as e:
        # Clean up temp file if it exists
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        return str(e)
```

Add `save_settings` to imports in tests if needed.

- [ ] **Step 4: Run all settings tests**

Run: `pytest tests/test_settings.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add app/settings.py tests/test_settings.py
git commit -m "feat: implement atomic settings.json save with error handling"
```

---

### Task 4: profiles.py — Profile CRUD

**Files:**
- Create: `app/profiles.py`
- Create: `tests/test_profiles.py`

- [ ] **Step 1: Write failing tests for profile operations**

```python
# tests/test_profiles.py
import json
import pytest
from pathlib import Path
from app.profiles import (
    list_profiles, save_profile, update_profile, delete_profile, get_profiles_dir
)


class TestListProfiles:
    def test_list_empty_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr("app.profiles.get_profiles_dir", lambda: tmp_path / "profiles")
        result = list_profiles()
        assert result == []

    def test_list_returns_profiles(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        (profiles_dir / "volcengine-ark.json").write_text(json.dumps({
            "name": "火山引擎 ARK",
            "env": {"ANTHROPIC_BASE_URL": "https://ark.example.com"}
        }))
        monkeypatch.setattr("app.profiles.get_profiles_dir", lambda: profiles_dir)
        result = list_profiles()
        assert len(result) == 1
        assert result[0]["name"] == "火山引擎 ARK"
        assert result[0]["filename"] == "volcengine-ark.json"

    def test_list_ignores_non_json(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        (profiles_dir / "volcengine-ark.json").write_text(json.dumps({"name": "test", "env": {}}))
        (profiles_dir / "notes.txt").write_text("ignore me")
        monkeypatch.setattr("app.profiles.get_profiles_dir", lambda: profiles_dir)
        result = list_profiles()
        assert len(result) == 1


class TestSaveProfile:
    def test_save_creates_file(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / "profiles"
        monkeypatch.setattr("app.profiles.get_profiles_dir", lambda: profiles_dir)
        result = save_profile("火山引擎 ARK", {
            "ANTHROPIC_BASE_URL": "https://ark.example.com",
            "ANTHROPIC_AUTH_TOKEN": "tok123",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "GLM-5.1",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "GLM-5.1",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "GLM-5.1",
        })
        assert result is None  # None = success
        saved = json.loads((profiles_dir / "火山引擎-ark.json").read_text(encoding="utf-8"))
        assert saved["name"] == "火山引擎 ARK"
        assert saved["env"]["ANTHROPIC_BASE_URL"] == "https://ark.example.com"
        # Must NOT contain non-connection fields
        assert "DISABLE_TELEMETRY" not in saved["env"]
        assert "API_TIMEOUT_MS" not in saved["env"]

    def test_save_creates_dir_if_missing(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / "profiles"
        assert not profiles_dir.exists()
        monkeypatch.setattr("app.profiles.get_profiles_dir", lambda: profiles_dir)
        result = save_profile("Test", {
            "ANTHROPIC_BASE_URL": "https://test.com",
            "ANTHROPIC_AUTH_TOKEN": "tok",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "m1",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "m2",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "m3",
        })
        assert profiles_dir.exists()

    def test_save_duplicate_returns_error(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        (profiles_dir / "test.json").write_text(json.dumps({"name": "Test", "env": {}}))
        monkeypatch.setattr("app.profiles.get_profiles_dir", lambda: profiles_dir)
        result = save_profile("Test", {
            "ANTHROPIC_BASE_URL": "x", "ANTHROPIC_AUTH_TOKEN": "y",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "a", "ANTHROPIC_DEFAULT_SONNET_MODEL": "b",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "c",
        })
        assert isinstance(result, str)  # error message about duplicate


class TestUpdateProfile:
    def test_update_overwrites_existing(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        (profiles_dir / "my-profile.json").write_text(json.dumps({
            "name": "My Profile", "env": {"ANTHROPIC_BASE_URL": "https://old.com"}
        }))
        monkeypatch.setattr("app.profiles.get_profiles_dir", lambda: profiles_dir)
        result = update_profile("my-profile", {
            "ANTHROPIC_BASE_URL": "https://new.com",
            "ANTHROPIC_AUTH_TOKEN": "newtok",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "m1",
            "ANTHROPIC_DEFAULT_SONNET_MODEL": "m2",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "m3",
        })
        assert result is None
        saved = json.loads((profiles_dir / "my-profile.json").read_text(encoding="utf-8"))
        assert saved["env"]["ANTHROPIC_BASE_URL"] == "https://new.com"

    def test_update_nonexistent_returns_error(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        monkeypatch.setattr("app.profiles.get_profiles_dir", lambda: profiles_dir)
        result = update_profile("ghost", {
            "ANTHROPIC_BASE_URL": "x", "ANTHROPIC_AUTH_TOKEN": "y",
            "ANTHROPIC_DEFAULT_OPUS_MODEL": "a", "ANTHROPIC_DEFAULT_SONNET_MODEL": "b",
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": "m3",
        })
        assert isinstance(result, str)  # error message


class TestDeleteProfile:
    def test_delete_removes_file(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        (profiles_dir / "old-profile.json").write_text(json.dumps({"name": "Old", "env": {}}))
        monkeypatch.setattr("app.profiles.get_profiles_dir", lambda: profiles_dir)
        result = delete_profile("old-profile")
        assert result is None
        assert not (profiles_dir / "old-profile.json").exists()

    def test_delete_nonexistent_returns_error(self, tmp_path, monkeypatch):
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        monkeypatch.setattr("app.profiles.get_profiles_dir", lambda: profiles_dir)
        result = delete_profile("ghost")
        assert isinstance(result, str)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_profiles.py -v`
Expected: all failures (module import error)

- [ ] **Step 3: Implement profiles.py**

```python
# app/profiles.py
import json
import re
from pathlib import Path


# Only these env keys are saved in profiles (connection config)
CONNECTION_KEYS = {
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
}


def get_profiles_dir() -> Path:
    """Return path to ~/.claude/profiles/"""
    return Path.home() / ".claude" / "profiles"


def _name_to_filename(name: str) -> str:
    """Convert display name to kebab-case filename."""
    # Replace non-alphanumeric (including CJK) with hyphens, collapse multiples
    kebab = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", name).strip("-")
    return f"{kebab}.json"


def _filter_connection_env(env: dict) -> dict:
    """Keep only connection config keys from env dict."""
    return {k: v for k, v in env.items() if k in CONNECTION_KEYS}


def list_profiles() -> list[dict]:
    """List all saved profiles. Returns list of dicts with name, filename, env."""
    profiles_dir = get_profiles_dir()
    if not profiles_dir.exists():
        return []

    result = []
    for f in sorted(profiles_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            result.append({
                "name": data.get("name", f.stem),
                "filename": f.name,
                "env": data.get("env", {}),
            })
        except (json.JSONDecodeError, OSError):
            continue  # skip corrupt files
    return result


def save_profile(name: str, env: dict) -> str | None:
    """Save a new profile. Returns None on success, error string on failure."""
    profiles_dir = get_profiles_dir()
    filename = _name_to_filename(name)
    filepath = profiles_dir / filename

    if filepath.exists():
        return f'Profile "{name}" already exists. Use update to overwrite.'

    profiles_dir.mkdir(parents=True, exist_ok=True)
    profile_data = {
        "name": name,
        "env": _filter_connection_env(env),
    }
    try:
        filepath.write_text(
            json.dumps(profile_data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return None
    except OSError as e:
        return str(e)


def update_profile(filename_stem: str, env: dict) -> str | None:
    """Update an existing profile by filename stem (without .json).
    Returns None on success, error string on failure."""
    profiles_dir = get_profiles_dir()
    filepath = profiles_dir / f"{filename_stem}.json"

    if not filepath.exists():
        return f'Profile "{filename_stem}" not found.'

    try:
        existing = json.loads(filepath.read_text(encoding="utf-8"))
        existing["env"] = _filter_connection_env(env)
        filepath.write_text(
            json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return None
    except OSError as e:
        return str(e)


def delete_profile(filename_stem: str) -> str | None:
    """Delete a profile by filename stem. Returns None on success, error string on failure."""
    profiles_dir = get_profiles_dir()
    filepath = profiles_dir / f"{filename_stem}.json"

    if not filepath.exists():
        return f'Profile "{filename_stem}" not found.'

    try:
        filepath.unlink()
        return None
    except OSError as e:
        return str(e)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_profiles.py -v`
Expected: all passed

- [ ] **Step 5: Run all tests**

Run: `pytest tests/ -v`
Expected: all passed

- [ ] **Step 6: Commit**

```bash
git add app/profiles.py tests/test_profiles.py
git commit -m "feat: implement profile CRUD with tests"
```

---

### Task 5: api.py — pywebview js_api bridge

**Files:**
- Create: `app/api.py`

This is a thin bridge layer — the logic is in settings.py and profiles.py. No unit tests needed for this glue code; integration is verified when the GUI runs.

- [ ] **Step 1: Implement api.py**

```python
# app/api.py
import webview
from app.settings import load_settings, save_settings
from app.profiles import list_profiles, save_profile, update_profile, delete_profile


class Api:
    """Bridge between frontend JS and Python backend via pywebview js_api."""

    def load_settings(self) -> dict:
        """Load current settings.json content."""
        try:
            return {"success": True, "data": load_settings()}
        except ValueError as e:
            return {"success": False, "error": str(e)}

    def save_settings(self, config: dict) -> dict:
        """Save config dict to settings.json."""
        result = save_settings(config)
        if result is None:
            return {"success": True}
        return {"success": False, "error": result}

    def list_profiles(self) -> dict:
        """List all saved profiles."""
        return {"success": True, "data": list_profiles()}

    def save_profile(self, name: str, env: dict) -> dict:
        """Save current env as a new profile."""
        result = save_profile(name, env)
        if result is None:
            return {"success": True}
        return {"success": False, "error": result}

    def update_profile(self, filename_stem: str, env: dict) -> dict:
        """Update an existing profile with current env values."""
        result = update_profile(filename_stem, env)
        if result is None:
            return {"success": True}
        return {"success": False, "error": result}

    def delete_profile(self, filename_stem: str) -> dict:
        """Delete a profile by filename stem."""
        result = delete_profile(filename_stem)
        if result is None:
            return {"success": True}
        return {"success": False, "error": result}
```

- [ ] **Step 2: Commit**

```bash
git add app/api.py
git commit -m "feat: add pywebview js_api bridge"
```

---

### Task 6: UI — index.html

**Files:**
- Create: `ui/index.html`

- [ ] **Step 1: Create the HTML page**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Settings Manager</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>

    <!-- Toolbar -->
    <div class="toolbar">
        <div class="toolbar-left">
            <label for="profile-select">Profile:</label>
            <select id="profile-select">
                <option value="">-- 无已保存配置 --</option>
            </select>
            <button id="btn-save-profile" class="btn btn-secondary">保存为 Profile</button>
            <button id="btn-update-profile" class="btn btn-secondary">更新</button>
            <button id="btn-delete-profile" class="btn btn-danger">删除</button>
        </div>
        <div class="toolbar-right">
            <button id="btn-save" class="btn btn-primary">保存配置</button>
        </div>
    </div>

    <!-- Connection Config -->
    <div class="section">
        <h3 class="section-title">🔗 连接配置</h3>
        <div class="form-grid">
            <label for="f-base-url">Base URL</label>
            <input type="text" id="f-base-url" data-env="ANTHROPIC_BASE_URL">

            <label for="f-auth-token">Auth Token</label>
            <div class="token-wrapper">
                <input type="password" id="f-auth-token" data-env="ANTHROPIC_AUTH_TOKEN">
                <button id="btn-toggle-token" class="btn-icon" title="显示/隐藏令牌">👁</button>
            </div>

            <label for="f-opus-model">Opus Model</label>
            <input type="text" id="f-opus-model" data-env="ANTHROPIC_DEFAULT_OPUS_MODEL">

            <label for="f-sonnet-model">Sonnet Model</label>
            <input type="text" id="f-sonnet-model" data-env="ANTHROPIC_DEFAULT_SONNET_MODEL">

            <label for="f-haiku-model">Haiku Model</label>
            <input type="text" id="f-haiku-model" data-env="ANTHROPIC_DEFAULT_HAIKU_MODEL">

            <label for="f-timeout">Timeout (ms)</label>
            <input type="text" id="f-timeout" data-env="API_TIMEOUT_MS" inputmode="numeric">
        </div>
    </div>

    <!-- Preference Switches -->
    <div class="section">
        <h3 class="section-title">⚙️ 偏好开关</h3>
        <div class="checkbox-row">
            <label><input type="checkbox" id="f-disable-telemetry" data-env="DISABLE_TELEMETRY"> 禁用遥测</label>
            <label><input type="checkbox" id="f-disable-error" data-env="DISABLE_ERROR_REPORTING"> 禁用错误上报</label>
            <label><input type="checkbox" id="f-disable-traffic" data-env="CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"> 禁用非必要流量</label>
        </div>
    </div>

    <!-- Plugins & Marketplaces -->
    <div class="section">
        <h3 class="section-title">🧩 插件与市场</h3>
        <div id="plugins-container" class="checkbox-row">
            <!-- Populated dynamically -->
        </div>
        <div id="marketplaces-container" class="marketplace-list">
            <!-- Populated dynamically -->
        </div>
    </div>

    <!-- Toast notification -->
    <div id="toast" class="toast hidden"></div>

    <!-- Dialog overlay -->
    <div id="dialog-overlay" class="dialog-overlay hidden">
        <div class="dialog-box">
            <p id="dialog-message"></p>
            <div class="dialog-input-wrapper hidden">
                <input type="text" id="dialog-input" placeholder="输入 Profile 名称">
            </div>
            <div class="dialog-buttons">
                <button id="dialog-cancel" class="btn btn-secondary">取消</button>
                <button id="dialog-confirm" class="btn btn-primary">确认</button>
            </div>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add ui/index.html
git commit -m "feat: add main HTML page with form layout"
```

---

### Task 7: UI — style.css

**Files:**
- Create: `ui/style.css`

- [ ] **Step 1: Create the light theme stylesheet**

```css
/* ui/style.css — Light theme for Claude Settings Manager */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
    color: #333;
    background: #fff;
    line-height: 1.5;
}

/* Toolbar */
.toolbar {
    background: #f8f9fa;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #e0e0e0;
    position: sticky;
    top: 0;
    z-index: 10;
}

.toolbar-left {
    display: flex;
    align-items: center;
    gap: 8px;
}

.toolbar-left label {
    color: #555;
    font-size: 13px;
}

.toolbar-left select {
    padding: 5px 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #fff;
    color: #333;
    font-size: 13px;
    min-width: 180px;
    cursor: pointer;
}

.toolbar-right {
    display: flex;
    align-items: center;
}

/* Sections */
.section {
    padding: 16px;
    border-bottom: 1px solid #f0f0f0;
}

.section:last-child {
    border-bottom: none;
}

.section-title {
    color: #333;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 12px;
}

/* Form grid */
.form-grid {
    display: grid;
    grid-template-columns: 140px 1fr;
    gap: 10px;
    align-items: center;
}

.form-grid label {
    color: #666;
    font-size: 13px;
    text-align: right;
}

.form-grid input[type="text"],
.form-grid input[type="password"] {
    padding: 6px 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 13px;
    color: #333;
    background: #fff;
    width: 100%;
}

.form-grid input:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
}

/* Token field */
.token-wrapper {
    display: flex;
    gap: 6px;
    align-items: center;
}

.token-wrapper input {
    flex: 1;
}

/* Buttons */
.btn {
    padding: 6px 14px;
    font-size: 13px;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
    background: #fff;
    color: #333;
    transition: background 0.15s;
}

.btn:hover {
    background: #f0f0f0;
}

.btn-primary {
    background: #2563eb;
    color: #fff;
    border: none;
}

.btn-primary:hover {
    background: #1d4ed8;
}

.btn-secondary {
    background: #fff;
    border: 1px solid #ccc;
}

.btn-danger {
    background: #dc2626;
    color: #fff;
    border: none;
}

.btn-danger:hover {
    background: #b91c1c;
}

.btn-icon {
    padding: 4px 8px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #fff;
    cursor: pointer;
    line-height: 1;
}

/* Checkbox row */
.checkbox-row {
    display: flex;
    gap: 24px;
    flex-wrap: wrap;
}

.checkbox-row label {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #444;
    font-size: 13px;
    cursor: pointer;
}

/* Marketplace list */
.marketplace-list {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #e0e0e0;
}

.marketplace-item {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #444;
    font-size: 13px;
    padding: 4px 0;
}

.marketplace-item .icon {
    color: #999;
}

.marketplace-item .name {
    font-weight: 600;
}

.marketplace-item .source {
    color: #999;
}

/* Toast notification */
.toast {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    padding: 10px 24px;
    border-radius: 6px;
    font-size: 13px;
    z-index: 100;
    transition: opacity 0.3s;
}

.toast.hidden {
    opacity: 0;
    pointer-events: none;
}

.toast.success {
    background: #16a34a;
    color: #fff;
}

.toast.error {
    background: #dc2626;
    color: #fff;
}

/* Dialog overlay */
.dialog-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 50;
}

.dialog-overlay.hidden {
    display: none;
}

.dialog-box {
    background: #fff;
    border-radius: 8px;
    padding: 24px;
    min-width: 320px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.dialog-box p {
    margin-bottom: 16px;
    color: #333;
}

.dialog-input-wrapper {
    margin-bottom: 16px;
}

.dialog-input-wrapper input {
    width: 100%;
    padding: 6px 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 13px;
}

.dialog-input-wrapper.hidden {
    display: none;
}

.dialog-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
}
```

- [ ] **Step 2: Commit**

```bash
git add ui/style.css
git commit -m "feat: add light theme stylesheet"
```

---

### Task 8: UI — app.js frontend logic

**Files:**
- Create: `ui/app.js`

- [ ] **Step 1: Create the frontend interaction script**

```js
// ui/app.js — Frontend logic for Claude Settings Manager

// pywebview API bridge (available after page loads)
let api;

// Current full settings data (for preserving unknown fields on save)
let currentSettings = {};

// Profile connection env keys
const CONNECTION_KEYS = [
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_DEFAULT_OPUS_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL",
];

// === Initialization ===

window.addEventListener("pywebviewready", () => {
    api = pywebview.api;
    init();
});

async function init() {
    await loadAndRenderSettings();
    await refreshProfileSelect();
    bindEvents();
}

// === Settings load & render ===

async function loadAndRenderSettings() {
    const resp = await api.load_settings();
    if (!resp.success) {
        showToast(resp.error, "error");
        return;
    }
    currentSettings = resp.data;
    renderSettings(currentSettings);
}

function renderSettings(data) {
    const env = data.env || {};

    // Connection config inputs
    const fields = {
        "f-base-url": "ANTHROPIC_BASE_URL",
        "f-auth-token": "ANTHROPIC_AUTH_TOKEN",
        "f-opus-model": "ANTHROPIC_DEFAULT_OPUS_MODEL",
        "f-sonnet-model": "ANTHROPIC_DEFAULT_SONNET_MODEL",
        "f-haiku-model": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        "f-timeout": "API_TIMEOUT_MS",
    };
    for (const [elemId, envKey] of Object.entries(fields)) {
        document.getElementById(elemId).value = env[envKey] || "";
    }

    // Preference switches: checked if value === "1"
    const switches = {
        "f-disable-telemetry": "DISABLE_TELEMETRY",
        "f-disable-error": "DISABLE_ERROR_REPORTING",
        "f-disable-traffic": "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    };
    for (const [elemId, envKey] of Object.entries(switches)) {
        document.getElementById(elemId).checked = env[envKey] === "1";
    }

    // Plugins
    const pluginsContainer = document.getElementById("plugins-container");
    pluginsContainer.innerHTML = "";
    const plugins = data.enabledPlugins || {};
    for (const [name, enabled] of Object.entries(plugins)) {
        const label = document.createElement("label");
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = enabled === true;
        checkbox.dataset.pluginName = name;
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(" " + name));
        pluginsContainer.appendChild(label);
    }

    // Marketplaces
    const mktContainer = document.getElementById("marketplaces-container");
    mktContainer.innerHTML = "";
    const marketplaces = data.extraKnownMarketplaces || {};
    for (const [name, info] of Object.entries(marketplaces)) {
        const div = document.createElement("div");
        div.className = "marketplace-item";
        const repo = info.source ? info.source.repo : "";
        div.innerHTML = `<span class="icon">📦</span><span class="name">${escapeHtml(name)}</span><span class="source">${escapeHtml(repo)}</span>`;
        mktContainer.appendChild(div);
    }
}

// === Collect form values and save ===

function collectFormData() {
    // Start from currentSettings to preserve unknown fields
    const data = JSON.parse(JSON.stringify(currentSettings));
    data.env = data.env || {};

    // Connection config fields
    data.env.ANTHROPIC_BASE_URL = document.getElementById("f-base-url").value;
    data.env.ANTHROPIC_AUTH_TOKEN = document.getElementById("f-auth-token").value;
    data.env.ANTHROPIC_DEFAULT_OPUS_MODEL = document.getElementById("f-opus-model").value;
    data.env.ANTHROPIC_DEFAULT_SONNET_MODEL = document.getElementById("f-sonnet-model").value;
    data.env.ANTHROPIC_DEFAULT_HAIKU_MODEL = document.getElementById("f-haiku-model").value;

    const timeout = document.getElementById("f-timeout").value.trim();
    if (timeout) {
        data.env.API_TIMEOUT_MS = timeout;
    }

    // Preference switches
    const switchMap = {
        "f-disable-telemetry": "DISABLE_TELEMETRY",
        "f-disable-error": "DISABLE_ERROR_REPORTING",
        "f-disable-traffic": "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
    };
    for (const [elemId, envKey] of Object.entries(switchMap)) {
        if (document.getElementById(elemId).checked) {
            data.env[envKey] = "1";
        } else {
            delete data.env[envKey];
        }
    }

    // Plugins
    data.enabledPlugins = data.enabledPlugins || {};
    const pluginCheckboxes = document.querySelectorAll("#plugins-container input[type=checkbox]");
    pluginCheckboxes.forEach(cb => {
        const name = cb.dataset.pluginName;
        if (cb.checked) {
            data.enabledPlugins[name] = true;
        } else {
            delete data.enabledPlugins[name];
        }
    });

    return data;
}

async function handleSave() {
    const data = collectFormData();
    const resp = await api.save_settings(data);
    if (resp.success) {
        currentSettings = data;
        showToast("配置已保存", "success");
    } else {
        showToast("保存失败: " + resp.error, "error");
    }
}

// === Profile operations ===

async function refreshProfileSelect() {
    const resp = await api.list_profiles();
    const select = document.getElementById("profile-select");
    // Keep first placeholder option
    select.innerHTML = '<option value="">-- 无已保存配置 --</option>';
    if (resp.success && resp.data.length > 0) {
        resp.data.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.filename;
            opt.textContent = p.name;
            opt.dataset.env = JSON.stringify(p.env);
            select.appendChild(opt);
        });
    }
}

function handleProfileSelect() {
    const select = document.getElementById("profile-select");
    const selected = select.options[select.selectedIndex];
    if (!selected || !selected.value) return;

    const profileEnv = JSON.parse(selected.dataset.env);
    // Only fill connection config fields (not switches, timeout, plugins)
    document.getElementById("f-base-url").value = profileEnv.ANTHROPIC_BASE_URL || "";
    document.getElementById("f-auth-token").value = profileEnv.ANTHROPIC_AUTH_TOKEN || "";
    document.getElementById("f-opus-model").value = profileEnv.ANTHROPIC_DEFAULT_OPUS_MODEL || "";
    document.getElementById("f-sonnet-model").value = profileEnv.ANTHROPIC_DEFAULT_SONNET_MODEL || "";
    document.getElementById("f-haiku-model").value = profileEnv.ANTHROPIC_DEFAULT_HAIKU_MODEL || "";
}

function getConnectionEnv() {
    return {
        ANTHROPIC_BASE_URL: document.getElementById("f-base-url").value,
        ANTHROPIC_AUTH_TOKEN: document.getElementById("f-auth-token").value,
        ANTHROPIC_DEFAULT_OPUS_MODEL: document.getElementById("f-opus-model").value,
        ANTHROPIC_DEFAULT_SONNET_MODEL: document.getElementById("f-sonnet-model").value,
        ANTHROPIC_DEFAULT_HAIKU_MODEL: document.getElementById("f-haiku-model").value,
    };
}

async function handleSaveProfile() {
    const name = await showDialog("保存新 Profile", "请输入 Profile 名称：", true);
    if (!name) return;

    const env = getConnectionEnv();
    const resp = await api.save_profile(name, env);
    if (resp.success) {
        showToast("Profile 已保存", "success");
        await refreshProfileSelect();
    } else {
        showToast("保存失败: " + resp.error, "error");
    }
}

async function handleUpdateProfile() {
    const select = document.getElementById("profile-select");
    const filename = select.value;
    if (!filename) {
        showToast("请先选择一个 Profile", "error");
        return;
    }
    const stem = filename.replace(".json", "");
    const env = getConnectionEnv();
    const resp = await api.update_profile(stem, env);
    if (resp.success) {
        showToast("Profile 已更新", "success");
        await refreshProfileSelect();
    } else {
        showToast("更新失败: " + resp.error, "error");
    }
}

async function handleDeleteProfile() {
    const select = document.getElementById("profile-select");
    const filename = select.value;
    if (!filename) {
        showToast("请先选择一个 Profile", "error");
        return;
    }
    const profileName = select.options[select.selectedIndex].textContent;
    const confirmed = await showDialog("删除 Profile", `确认删除 "${profileName}" 吗？此操作不可撤销。`, false);
    if (!confirmed) return;

    const stem = filename.replace(".json", "");
    const resp = await api.delete_profile(stem);
    if (resp.success) {
        showToast("Profile 已删除", "success");
        select.selectedIndex = 0;
        await refreshProfileSelect();
    } else {
        showToast("删除失败: " + resp.error, "error");
    }
}

// === Token toggle ===

function handleToggleToken() {
    const input = document.getElementById("f-auth-token");
    input.type = input.type === "password" ? "text" : "password";
}

// === Timeout validation ===

function handleTimeoutInput(e) {
    e.target.value = e.target.value.replace(/[^\d]/g, "");
}

// === Dialog ===

let dialogResolve = null;

function showDialog(title, message, showInput) {
    return new Promise(resolve => {
        dialogResolve = resolve;
        document.getElementById("dialog-message").textContent = message;
        const inputWrapper = document.querySelector(".dialog-input-wrapper");
        const input = document.getElementById("dialog-input");
        if (showInput) {
            inputWrapper.classList.remove("hidden");
            input.value = "";
        } else {
            inputWrapper.classList.add("hidden");
        }
        document.getElementById("dialog-overlay").classList.remove("hidden");
        if (showInput) input.focus();
    });
}

function handleDialogConfirm() {
    document.getElementById("dialog-overlay").classList.add("hidden");
    const inputWrapper = document.querySelector(".dialog-input-wrapper");
    if (!inputWrapper.classList.contains("hidden")) {
        const val = document.getElementById("dialog-input").value.trim();
        dialogResolve(val || null);
    } else {
        dialogResolve(true);
    }
    dialogResolve = null;
}

function handleDialogCancel() {
    document.getElementById("dialog-overlay").classList.add("hidden");
    dialogResolve(null);
    dialogResolve = null;
}

// === Toast ===

let toastTimer = null;

function showToast(message, type) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = "toast " + type;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
        toast.classList.add("hidden");
    }, 2500);
}

// === Utility ===

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// === Event binding ===

function bindEvents() {
    document.getElementById("btn-save").addEventListener("click", handleSave);
    document.getElementById("profile-select").addEventListener("change", handleProfileSelect);
    document.getElementById("btn-save-profile").addEventListener("click", handleSaveProfile);
    document.getElementById("btn-update-profile").addEventListener("click", handleUpdateProfile);
    document.getElementById("btn-delete-profile").addEventListener("click", handleDeleteProfile);
    document.getElementById("btn-toggle-token").addEventListener("click", handleToggleToken);
    document.getElementById("f-timeout").addEventListener("input", handleTimeoutInput);
    document.getElementById("dialog-confirm").addEventListener("click", handleDialogConfirm);
    document.getElementById("dialog-cancel").addEventListener("click", handleDialogCancel);
}
```

- [ ] **Step 2: Commit**

```bash
git add ui/app.js
git commit -m "feat: add frontend interaction logic"
```

---

### Task 9: main.pyw — Entry point with single instance

**Files:**
- Create: `main.pyw`

- [ ] **Step 1: Implement the entry point**

```python
# main.pyw — Entry point for Claude Settings Manager
# Use .pyw extension to avoid console window on Windows

import sys
import os
import webview
from app.api import Api


def is_already_running():
    """Check if another instance is running using a lock file."""
    lock_path = os.path.join(os.path.expanduser("~"), ".claude", ".settings-manager.lock")
    try:
        # Try to create lock file exclusively
        if os.path.exists(lock_path):
            # Check if the PID in the lock file is still alive
            with open(lock_path, "r") as f:
                old_pid = f.read().strip()
            if old_pid:
                try:
                    os.kill(int(old_pid), 0)  # Signal 0 = check existence
                    return True  # Process exists
                except (OSError, ValueError):
                    pass  # Stale lock file
            os.remove(lock_path)
        # Write our PID
        with open(lock_path, "w") as f:
            f.write(str(os.getpid()))
        return False
    except OSError:
        return False


def remove_lock():
    """Remove the lock file on exit."""
    lock_path = os.path.join(os.path.expanduser("~"), ".claude", ".settings-manager.lock")
    try:
        os.remove(lock_path)
    except OSError:
        pass


def main():
    if is_already_running():
        print("Another instance is already running.")
        sys.exit(0)

    try:
        api = Api()
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "index.html")
        window = webview.create_window(
            title="Claude Settings Manager",
            url=ui_path,
            js_api=api,
            width=800,
            height=600,
            resizable=True,
            min_size=(600, 450),
        )
        webview.start()
    finally:
        remove_lock()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add main.pyw
git commit -m "feat: add entry point with single instance lock"
```

---

### Task 10: Integration test — Run the app manually

This task verifies the complete flow by running the application.

- [ ] **Step 1: Run the application**

Run: `python main.pyw`
Expected: A native window opens showing the settings form with values from `~/.claude/settings.json`

- [ ] **Step 2: Verify settings load correctly**

Check that all fields are populated from the current settings.json:
- Base URL = `https://ark.cn-beijing.volces.com/api/coding`
- Token is masked
- Three models = `GLM-5.1`
- Timeout = `3000000`
- Three switches are checked
- Plugin `superpowers@claude-plugins-official` is checked
- Marketplace shows `superpowers-marketplace`

- [ ] **Step 3: Test token toggle**

Click the eye icon next to Auth Token.
Expected: Token switches between masked and visible.

- [ ] **Step 4: Test Profile save**

1. Click "保存为 Profile"
2. Enter name "火山引擎 ARK"
3. Click confirm
Expected: Toast shows "Profile 已保存", dropdown now has "火山引擎 ARK"

- [ ] **Step 5: Test Profile load**

1. Change Base URL to something else (e.g. `https://test.com`)
2. Select "火山引擎 ARK" from dropdown
Expected: Base URL changes back to the profile's value. Other fields (switches, plugins) unchanged.

- [ ] **Step 6: Test save settings**

1. Make a change (e.g. modify a model name)
2. Click "保存配置"
Expected: Toast shows "配置已保存". Verify `~/.claude/settings.json` has the new value.

- [ ] **Step 7: Test delete profile**

1. Select "火山引擎 ARK"
2. Click "删除"
3. Confirm
Expected: Toast shows "Profile 已删除", dropdown no longer has the entry.

- [ ] **Step 8: Test timeout validation**

Type "abc" into Timeout field.
Expected: Input only accepts digits, "abc" is removed.

- [ ] **Step 9: Test single instance**

With the app already running, try `python main.pyw` again.
Expected: Second instance exits immediately; first window remains active.

- [ ] **Step 10: Restore original settings if modified**

If settings.json was changed during testing, restore it to the original values.

- [ ] **Step 11: Final commit if any fixes were needed**

```bash
git add -A
git commit -m "fix: integration test fixes"
```

---

## Self-Review Checklist

- [x] **Spec coverage**: All requirements from settings-editor spec (8 requirements) and profile-manager spec (6 requirements) are covered by Tasks 2-9.
- [x] **Placeholder scan**: No TBD/TODO/vague steps. All code is complete.
- [x] **Type consistency**: `load_settings()` returns dict, `save_settings()` returns str|None, `list_profiles()` returns list[dict], profile operations return str|None — consistent across settings.py, profiles.py, api.py, and app.js.
