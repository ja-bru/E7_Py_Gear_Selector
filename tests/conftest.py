"""Shared pytest fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PROG_DIR = ROOT / "prog"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

if str(PROG_DIR) not in sys.path:
    sys.path.insert(0, str(PROG_DIR))


SLOT_NAMES = ["Weapon", "Helmet", "Armor", "Necklace", "Ring", "Boots"]


def make_gear_item(
    gear_id: str,
    type_idx: int,
    set_nm: str,
    main_stat: list,
    sub_stats: list,
    *,
    enhance: int = 15,
    level: int = 85,
) -> dict:
    subs = sub_stats + [["X", 0]] * (4 - len(sub_stats))
    return {
        "hero": "",
        "enhance": enhance,
        "slot": SLOT_NAMES[type_idx],
        "level": level,
        "set": set_nm,
        "rarity": "Epic",
        "mainStat": main_stat,
        "subStat1": subs[0],
        "subStat2": subs[1],
        "subStat3": subs[2],
        "subStat4": subs[3],
        "id": gear_id,
        "locked": False,
    }


@pytest.fixture
def minimal_master_data() -> dict:
    """Six pieces: Speed 4pc (slots 0-3) + Critical 2pc (slots 4-5)."""
    items = [
        make_gear_item("spd_w", 0, "Speed", ["Atk", 500], [["Spd", 10], ["AtkP", 12]]),
        make_gear_item("spd_h", 1, "Speed", ["HP", 2700], [["Spd", 8], ["HPP", 14]]),
        make_gear_item("spd_a", 2, "Speed", ["Def", 300], [["Spd", 7], ["CDmg", 12]]),
        make_gear_item("spd_n", 3, "Speed", ["CDmg", 65], [["Spd", 6], ["CChance", 8]]),
        make_gear_item("crt_r", 4, "Critical", ["AtkP", 60], [["CChance", 12], ["CDmg", 18]]),
        make_gear_item("crt_b", 5, "Critical", ["Spd", 40], [["CChance", 10], ["AtkP", 9]]),
        # Alternate boots so the optimizer has a choice on slot 5 when GEAR_LIMIT > 1
        make_gear_item("crt_b2", 5, "Critical", ["Spd", 38], [["CChance", 6], ["CDmg", 20]]),
    ]
    heroes = [
        {
            "Name": "Kayron",
            "Lvl": 60,
            "BonusStats": {"Atk": 0, "HP": 0, "CChance": 12.0},
        }
    ]
    return {"heroes": heroes, "items": items}


@pytest.fixture
def scored_items_df(minimal_master_data):
    import fx_lib as fx
    from e7_gear.scoring import score_all_items

    df = fx.item_json_to_df(minimal_master_data)
    df = fx.gear_stats(df)
    return score_all_items(df)


@pytest.fixture
def kayron_hero_df(minimal_master_data):
    import fx_lib as fx

    df_hero, _ = fx.hero_json_to_df(["Kayron"], minimal_master_data)
    return df_hero


@pytest.fixture
def general_build_target():
    return {
        "input_sets": ["Speed", "Critical"],
        "exclude_sets": [],
        "Force_4Set": 0,
        "Main_Stats": [[], [], []],
        "include_sets": ["Speed", "Critical"],
        "ATK": {"Min": 0, "Max": 999999, "Weight": 1},
        "CRIT": {"Min": 0, "Max": 100, "Weight": 2},
        "CDMG": {"Min": 150, "Max": 999, "Weight": 2},
        "SPD": {"Min": 150, "Max": 999, "Weight": 3},
        "HP": {"Min": 0, "Max": 99999, "Weight": 1},
        "DEF": {"Min": 0, "Max": 9999, "Weight": 1},
        "EFF": {"Min": 0, "Max": 100, "Weight": 1},
        "RES": {"Min": 0, "Max": 100, "Weight": 1},
        "Dmg_Rating": {"Min": 0, "Max": 999999, "Weight": 1},
        "EHP": {"Min": 0, "Max": 999999, "Weight": 1},
        "Prio": ["SPD", "CRIT"],
    }


@pytest.fixture
def fast_test_config(monkeypatch):
    import config as st

    monkeypatch.setattr(st, "GEAR_LIMIT", 2)
    monkeypatch.setattr(st, "AUTO_ADJ_GEAR_LIMIT", 0)
    monkeypatch.setattr(st, "NO_EQUIPPED_GEAR", 1)
    monkeypatch.setattr(st, "KEEP_CURR_GEAR", 0)


@pytest.fixture
def golden_optimizer_spec() -> dict:
    with open(FIXTURES_DIR / "golden_optimizer.json", encoding="utf-8") as fp:
        return json.load(fp)
