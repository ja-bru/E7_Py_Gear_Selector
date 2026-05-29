"""Input/output helpers for hero and gear data."""

import numpy as np
import pandas as pd

import config as st
import gear_ref_table as grt
import paths
from e7_gear.tables import subs_cols


def clean_up_dictionary_input(input_dict, key1, key2):
    """Specific data cleanup to improves compatibility with compeanansi OCR output."""
    if type(key2) == str:
        for i in range(0, len(input_dict)):
            if key1 in input_dict[i]:
                input_dict[i][key2] = input_dict[i][key1]
    elif type(key2) == list:
        for i in range(0, len(input_dict)):
            if key1 in input_dict[i]:
                if type(input_dict[i][key1]) != list:
                    input_dict[i][key1] = key2
            else:
                input_dict[i][key1] = key2
    return input_dict.copy()


def hero_json_to_df(chars, data):
    char_df = pd.read_csv(paths.CHARACTER_DATA_CSV)
    char_list = np.sort(char_df[grt.e7api_map["hero"]].unique())
    print("Missing hero stats in source file for:", [x for x in chars if x not in char_list])
    data["heroes"] = clean_up_dictionary_input(data["heroes"], "Artifact", "BonusStats")
    df = pd.DataFrame(char_list, columns=["Name"])
    df2 = pd.DataFrame(data["heroes"])
    df = pd.merge(df, df2[["Name", "Lvl", "BonusStats"]], how="left", on=["Name"])
    df["Lvl"] = df["Lvl"].fillna(st.MIN_LEVEL)
    df["Lvl"] = df["Lvl"].clip(lower=st.MIN_LEVEL)
    df = df.merge(
        char_df,
        how="left",
        left_on=["Name", "Lvl"],
        right_on=[grt.e7api_map["hero"], grt.e7api_map["level"]],
    )
    if len(df["Name"][df[grt.e7api_map["atk"]].isnull()]) > 0:
        print(
            "Error: Character data missing from source file",
            df["Name"][df[grt.e7api_map["atk"]].isnull()].values,
        )
        exit()
    return df, char_list


def item_json_to_df(data):
    data["items"] = clean_up_dictionary_input(data["items"], "ability", "enhance")
    for sub in subs_cols:
        data["items"] = clean_up_dictionary_input(data["items"], sub, ["X", 0])
    data["items"] = clean_up_dictionary_input(data["items"], "hero", "")
    default_input_format = {
        "hero": "",
        "enhance": 0,
        "slot": "",
        "level": 0,
        "set": "",
        "rarity": "",
        "mainStat": ["X", 0],
        "subStat1": ["X", 0],
        "subStat2": ["X", 0],
        "subStat3": ["X", 0],
        "subStat4": ["X", 0],
        "id": "",
        "locked": False,
    }
    data_list = [default_input_format]
    data_list.extend(data["items"])
    df = pd.DataFrame(data_list, columns=default_input_format.keys())
    df = df[1:]
    df["grade"] = df["rarity"].map(grt.r_map)
    df["Type"] = df["slot"].map(grt.t_map)
    return df


def startup_msg1(target_stats):
    hero_order = target_stats["Hero_Order"]
    print("Heroes for optimization:", hero_order)
    if st.NO_EQUIPPED_GEAR == 1:
        print("No equipped gear will be included in optimization.")
    else:
        print(
            "Gear on the following heroes is locked and cannot be stolen from another hero.",
            target_stats["Lock_Gear"],
        )
    print("Gear will be unlocked if new gear is equipped on that hero")
    return hero_order


def startup_msg2(df, lock_gear):
    df["reco"] = np.where(df["hero"].isin(lock_gear), df["hero"], df["reco"])
    print("Total # of items loaded:", len(df))
    if st.NO_EQUIPPED_GEAR == 1:
        print(
            "Unequipped gear will be used. # of items: ",
            len(df[(df.hero == np.nan) | (df.hero == "")]),
        )
    elif len(lock_gear) > 0:
        print("Unequipped and unlocked gear will be used.  # of items", len(df[df.reco == ""]))
    else:
        print("All gear will be used.")
    return df
