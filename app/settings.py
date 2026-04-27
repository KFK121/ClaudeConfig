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
