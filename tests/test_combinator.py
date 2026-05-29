"""Tests for gear combination search."""

import pandas as pd

from e7_gear.combinator import (
    _append_combo,
    _flatten_gear,
    build_set_gear_index,
    estimate_set_combination_count,
    gen_input_sets,
    get_set_bonus,
    set_combination_iterate,
)
from e7_gear.tables import l2, l4, set_2, set_4


def test_flatten_gear_four_plus_two_set():
    gear = (("spd_w", "spd_h", "spd_a", "spd_n"), ("crt_r", "crt_b"))
    assert _flatten_gear(gear) == ["crt_b", "crt_r", "spd_a", "spd_h", "spd_n", "spd_w"]


def test_flatten_gear_three_two_sets():
    gear = (("a", "b"), ("c", "d"), ("e", "f"))
    assert _flatten_gear(gear) == ["a", "b", "c", "d", "e", "f"]


def test_gen_input_sets_autofills_two_pieces():
    include = gen_input_sets(["Speed"], [], autofill=0)
    assert "Speed" in include
    assert len(include) >= 2


def test_get_set_bonus_detects_complete_sets(scored_items_df):
    row = pd.DataFrame(
        [
            {
                "0": "spd_w",
                "1": "spd_h",
                "2": "spd_a",
                "3": "spd_n",
                "4": "crt_r",
                "5": "crt_b",
            }
        ]
    )
    result = get_set_bonus(row, scored_items_df)

    assert result.iloc[0]["Complete"] == 1
    sets = {result.iloc[0]["Set_1"], result.iloc[0]["Set_2"], result.iloc[0]["Set_3"]} - {None}
    assert sets == {"Speed", "Critical"}


def test_append_combo_deduplicates_identical_gear():
    rows = []
    seen = set()
    gear = (("a", "b", "c", "d"), ("e", "f"))

    _append_combo(rows, seen, "Speed", "Critical", None, gear)
    _append_combo(rows, seen, "Critical", "Speed", None, gear)

    assert len(rows) == 1


def test_set_combination_iterate_respects_force_four_set(scored_items_df, fast_test_config):
    include = ["Speed", "Critical"]
    set4_list = set_4[set_4.Set_Nm.isin(include)].Set_Nm.values
    set2_list = set_2[set_2.Set_Nm.isin(include)].Set_Nm.values
    gear_index = build_set_gear_index(scored_items_df, l4, l2)

    all_combos = set_combination_iterate(gear_index, set4_list, set2_list, force_4set=0)
    four_only = set_combination_iterate(gear_index, set4_list, set2_list, force_4set=1)

    assert len(all_combos) >= len(four_only)
    assert len(all_combos) > 0


def test_estimate_count_matches_iterate_length(scored_items_df, fast_test_config):
    include = ["Speed", "Critical"]
    set4_list = set_4[set_4.Set_Nm.isin(include)].Set_Nm.values
    set2_list = set_2[set_2.Set_Nm.isin(include)].Set_Nm.values
    gear_index = build_set_gear_index(scored_items_df, l4, l2)

    estimate = estimate_set_combination_count(scored_items_df, set4_list, set2_list, force_4set=0)
    combos = set_combination_iterate(gear_index, set4_list, set2_list, force_4set=0)

    assert estimate >= len(combos)
