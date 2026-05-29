"""Tests for gear scoring and validation."""

import pandas as pd

from e7_gear.scoring import gear_stats, score_all_items, verify_item_input, verify_main_stats


def test_verify_main_stats_rejects_wrong_weapon_main():
    assert verify_main_stats(85, 15, "HP", 2700, 0) > 0


def test_verify_main_stats_accepts_valid_weapon():
    assert verify_main_stats(85, 15, "Atk", 500, 0) == 0


def test_gear_stats_extracts_substats(minimal_master_data):
    import fx_lib as fx

    df = fx.item_json_to_df(minimal_master_data)
    scored = gear_stats(df)

    spd_row = scored[scored.id == "spd_w"].iloc[0]
    assert spd_row["SPD"] == 10
    assert spd_row["AtkP"] == 12


def test_score_all_items_adds_rating_columns(scored_items_df):
    df = scored_items_df

    for col in ["GR", "rating", "efficiency", "max_eff", "current_eff", "main_tp"]:
        assert col in df.columns
    assert df["efficiency"].notna().all()
    assert (df["rating"] > 0).all()


def test_score_all_items_matches_row_apply(scored_items_df):
    from e7_gear.scoring import item_potential

    row = scored_items_df.iloc[0]
    single = item_potential(row.copy())

    assert single["efficiency"] == row["efficiency"]
    assert single["rating"] == row["rating"]


def test_verify_item_input_flags_duplicate_main_sub(scored_items_df):
    row = scored_items_df[scored_items_df.id == "spd_w"].iloc[0].copy()
    row["CRIT"] = 0
    row["mainStat"] = ["CChance", 8]
    row["subStat1"] = ["CChance", 8]

    assert verify_item_input(row) > 0
