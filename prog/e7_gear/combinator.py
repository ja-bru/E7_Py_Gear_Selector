"""Gear set combination search."""

import itertools

import numpy as np
import pandas as pd

import config as st
from e7_gear.tables import l2, l4, set_2, set_4, set_df


def equip_optimizer_input(item_df, hero_name, sets, list_main_stats=[], gear_limit=None):
    if gear_limit is None:
        gear_limit = st.GEAR_LIMIT
    temp_df = item_df.copy()
    temp_df = temp_df[(temp_df.reco.isnull()) | (temp_df.reco == "") | (temp_df.reco == hero_name)]
    if st.NO_EQUIPPED_GEAR == 1:
        temp_df = temp_df[(temp_df.hero == "") | (temp_df.hero.isnull()) | (temp_df.hero == hero_name)]
    temp_df = temp_df[(temp_df.set.isin(sets))]
    if len(list_main_stats) > 0:
        for i in range(0, 3):
            if len(list_main_stats[i]) > 0:
                temp_df = temp_df.drop(
                    temp_df[(temp_df.Type == i + 3) & ~(temp_df.main_tp.isin(list_main_stats[i]))].index
                )
    temp_df.sort_values(by=["rating"], ascending=False, inplace=True)
    if st.KEEP_CURR_GEAR == 1:
        temp_slots = temp_df[(temp_df.hero == hero_name)].Type.values
        temp_df = temp_df[(~temp_df.Type.isin(temp_slots)) | (temp_df.hero == hero_name)]
        temp_df = temp_df.groupby("slot").head(gear_limit).reset_index(drop=True)
    else:
        temp_df_b = temp_df.groupby("slot").head(gear_limit).reset_index(drop=True)
        temp_df_c = temp_df.groupby(["slot", "set"]).head(1).reset_index(drop=True)
        temp_df.sort_values(by=["efficiency"], ascending=False, inplace=True)
        temp_df_d = temp_df.groupby(["slot", "set"]).head(1).reset_index(drop=True)
        temp_df = pd.concat([temp_df_b, temp_df_c, temp_df_d], ignore_index=True)
        temp_df = temp_df.drop_duplicates(["id"])
        temp_df.reset_index(inplace=True)
    return temp_df


def set_combo(item_df, l4_codes, l2_codes):
    gear_comb_dict = {}
    for set_nm in set_2.Set_Nm:
        temp_dict = {}
        temp_df2 = item_df[(item_df.set == set_nm)]
        for i in range(0, len(l2_codes)):
            temp_l = list(set(l2_codes[i]))
            temp_l.remove(",")
            itr = list(
                itertools.product(
                    temp_df2[(temp_df2.Type == int(temp_l[0]))].id.values,
                    temp_df2[(temp_df2.Type == int(temp_l[1]))].id.values,
                )
            )
            temp_dict[l2_codes[i]] = itr
        for i in range(0, len(l4_codes)):
            temp_l = list(set(l4_codes[i]))
            temp_l.remove(",")
            itr = list(
                itertools.product(
                    temp_df2[(temp_df2.Type == int(temp_l[0]))].id.values,
                    temp_df2[(temp_df2.Type == int(temp_l[1]))].id.values,
                    temp_df2[(temp_df2.Type == int(temp_l[2]))].id.values,
                    temp_df2[(temp_df2.Type == int(temp_l[3]))].id.values,
                )
            )
            temp_dict[l4_codes[i]] = itr
        gear_comb_dict[set_nm] = temp_dict
    for set_nm in set_4.Set_Nm:
        temp_dict = {}
        temp_df2 = item_df[(item_df.set == set_nm)]
        for i in range(0, len(l4_codes)):
            temp_l = list(set(l4_codes[i]))
            temp_l.remove(",")
            itr = list(
                itertools.product(
                    temp_df2[(temp_df2.Type == int(temp_l[0]))].id.values,
                    temp_df2[(temp_df2.Type == int(temp_l[1]))].id.values,
                    temp_df2[(temp_df2.Type == int(temp_l[2]))].id.values,
                    temp_df2[(temp_df2.Type == int(temp_l[3]))].id.values,
                )
            )
            temp_dict[l4_codes[i]] = itr
        gear_comb_dict[set_nm] = temp_dict
    return gear_comb_dict


