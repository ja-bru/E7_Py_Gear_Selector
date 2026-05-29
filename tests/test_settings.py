"""Tests for runtime settings."""

import config as st
from e7_gear.settings import Settings, verify_settings


def test_settings_round_trip():
    settings = Settings.from_config()
    settings.gear_limit = 7
    settings.flat_sub = 0.75
    settings.apply_to_config()

    assert st.GEAR_LIMIT == 7
    assert st.FLAT_SUB == 0.75


def test_settings_validate_clamps_invalid_values():
    settings = Settings(
        min_level=55,
        gear_enhance=99,
        flat_sub=1.5,
        flat_main=-0.2,
    )
    settings.validate()

    assert settings.min_level == 50
    assert settings.gear_enhance == 12
    assert settings.flat_sub == 0.8
    assert settings.flat_main == 0.5


def test_verify_settings_syncs_config(monkeypatch):
    import config as st

    monkeypatch.setattr(st, "GEAR_ENHANCE", "invalid")
    result = verify_settings()

    assert isinstance(result, Settings)
    assert st.GEAR_ENHANCE == 12
