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
