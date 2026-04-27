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
            continue
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
