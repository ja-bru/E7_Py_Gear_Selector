"""Tests for I/O helpers."""

import pytest

from e7_gear.io import hero_json_to_df


def test_hero_json_to_df_raises_on_missing_character_data():
    data = {
        "heroes": [{"Name": "NotARealHero", "Lvl": 60, "BonusStats": {}}],
        "items": [],
    }
    with pytest.raises(ValueError, match="Character data missing"):
        hero_json_to_df(["NotARealHero"], data)
