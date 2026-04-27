import json
import pytest
from pathlib import Path
from app.settings import load_settings, get_settings_path, save_settings


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
        settings_file.write_text("{}")
        monkeypatch.setattr("app.settings.get_settings_path", lambda: settings_file)
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
        from unittest.mock import patch
        with patch("app.settings.Path.write_text", side_effect=PermissionError("denied")):
            save_settings({"env": {"ANTHROPIC_BASE_URL": "https://new.com"}, "enabledPlugins": {}})
        still_there = json.loads(settings_file.read_text(encoding="utf-8"))
        assert still_there["env"]["ANTHROPIC_BASE_URL"] == "https://original.com"