def l4comb(l4_codes, l2_codes):
    l4_comb = []
    for i in range(0, len(l4_codes)):
        for j in range(0, len(l2_codes)):
            x4 = list(set(l4_codes[i]))
            x4.remove(",")
            x2 = list(set(l2_codes[j]))
            x2.remove(",")
            x6 = x2.copy()
            x6.extend(x4)
            if len(np.unique(x6)) == 6:
                l4_comb.append([l4_codes[i], l2_codes[j]])
    return l4_comb


def l2comb(l2_codes):
    l2_comb = []
    for i in range(0, 5):
        for j in range(5, len(l2_codes)):
            for k in range(5, len(l2_codes)):
                x21 = sorted(list(set(l2_codes[i])))
                x21.remove(",")
                x22 = sorted(list(set(l2_codes[j])))
                x22.remove(",")
                x23 = sorted(list(set(l2_codes[k])))
                x23.remove(",")
                x6 = x21.copy()
                x6.extend(x22)
                x6.extend(x23)
                if (x21[0] < x22[0]) & (x22[0] < x23[0]) & (len(np.unique(x6)) == 6):
                    l2_comb.append([l2_codes[i], l2_codes[j], l2_codes[k]])
    return l2_comb


def _parse_slot_code(code):
    return code.split(",")


def _set_product_count(item_df, set_nm, slot_code):
    temp_df2 = item_df[item_df.set == set_nm]
    count = 1
    for slot in _parse_slot_code(slot_code):
        slot_count = len(temp_df2[temp_df2.Type == int(slot)])
        if slot_count == 0:
            return 0
        count *= slot_count
    return count


def estimate_set_combination_count(item_df, set4_list, set2_list, force_4set):
    total = 0
    l4_comb_list = l4comb(l4, l2)
    l2_comb_list = l2comb(l2)
    for set_nm4 in set4_list:
        for set_nm2 in set2_list:
            for code4, code2 in l4_comb_list:
                total += _set_product_count(item_df, set_nm4, code4) * _set_product_count(item_df, set_nm2, code2)
    if force_4set != 1:
        for set_nm in itertools.combinations(set2_list, 3):
            for code1, code2, code3 in l2_comb_list:
                total += (
                    _set_product_count(item_df, set_nm[0], code1)
                    * _set_product_count(item_df, set_nm[1], code2)
                    * _set_product_count(item_df, set_nm[2], code3)
                )
    return total


def set_combination_iterate(gear_comb_dict, set4_list, set2_list, force_4set):
    Set_1 = []
    Set_2 = []
    Set_3 = []
    Gear = []
    Complete = []
    l4_comb = l4comb(l4, l2)
    l2_comb = l2comb(l2)
    for set_nm4 in set4_list:
        for set_nm2 in set2_list:
            for a in range(0, len(l4_comb)):
                code4 = l4_comb[a][0]
                code2 = l4_comb[a][1]
                g4_set = gear_comb_dict[set_nm4][code4]
                g2_set = gear_comb_dict[set_nm2][code2]
                itr = list(itertools.product(g4_set, g2_set))
                Set_1.extend([set_nm4] * len(itr))
                Set_2.extend([set_nm2] * len(itr))
                Set_3.extend([None] * len(itr))
                Gear.extend(itr)
                Complete.extend([1] * len(itr))
    if force_4set != 1:
        for set_nm in itertools.combinations(set2_list, 3):
            for a in range(0, len(l2_comb)):
                code1 = l2_comb[a][0]
                code2 = l2_comb[a][1]
                code3 = l2_comb[a][2]
                g2_set1 = gear_comb_dict[set_nm[0]][code1]
                g2_set2 = gear_comb_dict[set_nm[1]][code2]
                g2_set3 = gear_comb_dict[set_nm[2]][code3]
                itr = list(itertools.product(g2_set1, g2_set2, g2_set3))
                Set_1.extend([set_nm[0]] * len(itr))
                Set_2.extend([set_nm[1]] * len(itr))
                Set_3.extend([set_nm[2]] * len(itr))
                Gear.extend(itr)
                Complete.extend([1] * len(itr))
    print("Progress: Step 1/4 Complete.  Number of combinations found", len(Complete))
    print("For processing efficency, I would aim to keep combinations less than 1 million")
    return list(zip(Set_1, Set_2, Set_3, Complete, Gear))


