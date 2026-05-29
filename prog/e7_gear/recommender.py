"""Build resolution and gear recommendation."""

import numpy as np
import pandas as pd

import config as st
from e7_gear.combinator import gen_input_sets
from e7_gear.models import BuildConfig
from e7_gear.tables import set_4, set_df


def resolve_build(char: str, target_stats: dict) -> tuple[str, BuildConfig]:
    if char in target_stats:
        build = char
    elif char in target_stats.get("Type", {}):
        build = target_stats["Type"][char]
    else:
        build = "General"
    return build, target_stats[build]


def prepare_hero_target(char: str, target_stats: dict) -> tuple[str, BuildConfig]:
    """Resolve build template and populate include_sets on the hero target."""
    build, hero_target = resolve_build(char, target_stats)
    include_sets = gen_input_sets(hero_target["input_sets"], hero_target["exclude_sets"])
    hero_target["include_sets"] = include_sets
    hero_target["Main_Stats"] = []
    return build, hero_target


def start_hero(char, target_stats):
    print("Hero: ", char)
    if char in target_stats:
        build = char
        print("Customer character build")
    elif char in target_stats["Type"]:
        build = target_stats["Type"][char]
        print("Character assigned template build:", build)
    else:
        print("No build assigned to this character")
        build = "General"
    print("Build type: ", build, "Stat priority: ", target_stats[build]["Prio"])

    input_sets = target_stats[build]["input_sets"]
    exclude_sets = target_stats[build]["exclude_sets"]
    include_sets = gen_input_sets(input_sets, exclude_sets)
    print("Sets to include for this character:", include_sets)
    target_stats[build]["include_sets"] = include_sets.tolist()
    try:
        if len(target_stats[build]["Force_4Set"]) == 1:
            pass
    except (KeyError, TypeError):
        if any(item in include_sets for item in set_4.Set_Nm.values):
            target_stats[build]["Force_4Set"] = 1
            print("Looking for combinations using a four piece set only.")
            print("To include combinations of three 2 gear sets, set FORCE_4SET = 0")
        else:
            target_stats[build]["Force_4Set"] = 0
            print("Accepts all set combinations (4set+2set or 3x2set)")
    return char, target_stats[build]


def run_stat_reco(output, hero_with_gear, hero_target):
    if hero_with_gear == 1:
        choice_df = output.iloc[-1:, :].copy()
        output = output.sort_values(by=[st.primary_sort_stat], ascending=False)
    else:
        output = output.sort_values(by=[st.primary_sort_stat], ascending=False)
        choice_df = output.iloc[:1, :].copy()
    output2 = output.copy()
    for stat in set_df[set_df.Bonus_Stat != "NA"].Bonus_Stat.values:
        output2.drop(output2[(output2[stat]).astype(int) < hero_target[stat]["Min"]].index, inplace=True)
        output2.drop(output2[(output2[stat]).astype(int) > hero_target[stat]["Max"]].index, inplace=True)
    print(
        "Progress: Step 3/4 Complete.  The number of combinations available with stats in specified range is: ",
        len(output2),
    )
    if len(output2) == 0:
        output2 = output.copy()
        print(
            "Since no combinations meet criteria, best alternative combinations will be shown based on desired stat weighting."
        )
    choice_parts = [
        choice_df,
        output.iloc[:3, :],
        output2.sort_values(by=[st.primary_sort_stat], ascending=False).iloc[:3, :],
    ]
    if hero_target.get("Prio"):
        for stat in np.unique(hero_target["Prio"]):
            choice_parts.append(output.sort_values(by=stat, ascending=False).iloc[:3, :])
            choice_parts.append(output2.sort_values(by=stat, ascending=False).iloc[:3, :])
    if hero_target.get("Prio"):
        for i in range(0, len(hero_target["Prio"])):
            target = hero_target["Prio"][i]
            cut_off = output2[target].quantile(0.9)
            output2 = output2[output2[target] >= cut_off]
    print("combinations after prio sortings ", len(output2))
    idx_reco = output2.iloc[[0]].index.values[0]
    choice_parts.append(output2.sort_values(by=[st.primary_sort_stat], ascending=False).iloc[:3, :])
    choice_parts.append(
        output2[
            (output2.Set_1.isin(["Unity", "Immunity", "Penetration"]))
            | (output2.Set_2.isin(["Unity", "Immunity"]))
            | (output2.Set_3.isin(["Unity", "Immunity"]))
        ]
        .sort_values(by=[st.primary_sort_stat], ascending=False)
        .iloc[:3, :]
    )
    choice_parts.append(
        output2[output2.Set_1.isin(["Counter", "Lifesteal", "Rage", "Injury", "Revenge"])]
        .sort_values(by=[st.primary_sort_stat], ascending=False)
        .iloc[:3, :]
    )
    if hero_target.get("Prio"):
        for stat in np.unique(hero_target["Prio"]):
            choice_parts.append(output2.sort_values(by=stat, ascending=False).iloc[:3, :])
    choice_df = pd.concat(choice_parts, ignore_index=False)
    choice_df = choice_df.drop(axis=1, columns=["gear_list", "Gear"]).drop_duplicates()
    return idx_reco, choice_df
