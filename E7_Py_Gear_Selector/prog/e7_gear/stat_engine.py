"""Hero stat calculation from gear combinations."""

import numpy as np
import pandas as pd

import config as st
import gear_ref_table as grt
from e7_gear.tables import gear_rating_lookup, grl, set_df


def enhance_mult(x):
    y = st.GEAR_ENHANCE
    return np.where((x < y), grt.gear_scaling[y] / x.map(grt.gear_scaling), 1)


def set_sum(df):
    setst_df = df.copy()
    for stat in np.unique(set_df[set_df.Bonus_Stat != "NA"].Bonus_Stat.values):
        mult = [0] * len(setst_df)
        temp_set = set_df[set_df.Bonus_Stat == stat]
        mult += np.where(setst_df["Set_1"].isin(temp_set.Set_Nm), 1, 0)
        mult += np.where(setst_df["Set_2"].isin(temp_set.Set_Nm), 1, 0)
        mult += np.where(setst_df["Set_3"].isin(temp_set.Set_Nm), 1, 0)
        temp_bonus = temp_set.Bonus.values * mult
        setst_df[stat] = temp_bonus
    return setst_df


def subst_sum(df, item_df):
    subst_cols = list(gear_rating_lookup.stat)
    subst_cols.extend(["id", "GR"])
    subst_df = df.copy()
    for subst in subst_cols:
        subst_df[subst] = 0
    for col in range(0, 6):
        subst_df = pd.merge(
            subst_df,
            item_df[subst_cols],
            how="left",
            left_on=[str(col)],
            right_on=["id"],
            suffixes=("", "_" + str(col)),
        )
    for subst in gear_rating_lookup.stat.values:
        subst_df[subst] = (
            subst_df[subst + "_0"]
            + subst_df[subst + "_1"]
            + subst_df[subst + "_2"]
            + subst_df[subst + "_3"]
            + subst_df[subst + "_4"]
            + subst_df[subst + "_5"]
        )
    drop_cols = []
    for subst in subst_cols:
        for suffix in ["_0", "_1", "_2", "_3", "_4", "_5"]:
            drop_cols.append(subst + suffix)
    drop_cols.extend(["id", "Gear"])
    subst_df.drop(columns=drop_cols, axis=1, inplace=True)
    return subst_df


def mainst_sum(df, item_df):
    mainst_df = df.copy()
    mainst_cols = ["id", "main_tp", "main_val", "level", "enhance"]
    for subst in mainst_cols:
        mainst_df[subst] = 0
    for subst in gear_rating_lookup.stat.values:
        mainst_df[subst] = 0
    for col in range(0, 6):
        mainst_df = pd.merge(
            mainst_df,
            item_df[mainst_cols],
            how="left",
            left_on=[str(col)],
            right_on=["id"],
            suffixes=("", "_" + str(col)),
        )
    for stat in gear_rating_lookup.stat.values:
        for i in range(0, 6):
            col1 = "main_tp_" + str(i)
            col2 = "main_val_" + str(i)
            col3 = "enhance_" + str(i)
            enh_mult = enhance_mult(mainst_df[col3])
            mainst_df[stat] += np.where(
                mainst_df[col1].map(grt.s_map) == stat,
                (mainst_df[col2] * enh_mult).astype(int),
                0,
            )
    drop_cols = []
    for subst in ["id", "level", "main_val", "main_tp", "enhance"]:
        for suffix in ["_0", "_1", "_2", "_3", "_4", "_5"]:
            drop_cols.append(subst + suffix)
    drop_cols.extend(["id", "Gear", "main_tp", "main_val", "level", "enhance"])
    mainst_df.drop(columns=drop_cols, axis=1, inplace=True)
    return mainst_df


def bonus_eqp_sum(hero_df):
    bonus_eqp_df = hero_df["Name"].copy()
    hero_bonus = hero_df["BonusStats"].values[0]
    for stat in np.unique(gear_rating_lookup.stat_in.values):
        try:
            bonus_eqp_df[stat] = hero_bonus[stat]
        except KeyError:
            bonus_eqp_df[stat] = 0
    return bonus_eqp_df


def pull_hero_stat_format(df_flag, stat, input_set):
    if df_flag == 1:
        return input_set[stat].values
    return input_set[stat].values[0]