def prepare_gear_combinations(df_items, char, include_sets, main_stats, force_4set=0):
    set4_list = set_4[set_4.Set_Nm.isin(include_sets)].Set_Nm.values
    set2_list = set_2[set_2.Set_Nm.isin(include_sets)].Set_Nm.values
    gear_limit = st.GEAR_LIMIT
    filtered_df = equip_optimizer_input(df_items, char, include_sets, main_stats, gear_limit=gear_limit)
    combo_count = estimate_set_combination_count(filtered_df, set4_list, set2_list, force_4set)

    while combo_count > st.COMBO_COUNT_LIMIT and st.AUTO_ADJ_GEAR_LIMIT and gear_limit > 1:
        gear_limit -= 1
        print(
            f"Estimated {combo_count:,} combinations exceeds {st.COMBO_COUNT_LIMIT:,}; "
            f"reducing GEAR_LIMIT to {gear_limit}"
        )
        filtered_df = equip_optimizer_input(df_items, char, include_sets, main_stats, gear_limit=gear_limit)
        combo_count = estimate_set_combination_count(filtered_df, set4_list, set2_list, force_4set)

    if combo_count > st.COMBO_COUNT_LIMIT:
        print(
            f"Warning: estimated {combo_count:,} combinations still exceeds "
            f"{st.COMBO_COUNT_LIMIT:,}. Consider lowering GEAR_LIMIT manually."
        )
    elif gear_limit != st.GEAR_LIMIT:
        print(f"Using GEAR_LIMIT={gear_limit} for this hero (default is {st.GEAR_LIMIT})")

    gear_comb_dict = set_combo(filtered_df, l4, l2)
    sc_output = set_combination_iterate(gear_comb_dict, set4_list, set2_list, force_4set)
    return sc_output, gear_limit


def gear_split(df):
    if df.Set_3 == None:
        u, v = df.Gear
        m, n, o, p = u
        q, r = v
    else:
        u, v, w = df.Gear
        m, n = u
        o, p = v
        q, r = w
    return list(np.sort([m, n, o, p, q, r]))


def final_gear_combos(sc_output, char, df_items):
    sc_df = pd.DataFrame(sc_output, columns=["Set_1", "Set_2", "Set_3", "Complete", "Gear"])
    sc_df["gear_list"] = sc_df.apply(lambda row: gear_split(row), axis=1)
    sc_df[["0", "1", "2", "3", "4", "5"]] = pd.DataFrame(sc_df.gear_list.values.tolist(), index=sc_df.index)
    sc_df = sc_df.drop_duplicates(["0", "1", "2", "3", "4", "5"])
    current_gear = pd.DataFrame(
        columns=["Set_1", "Set_2", "Set_3", "Complete", "Gear", "gear_list", "0", "1", "2", "3", "4", "5"],
        index=["0"],
    )
    try:
        nix = 0
        for gid in range(0, 6):
            current_gear[str(gid)] = df_items[(df_items.hero == char) & (df_items.Type == gid)][["id"]].values
            val = df_items[(df_items.hero == char) & (df_items.Type == gid)][["reco"]].values
            if (val > "") & (val != char):
                nix = 1
        current_gear = get_set_bonus(current_gear, df_items)
        if nix == 1:
            current_gear["Complete"] = "PREVIOUS"
        elif nix == 0:
            current_gear["Complete"] = "CURRENT"
        sc_df = pd.concat([sc_df, current_gear], ignore_index=True)
        hero_with_gear = 1
    except (IndexError, KeyError, ValueError):
        hero_with_gear = 0
    print(
        "Progress: Step 2/4 Complete.  Number of unique combinations for optimization",
        len(sc_df[sc_df.Complete != "PREVIOUS"]),
    )
    return sc_df, hero_with_gear


