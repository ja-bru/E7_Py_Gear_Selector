"""Gear scoring and input validation."""

import math

import numpy as np
import pandas as pd

import config as st
import gear_ref_table as grt
from e7_gear.tables import gear_rating_lookup, gear_tier, grl, subs_cols


def verify_main_stats(gear_lvl, enhance, main_type, main_val, gear_type):
    main_error = 0
    if (gear_type == 0) & (main_type != "Atk"):
        main_error = 1
    if (gear_type == 1) & (main_type != "HP"):
        main_error = 1
    if (gear_type == 2) & (main_type != "Def"):
        main_error = 1
    if (gear_type == 3) & (main_type in (["Eff", "Res", "Spd"])):
        main_error = 1
    if (gear_type == 4) & (main_type in (["CChance", "CDmg", "Spd"])):
        main_error = 1
    if (gear_type == 5) & (main_type in (["CChance", "CDmg", "Eff", "Res"])):
        main_error = 1
    base_stat = gear_tier[(gear_tier.Level == gear_lvl)][main_type].values[0]
    projected_stat = base_stat * grt.gear_scaling[enhance]
    if (main_val > projected_stat * 1.01) | (main_val < projected_stat * 0.88):
        main_error += 1
    return main_error * 10


def verify_item_input(df):
    check_error = 0
    gear_lvl = df["level"]
    enhance = df["enhance"]
    tier = gear_tier[gear_tier.Level == gear_lvl]["Tier"].values[0]
    main_type = df["mainStat"][0]
    main_val = df["mainStat"][1]
    gear_type = df["Type"]
    check_error += verify_main_stats(gear_lvl, enhance, main_type, main_val, gear_type)
    grt_col = "max_" + tier.lower()
    pwrup = math.floor(enhance / 3)
    tot_pwr = 0
    for stat in gear_rating_lookup.stat.values:
        sub_limit = gear_rating_lookup[gear_rating_lookup.stat == stat][grt_col].values
        if stat in (["CRIT", "CDMG", "HP%", "ATK%", "DEF%", "EFF", "RES"]):
            sub_limit = sub_limit * 100
        val = df[stat]
        tot_pwr += math.ceil(val / sub_limit)
        sub_pred = (1 + pwrup) * sub_limit
        if sub_pred < val:
            check_error += 1
        if (val > 0) & (gear_rating_lookup[gear_rating_lookup.stat == stat]["stat_in"].values == main_type):
            check_error += 1
    if (4 - df["grade"] + pwrup) < tot_pwr:
        check_error += 100
    return check_error


def gear_stats(df):
    """Extract substat values into stat columns (vectorized over substats)."""
    newcols = {grl["stat"][code]: np.zeros(len(df)) for code in gear_rating_lookup.code.values}
    for in_col in subs_cols:
        parsed = pd.DataFrame(df[in_col].tolist(), index=df.index, columns=["b1", "b2"])
        values = parsed["b2"].fillna(0).to_numpy()
        for code in gear_rating_lookup.code.values:
            stat_in = grl["stat_in"][code]
            mask = (parsed["b1"] == stat_in).to_numpy()
            newcols[grl["stat"][code]] += np.where(mask, values, 0)
    return pd.concat([df, pd.DataFrame(newcols, index=df.index)], axis=1)


def spd_potential(p, g, s):
    v1 = np.where((s == 0) & (g > 0) & (p > g), 2, 0)
    v2 = np.where(s == 1, np.maximum(np.minimum(p, p - g), np.where(p > 0, 1, 0)), 0)
    return v1 + v2


def score_all_items(df: pd.DataFrame) -> pd.DataFrame:
    """Vectorized gear potential scoring for an entire inventory dataframe."""
    df = df.copy()
    main_parts = pd.DataFrame(df["mainStat"].tolist(), index=df.index, columns=["main_tp", "main_val"])
    df["main_tp"] = main_parts["main_tp"]
    df["main_val"] = main_parts["main_val"]

    tier_factors = gear_tier.set_index("Level")["X_Factor"]
    main_rating = df["level"].map(tier_factors).to_numpy(dtype=float)
    flat_mask = (df["Type"].to_numpy() >= 3) & df["main_tp"].isin(["Atk", "HP", "Def"]).to_numpy()
    main_rating = np.where(flat_mask, main_rating * st.FLAT_MAIN, main_rating)

    gr_total = np.zeros(len(df))
    for stat in gear_rating_lookup.stat.values:
        if stat not in df.columns:
            continue
        val = df[stat].to_numpy(dtype=float)
        mult = gear_rating_lookup.loc[gear_rating_lookup.stat == stat, "multiplier"].iloc[0] / 9
        weight = st.FLAT_SUB if stat in ["ATK", "HP", "DEF"] else 1
        gr_total += val * mult * weight
    df["GR"] = gr_total

    gear_lvl = df["level"].to_numpy()
    enhance = df["enhance"].to_numpy()
    main_type = df["main_tp"].to_numpy()
    rarity = df["grade"].to_numpy()
    spd_ind = (df["SPD"].to_numpy() > 0).astype(int)
    spd_val = df["SPD"].to_numpy(dtype=float)
    pwrup = ((15 - enhance) // 3).astype(int)

    minp = gr_total + pwrup / 18 * np.where(gear_lvl < 86, 0.87, 1) * np.where(gear_lvl < 58, 0.87, 1)
    df["minp"] = minp
    maxp = (
        gr_total
        + pwrup / 9
        * np.where(gear_lvl < 86, 0.87, 1)
        * np.where(gear_lvl < 72, 0.87, 1)
        * np.where(gear_lvl < 58, 0.87, 1)
    )
    df["maxp"] = maxp
    df["spdp"] = (
        np.where(main_type == "Spd", 0, spd_potential(pwrup, rarity, spd_ind))
        * np.where(gear_lvl > 88, 5, np.where(gear_lvl > 57, 4, 3))
        + spd_val
    )
    df["rating"] = main_rating * 1.4 + (minp + maxp) / 2 + np.where(main_type == "Spd", 0.2, 0) + spd_val * 0.01

    eff_base = main_rating * 44 + gr_total * 66 + np.where(main_type == "Spd", 2, 0) + spd_val * 0.1
    df["efficiency"] = eff_base.astype(int)
    df["max_eff"] = (main_rating * 44 + maxp * 66 + np.where(main_type == "Spd", 2, 0) + spd_val * 0.1).astype(int)
    scaling = pd.Series(enhance, index=df.index).map(grt.gear_scaling).to_numpy(dtype=float)
    df["current_eff"] = gr_total * 6.6 + main_rating * scaling / 5 * 4.4
    return df


def item_potential(df):
    """Score a single gear row (kept for compatibility)."""
    return score_all_items(df.to_frame().T).iloc[0]