def get_combo_stats(df, df_hero, mainst_df, subst_df, setst_df, hero_ee, char, target_stats):
    if char == "all":
        df["Char"] = df_hero["Name"]
        df_hero_stat = df_hero
    else:
        df["Char"] = [char] * len(df)
        df_hero_stat = df_hero[df_hero.Name == char]
    df_flag = 1 if len(df) > 1 else 0
    df["ATK"] = (
        pull_hero_stat_format(df_flag, grt.e7api_map["atk"], df_hero_stat)
        * (100 + mainst_df["ATK%"] + subst_df["ATK%"] + setst_df["ATK"] + hero_ee["AtkP"])
        / 100
        + mainst_df["ATK"]
        + subst_df["ATK"]
        + hero_ee["Atk"]
    ).astype(int)
    df["HP"] = (
        pull_hero_stat_format(df_flag, grt.e7api_map["hp"], df_hero_stat)
        * (100 + mainst_df["HP%"] + subst_df["HP%"] + setst_df["HP"] + hero_ee["HPP"])
        / 100
        + mainst_df["HP"]
        + subst_df["HP"]
        + hero_ee["HP"]
    ).astype(int)
    df["DEF"] = (
        pull_hero_stat_format(df_flag, grt.e7api_map["def"], df_hero_stat)
        * (100 + mainst_df["DEF%"] + subst_df["DEF%"] + setst_df["DEF"] + hero_ee["DefP"])
        / 100
        + mainst_df["DEF"]
        + subst_df["DEF"]
        + hero_ee["Def"]
    ).astype(int)
    df["SPD"] = (
        pull_hero_stat_format(df_flag, grt.e7api_map["spd"], df_hero_stat)
        * ((100 + setst_df["SPD"].values) / 100)
        + mainst_df["SPD"]
        + subst_df["SPD"]
        + hero_ee["Spd"]
    ).astype(int)
    df["CRIT"] = np.minimum(
        (
            pull_hero_stat_format(df_flag, grt.e7api_map["crit"], df_hero_stat) * 100
            + mainst_df["CRIT"]
            + subst_df["CRIT"]
            + setst_df["CRIT"]
            + hero_ee["CChance"]
        ).astype(int),
        100,
    )
    df["CDMG"] = (
        pull_hero_stat_format(df_flag, grt.e7api_map["cdmg"], df_hero_stat) * 100
        + mainst_df["CDMG"]
        + subst_df["CDMG"]
        + setst_df["CDMG"]
        + hero_ee["CDmg"]
    ).astype(int)
    df["EFF"] = (
        pull_hero_stat_format(df_flag, grt.e7api_map["eff"], df_hero_stat) * 100
        + mainst_df["EFF"]
        + subst_df["EFF"]
        + setst_df["EFF"]
        + hero_ee["Eff"]
    ).astype(int)
    df["RES"] = (
        pull_hero_stat_format(df_flag, grt.e7api_map["res"], df_hero_stat) * 100
        + mainst_df["RES"]
        + subst_df["RES"]
        + setst_df["RES"]
        + hero_ee["Res"]
    ).astype(int)
    cp1 = round(
        (
            (df["ATK"] * 1.6 + df["ATK"] * 1.6 * df["CRIT"] * df["CDMG"] / 10000)
            * (1 + (df["SPD"] - 45) * 0.02)
            + df["HP"]
            + df["DEF"] * 9.3
        )
        * (1 + (df["RES"] + df["EFF"]) / 400),
        0,
    )
    cp2 = 1 + 0.08 * df_hero_stat[grt.e7api_map["sc"]].values[0] + 0.02 * df_hero_stat[grt.e7api_map["ee"]].values[0]
    df["CP"] = round(cp1 * cp2, 0)
    df["Dmg_Rating"] = (
        (
            df["ATK"]
            / 2500
            * (df["CRIT"] / 100 * df["CDMG"] / 100 + (100 - df["CRIT"]) / 100)
            * df["SPD"]
            / 150
        )
        * 10
    ).astype(int)
    df["EHP"] = (df["HP"] * (1 + df["DEF"] / 300) / 100).astype(int)
    df["PI"] = (
        df["ATK"] / df_hero_stat[grt.e7api_map["atk"]].values[0] / grl["max_t7"][0]
        + df["SPD"] / df_hero_stat[grt.e7api_map["spd"]].values[0] / grl["max_t7"][2]
        + (df["CRIT"] - df_hero_stat[grt.e7api_map["crit"]].values[0]) / 100 / grl["max_t7"][3]
        + (df["CDMG"] - df_hero_stat[grt.e7api_map["cdmg"]].values[0]) / 100 / grl["max_t7"][4]
        + df["HP"] / df_hero_stat[grt.e7api_map["hp"]].values[0] / grl["max_t7"][5]
        + df["DEF"] / df_hero_stat[grt.e7api_map["def"]].values[0] / grl["max_t7"][7]
        + (df["EFF"] - df_hero_stat[grt.e7api_map["eff"]].values[0]) / 100 / grl["max_t7"][9]
        + (df["RES"] - df_hero_stat[grt.e7api_map["res"]].values[0]) / 100 / grl["max_t7"][10]
    ).astype(int)
    df["GR"] = subst_df["GR"] / 6
    df["WW"] = round(
        df["ATK"] / df_hero_stat[grt.e7api_map["atk"]].values[0] / grl["max_t7"][0] * target_stats["ATK"]["Weight"]
        + df["SPD"] / df_hero_stat[grt.e7api_map["spd"]].values[0] / grl["max_t7"][2] * target_stats["SPD"]["Weight"]
        + (df["CRIT"] - df_hero_stat[grt.e7api_map["crit"]].values[0])
        / 100
        / grl["max_t7"][3]
        * target_stats["CRIT"]["Weight"]
        + (df["CDMG"] - df_hero_stat[grt.e7api_map["cdmg"]].values[0])
        / 100
        / grl["max_t7"][4]
        * target_stats["CDMG"]["Weight"]
        + df["HP"] / df_hero_stat[grt.e7api_map["hp"]].values[0] / grl["max_t7"][5] * target_stats["HP"]["Weight"]
        + df["DEF"] / df_hero_stat[grt.e7api_map["def"]].values[0] / grl["max_t7"][7] * target_stats["DEF"]["Weight"]
        + (df["EFF"] - df_hero_stat[grt.e7api_map["eff"]].values[0])
        / 100
        / grl["max_t7"][9]
        * target_stats["EFF"]["Weight"]
        + (df["RES"] - df_hero_stat[grt.e7api_map["res"]].values[0])
        / 100
        / grl["max_t7"][10]
        * target_stats["RES"]["Weight"],
        2,
    )
    df["Element"] = df_hero_stat[grt.e7api_map["element"]]
    df["Role"] = df_hero_stat[grt.e7api_map["role"]]
    return df
