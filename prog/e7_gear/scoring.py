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
    newcols = {}
    for code in gear_rating_lookup.code.values:
        col = [0] * len(df)
        for in_col in subs_cols:
            temp_df = df.copy()
            temp_df[["b1", "b2"]] = pd.DataFrame(temp_df[in_col].tolist(), index=temp_df.index)
            m = np.where(temp_df["b1"] == grl["stat_in"][code], 1, 0)
            t = m * np.where(np.isnan(temp_df["b2"]), 0, temp_df["b2"])
            col += t
        newcols[grl["stat"][code]] = col
    return pd.concat([df, pd.DataFrame(newcols, index=df.index)], axis=1)


def spd_potential(p, g, s):
    v1 = np.where((s == 0) & (g > 0) & (p > g), 2, 0)
    v2 = np.where(s == 1, max(min(p, p - g), np.where(p > 0, 1, 0)), 0)
    return v1 + v2


def item_potential(df):
    GR = 0
    gear_lvl = df["level"]
    main_type = df["mainStat"][0]
    main_val = df["mainStat"][1]
    df["main_tp"] = main_type
    df["main_val"] = main_val
    main_rating = gear_tier[gear_tier.Level == gear_lvl]["X_Factor"].values[0]
    main_rating = np.where(
        (df["Type"] >= 3) & (main_type in ["Atk", "HP", "Def"]),
        main_rating * st.FLAT_MAIN,
        main_rating,
    )
    rarity = df["grade"]
    for stat in gear_rating_lookup.stat.values:
        val = df[stat]
        x = gear_rating_lookup[gear_rating_lookup.stat == stat]["multiplier"].values
        z = x[0] / 9
        rating = val * z * np.where(stat in ["ATK", "HP", "DEF"], st.FLAT_SUB, 1)
        GR = GR + rating
    df["GR"] = GR
    spd_ind = np.where(df["SPD"] > 0, 1, 0)
    spd_val = df["SPD"]
    enhance = df["enhance"]
    pwrup = int((15 - enhance) / 3)
    minp = GR + pwrup / 18 * np.where(gear_lvl < 86, 0.87, 1) * np.where(gear_lvl < 58, 0.87, 1)
    df["minp"] = minp
    maxp = (
        GR
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
    df["efficiency"] = int(main_rating * 44 + GR * 66 + np.where(main_type == "Spd", 2, 0) + spd_val * 0.1)
    df["max_eff"] = int(main_rating * 44 + maxp * 66 + np.where(main_type == "Spd", 2, 0) + spd_val * 0.1)
    df["current_eff"] = GR * 6.6 + main_rating * grt.gear_scaling[enhance] / 5 * 4.4
    return df