def gen_input_sets(include, exclude, autofill=0):
    x = 0
    iv = 0
    ii = 0
    if len(include) == 0:
        include = set_df[~set_df.Set_Nm.isin(exclude)]["Set_Nm"].values
    else:
        for set_nm in include:
            x += set_df[set_df.Set_Nm == set_nm].iloc[0]["Set_Lg"]
            iv = 1 if set_nm in (set_df[set_df.Set_Lg == 4]["Set_Nm"].values) else iv
            ii = 1 if set_nm in (set_df[set_df.Set_Lg == 2]["Set_Nm"].values) else ii
        if iv == 1:
            exclude.extend(list(set(set_df[set_df.Set_Lg == 4]["Set_Nm"].values) - set(include)))
        if ii == 1:
            exclude.extend(list(set(set_df[set_df.Set_Lg == 2]["Set_Nm"].values) - set(include)))
        if (x == 6) or ((x > 6) & (ii == 1)):
            pass
        elif (ii == 0) & (iv == 1):
            include.extend(set_df[(set_df.Set_Lg == 2) & (~set_df.Set_Nm.isin(exclude))]["Set_Nm"].values)
        elif autofill == 0:
            pass
        elif x == 2:
            include.extend(
                set_df[(set_df.Set_Lg == 4) & (~set_df.Set_Nm.isin(exclude)) & (~set_df.Set_Nm.isin(include))][
                    "Set_Nm"
                ].values
            )
            include.extend(
                set_df[(set_df.Set_Lg == 2) & (~set_df.Set_Nm.isin(exclude)) & (~set_df.Set_Nm.isin(include))][
                    "Set_Nm"
                ].values
            )
        elif x < 6:
            include.extend(
                set_df[(set_df.Set_Lg == 2) & (~set_df.Set_Nm.isin(exclude)) & (~set_df.Set_Nm.isin(include))][
                    "Set_Nm"
                ].values
            )
            include.extend(
                set_df[(set_df.Set_Lg == 4) & (~set_df.Set_Nm.isin(exclude)) & (~set_df.Set_Nm.isin(include))][
                    "Set_Nm"
                ].values
            )
    return include


def get_set_bonus(df, item_df):
    if len(df) > 1:
        gears = df[["0", "1", "2", "3", "4", "5"]].values
    else:
        gears = df[["0", "1", "2", "3", "4", "5"]].values[0]
    set_stats = item_df[item_df.id.isin(gears)].groupby(["set"]).count()[["id"]]
    set_stats = set_df.merge(set_stats, how="inner", left_on="Set_Nm", right_on="set")
    set_stats["Mult"] = (set_stats.id / set_stats.Set_Lg).astype(int)
    complete_sets_ind = (set_stats.Mult * set_stats.Set_Lg).sum()
    set_list = []
    for set_nm in set_stats.Set_Nm.values:
        v = set_stats[(set_stats.Set_Nm == set_nm)].iloc[0]["Mult"]
        for _ in range(0, v):
            set_list.append(set_nm)
    df["Complete"] = np.where(complete_sets_ind == 6, 1, 0)
    df["Set_1"] = set_list[0] if len(set_list) >= 1 else None
    df["Set_2"] = set_list[1] if len(set_list) >= 2 else None
    df["Set_3"] = set_list[2] if len(set_list) >= 3 else None
    return df
