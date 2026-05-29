## THIS FILE USES AVAILABLE GEAR TO OPTIMIZE STATS ON YOUR HEROES IN EPIC Seven

from datetime import datetime
import json

import numpy as np
import pandas as pd

pd.set_option("display.max_rows", 100)
pd.set_option("display.max_columns", 40)

import customer_ui_fx as ui
import config as st
import fx_lib as fx
import paths
from e7_gear.optimizer import optimize_hero


def _prompt_no_combos(char, exclude_sets, hero_target):
    print("No combinations were found for this hero. To skip this hero and begin the next here, enter [Skip]. ")
    print("To retry this hero, enter [Retry].  To end the optimization, enter [Exit].")
    print("If you exit, your data so far will not be lost, but you will need to run the recover program to get output up to this point.")
    user_input = input("""Please enter one of [Skip, Retry, Exit] """)
    input_list = ["Skip", "Retry", "Exit"]
    if user_input not in input_list:
        user_input = ui.readInput("Please enter one of [Skip, Retry, Exit]", "Retry")
        if user_input not in input_list:
            user_input = "Retry"
    if user_input == "Retry":
        include_sets = fx.gen_input_sets([], exclude_sets)
        hero_target["include_sets"] = include_sets
        hero_target["Main_Stats"] = []
        print("Retrying with the following sets ", include_sets)
        return "retry", hero_target
    if user_input == "Skip":
        return "skip", hero_target
    return "exit", hero_target


def main():
    target_stats = fx.load_target_stats()
    with open(paths.MASTER_DATA_JSON) as json_file:
        data = json.load(json_file)
    df_items = pd.read_pickle(paths.EQUIP_POTENTIAL_PKL)
    df_items["reco"] = ""
    df_items["start_loc"] = df_items["hero"]

    fx.verify_setup()

    hero_order = fx.startup_msg1(target_stats)
    lock_gear = target_stats["Lock_Gear"]
    df_hero, char_list = fx.hero_json_to_df(hero_order, data)
    df_items = fx.startup_msg2(df_items, lock_gear)

    for char in hero_order:
        print(".")
        print(".")
        print(".")
        print(
            "Start hero: ",
            char,
            " // Level ",
            df_hero[df_hero.Name == char]["Lvl"].values,
            "  //  ",
            datetime.now(),
        )

        build, hero_target = fx.prepare_hero_target(char, target_stats)
        print("Build type: ", build, "Final Stat Priority: ", hero_target["Prio"])
        print("The following sets are included in gear optimization", hero_target["include_sets"])

        exclude_sets = list(hero_target["exclude_sets"])
        run_counter = 0
        result = None
        while result is None and run_counter < 2:
            result = optimize_hero(
                char,
                df_items,
                df_hero,
                hero_target,
                build=build,
                force_4set=hero_target.get("Force_4Set", 0),
            )
            if result is not None:
                break
            action, hero_target = _prompt_no_combos(char, exclude_sets, hero_target)
            if action == "exit":
                ui.save_final_data(df_items)
                print("Saving partial results before exit.")
                return
            if action == "skip":
                break
            if action == "retry":
                run_counter += 1
                if run_counter >= 2:
                    print("No results were found during retry, the hero will be skipped")
                    break

        if result is None:
            continue

        idx_reco = result.idx_reco
        choice_df = result.choice_df
        odf = result.odf

        if st.MANUAL_SELECTION == 1:
            print("Enter the index value (the top number of the stat output) for the stats you would like to assign to your hero:")
            screen_options = choice_df[
                [
                    "Set_1", "Set_2", "Set_3", "WW", "ATK", "HP", "DEF", "SPD",
                    "CRIT", "CDMG", "EFF", "RES", "Dmg_Rating", "EHP", "Complete",
                ]
            ].transpose()
            print(screen_options)
            row_idx = int(input(""" Please enter index corresponding with gear selection """))
            idx_reco = row_idx

        gear_selected = odf.loc[idx_reco]
        odf.loc[idx_reco, "Complete"] = "RECO"
        df_items = ui.save_hero(df_items, odf.loc[idx_reco], char)
        print("Progress: Step 4/4 Complete.  Recommended gear selected.  Completed hero: ", char)
        if result.hero_with_gear == 1:
            print("Hero began optimization with gear equipped")
        print(
            odf[odf.Complete.isin(["CURRENT", "PREVIOUS", "RECO"])][
                [
                    "Complete", "Set_1", "Set_2", "Set_3", "WW", "ATK", "HP", "DEF",
                    "SPD", "CRIT", "CDMG", "EFF", "RES", "Dmg_Rating", "EHP",
                ]
            ]
        )

        reco_list = gear_selected["gear_list"]
        df_items["reco"] = np.where(df_items.id.isin(reco_list), char, df_items["reco"])

    ui.save_final_data(df_items)
    print("Saving final results.  Results can be viewed in gear_reco.csv or upd_items.json.")
    print("If you are happy with the results, you can move gear over in Epic Seven and update the items section in master_data.json")


if __name__ == "__main__":
    main()
