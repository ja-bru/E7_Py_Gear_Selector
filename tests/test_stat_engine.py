"""Tests for hero stat calculation."""

import pandas as pd

from e7_gear.combinator import get_set_bonus
from e7_gear.stat_engine import bonus_eqp_sum, get_combo_stats, mainst_sum, set_sum, subst_sum


def _single_combo_df(scored_items_df):
    gear_ids = ["spd_w", "spd_h", "spd_a", "spd_n", "crt_r", "crt_b"]
    row = pd.DataFrame([{"0": gear_ids[0], "1": gear_ids[1], "2": gear_ids[2],
                         "3": gear_ids[3], "4": gear_ids[4], "5": gear_ids[5], "Gear": ()}])
    return get_set_bonus(row, scored_items_df)


def test_subst_sum_totals_substats(scored_items_df):
    combo = _single_combo_df(scored_items_df)
    totals = subst_sum(combo, scored_items_df)

    assert totals.iloc[0]["SPD"] > 0
    assert totals.iloc[0]["CChance"] > 0
    assert totals.iloc[0]["GR"] > 0


def test_mainst_sum_includes_flat_weapon_attack(scored_items_df):
    combo = _single_combo_df(scored_items_df)
    mains = mainst_sum(combo, scored_items_df)

    assert mains.iloc[0]["ATK"] > 0


def test_set_sum_applies_speed_set_bonus():
    combo = pd.DataFrame(
        [{"Set_1": "Speed", "Set_2": "Critical", "Set_3": None, "Complete": 1}]
    )
    bonuses = set_sum(combo)

    assert bonuses.iloc[0]["SPD"] == 25


def test_get_combo_stats_produces_core_stats(scored_items_df, kayron_hero_df, general_build_target):
    combo = _single_combo_df(scored_items_df)
    hero_slice = kayron_hero_df[kayron_hero_df.Name == "Kayron"]
    hero_ee = bonus_eqp_sum(hero_slice)

    stats = get_combo_stats(
        combo,
        kayron_hero_df,
        mainst_sum(combo, scored_items_df),
        subst_sum(combo, scored_items_df),
        set_sum(combo),
        hero_ee,
        "Kayron",
        general_build_target,
    )

    row = stats.iloc[0]
    assert row["SPD"] >= 150
    assert row["CRIT"] >= 50
    assert row["ATK"] > 1000
    assert row["WW"] > 0


def test_bonus_eqp_sum_defaults_missing_stats(kayron_hero_df):
    hero_ee = bonus_eqp_sum(kayron_hero_df[kayron_hero_df.Name == "Kayron"])

    assert hero_ee["CChance"] == 12.0
    assert hero_ee["AtkP"] == 0
