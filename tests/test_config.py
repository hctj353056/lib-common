import pytest
from lib_common import config


def test_env_bool(monkeypatch):
    monkeypatch.setenv("TEST_FLAG", "yes")
    assert config.env_bool("TEST_FLAG") is True
    monkeypatch.setenv("TEST_FLAG", "no")
    assert config.env_bool("TEST_FLAG", True) is False
    monkeypatch.setenv("TEST_FLAG", "maybe")
    with pytest.raises(ValueError):
        config.env_bool("TEST_FLAG")


def test_settings_prefix(monkeypatch):
    monkeypatch.setenv("APP_TOKEN", "abc")
    settings = config.Settings(prefix="APP_")
    assert settings.require("TOKEN") == "abc"
