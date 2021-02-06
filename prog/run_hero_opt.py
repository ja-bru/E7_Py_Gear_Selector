## THIS FILE USES AVAILABLE GEAR TO OPTIMIZE STATS ON YOUR HEROES IN EPIC Seven

## ## Import packages
from datetime import datetime
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 40)
import numpy as np
import itertools
import pickle
import json
import yaml
## ## Import Custom-funtions from python files
import setup as st
import fx_lib as fx
import customer_ui_fx as ui
## ## Open input datasets
with open(r'../inp/character_inputs.yaml') as file:
    target_stats = yaml.load(file, Loader=yaml.FullLoader)
with open('../inp/master_data.json') as json_file:
    data = json.load(json_file)
df_items = pd.read_pickle('../outp/equip_potential.pkl')
df_items['reco'] = ''
df_items['start_loc'] = df_items['hero']
# CATCH INPUT ERRORS
fx.verify_setup()

# ##### HEROES
hero_order = fx.startup_msg1(target_stats)
##lock gear on user specified heroes
lock_gear = target_stats['Lock_Gear']
df_hero, char_list = fx.hero_json_to_df(hero_order, data)
df_items = fx.startup_msg2(df_items, lock_gear)

###input for loop
for j in range(0,len(hero_order)):
    char = hero_order[j]
    print(".")
    print(".")
    print(".")
    print("Start hero: ", char, " // Level ", df_hero[df_hero.Name == char]['Lvl'].values , "  //  ", datetime.now())
    if char in target_stats: build = char
    elif char in target_stats["Type"]: build = target_stats['Type'][char]
    else: build = 'General'

    hero_target = target_stats[build]
    print("Build type: ", build, "Final Stat Priority: ", hero_target['Prio'])

    ##what sets to use
    input_sets = hero_target['input_sets']
    exclude_sets = hero_target['exclude_sets']
    include_sets = fx.gen_input_sets(input_sets, exclude_sets)
    print("The following sets are included in gear optimization", include_sets)
    hero_target['include_sets'] = include_sets
    hero_target['Main_Stats'] = []

    run_counter = run_pass = 0
    while (run_pass < 1)&(run_counter < 1):
        gear_comb_dict = fx.set_combo(fx.equip_optimizer_input(df_items, char, hero_target, hero_target['Main_Stats']), fx.l4, fx.l2)  ## Output gear_comb_dict[ [set_nm] , [type] , [ID] ]
        sc_output = fx.set_combination_iterate(gear_comb_dict, fx.set_4[fx.set_4.Set_Nm.isin(include_sets)].Set_Nm.values , fx.set_2[fx.set_2.Set_Nm.isin(include_sets)].Set_Nm.values, 0)
        if len(sc_output) == 0:
            print("No combinations were found for this hero. To skip this hero and begin the next here, enter [Skip]. ")
            print("To retry this hero, enter [Retry].  To end the optimization, enter [Exit].")
            print("If you exit, your data so far will not be lost, but you will need to run the recover program to get output up to this point.")
            user_input = input("""Please enter one of [Skip, Retry, Exit] """ )
            input_list = ['Skip','Retry','Exit']
            if user_input not in input_list:
                user_input = ui.readInput("Please enter one of [Skip, Retry, Exit]","Retry" )
                if user_input not in input_list: user_input = 'Retry'
            if user_input == 'Retry':
                if run_counter == 1:
                    print("No results were found during retry, the hero will be skipped")
                    continue
                else: run_counter = 1
                include_sets = fx.gen_input_sets([], exclude_sets)
                hero_target['Main_Stats'] = []
                #hero_target['Force_4Set'] = 0
                print("Retrying with the following sets ", include_sets)
            elif user_input == 'Skip':
                run_pass = 1
            elif user_input == 'Exit':
                break
        else:  run_pass = 1
    #end while loop
    try:   ##initializes the dataframe
        sc_df = pd.DataFrame(sc_output, columns =['Set_1', 'Set_2', 'Set_3','Complete','Gear'])
    except:
        continue

    sc_df, hero_with_gear = fx.final_gear_combos(sc_output, char)
    odf = fx.get_combo_stats(sc_df, df_hero, fx.mainst_sum(sc_df, df_items), fx.subst_sum(sc_df, df_items), \
                    fx.set_sum(sc_df), fx.bonus_eqp_sum(df_hero[df_hero.Name == char]), char, hero_target)
    idx_reco, choice_df = fx.run_stat_reco(odf, hero_with_gear, hero_target)
    if st.MANUAL_SELECTION == 1:
        print("Enter the index value (the top number of the stat output) for the stats you would like to assign to your hero:")
        screen_options = choice_df[['Set_1','Set_2','Set_3','WW','ATK','HP','DEF','SPD','CRIT','CDMG','EFF','RES','Dmg_Rating','EHP','Complete']].transpose()
        print(screen_options)
        row_idx = int(input(""" Please enter index corresponding with gear selection """ ))
        idx_reco = row_idx
    gear_selected = odf.loc[idx_reco]
    odf['Complete'].loc[idx_reco] = 'RECO'
    df_items = ui.save_hero(df_items, odf.loc[idx_reco], char)
    print("Progress: Step 4/4 Complete.  Recommended gear selected.  Completed hero: ", char)
    if hero_with_gear == 1:  print("Hero began optimization with gear equipped")
    print(odf[odf.Complete.isin(['CURRENT','PREVIOUS','RECO'])][['Complete','Set_1','Set_2','Set_3','WW','ATK','HP','DEF','SPD','CRIT','CDMG','EFF','RES','Dmg_Rating','EHP']])

    reco_list = gear_selected['gear_list']
    df_items['reco'] = np.where( df_items.id.isin(reco_list) , char, df_items['reco'])
##end for loop
ui.save_final_data(df_items)
print("Saving final results.  Results can be viewed in gear_reco.csv or upd_items.json.")
print("If you are happy with the results, you can move gear over in Epic Seven and update the items section in master_data.json")
