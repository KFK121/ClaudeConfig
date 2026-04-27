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
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        return str(e)
