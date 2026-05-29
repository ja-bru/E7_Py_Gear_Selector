"""Golden-file style integration test for optimize_hero."""

from e7_gear.optimizer import optimize_hero


def test_optimize_hero_golden(
    scored_items_df,
    kayron_hero_df,
    general_build_target,
    fast_test_config,
    golden_optimizer_spec,
):
    scored_items_df = scored_items_df.copy()
    scored_items_df["reco"] = ""

    result = optimize_hero(
        golden_optimizer_spec["char"],
        scored_items_df,
        kayron_hero_df,
        general_build_target,
        build=golden_optimizer_spec["build"],
        force_4set=golden_optimizer_spec["force_4set"],
    )

    assert result is not None
    assert len(result.sc_output) >= golden_optimizer_spec["min_combo_count"]
    assert len(result.sc_output) <= golden_optimizer_spec["max_combo_count"]

    top = result.odf.loc[result.idx_reco]
    top_gear = sorted(result.odf.loc[result.idx_reco, "gear_list"])

    assert top["SPD"] >= golden_optimizer_spec["min_spd"]
    assert top["CRIT"] >= golden_optimizer_spec["min_crit"]

    for gear_id in golden_optimizer_spec["required_gear_ids"]:
        assert gear_id in top_gear
    assert len(set(top_gear) & set(golden_optimizer_spec["boot_options"])) == 1
    assert len(top_gear) == 6
    assert len(set(top_gear)) == 6
