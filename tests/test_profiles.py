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
