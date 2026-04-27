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
