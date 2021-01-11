## THIS FILE USES AVAILABLE GEAR TO OPTIMIZE STATS ON YOUR HEROES IN EPIC Seven

## ## FILE SETTINGS
import setup as st
import fx_lib as fx
from datetime import datetime
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 40)
import numpy as np
import itertools
import pickle
import json
import yaml
with open(r'../inp/character_inputs.yaml') as file:
    target_stats = yaml.load(file, Loader=yaml.FullLoader)

with open('../inp/master_data.json') as json_file:
    data = json.load(json_file)

# CATCH INPUT ERRORS
fx.verify_setup()

# ##### HEROES
hero_order = target_stats['Hero_Order']
df_hero = fx.hero_json_to_df(hero_order, data)
if len(df_hero['Character'][df_hero['Atk'].isnull()]) > 0:
    print("Error: Character data missing from source file", df_hero['Name'][df_hero['Atk'].isnull()].values)
    exit()

##gear combination set up
import set_combo as sc

print("")
if st.NO_EQUIPPED_GEAR == 1:
    print("No equipped gear will be included in optimization.  Pieces of gear: ", len(sc.df_items[(sc.df_items.hero == np.nan) | (sc.df_items.hero == '')]) )
elif len(target_stats['Lock_Gear']) > 0:
    print("Gear equipped on the following heroes is locked and will not be included in optimization: ", target_stats['Lock_Gear'])
else:
    print("All gear will be used for optimization.", len(sc.df_items) )

##lock gear on user specified heroes
lock_gear = target_stats['Lock_Gear']
sc.df_items['reco'] = np.where( sc.df_items['hero'].isin(lock_gear) , sc.df_items['hero'], sc.df_items['reco'] )
sc.df_items['start_loc'] = sc.df_items['hero']

print("The following heroes will run: ", hero_order)
print("")
###input for loop
for j in range(0,len(hero_order)):
    char = hero_order[j]
    print("")
    print("Start hero: ", char, " // Level ", df_hero[df_hero.Name == char]['Lvl'].values , "  //  ", datetime.now())
    if char in target_stats: char2 = char
    elif char in target_stats["Type"]: char2 = target_stats['Type'][char]
    else: char2 = 'General'

    print("Build type: ", char2, "Final Stat Priority: ", target_stats[char2]['Prio'])

    ##what sets to use
    input_sets = target_stats[char2]['input_sets']
    exclude_sets = target_stats[char2]['exclude_sets']
    include_sets = fx.gen_input_sets(input_sets, exclude_sets)
    print("The following sets are included in gear optimization", include_sets)

    run_counter = run_pass = 0
    while (run_pass < 1)&(run_counter < 1):
        gear_comb_dict = fx.set_combo(sc.df_items[(sc.df_items.set.isin(include_sets))|(sc.df_items.hero==char)], char, sc.l4, sc.l2)  ## Output gear_comb_dict[ [set_nm] , [type] , [ID] ]
        sc_output = sc.set_combination_iterate(gear_comb_dict, fx.set_4[fx.set_4.Set_Nm.isin(include_sets)].Set_Nm.values , fx.set_2[fx.set_2.Set_Nm.isin(include_sets)].Set_Nm.values, only4_flag = 0)
        print('Progress: Step 1/4 Complete.  Number of combinations found', len(sc_output) , "   ", datetime.now())
        if len(sc_output) == 0:
            print("No combinations were found for this hero. To skip this hero and begin the next here, enter [Skip]. ")
            print("To retry this hero, enter [Retry].  To end the optimization, enter [Exit].")
            print("If you exit, your data so far will not be lost, but you will need to run the recover program to get output up to this point.")
            user_input = input("""Please enter one of [Skip, Retry, Exit] """ )
            input_list = ['Skip','Retry','Exit']
            if user_input not in input_list:
                user_input = input("""Please enter one of [Skip, Retry, Exit] """ )
                if user_input not in input_list: user_input = 'Retry'
            if user_input == 'Retry':
                if run_counter == 1:
                    print("No results were found during retry, the hero will be skipped")
                    continue
                else: run_counter = 1
                include_sets = fx.gen_input_sets([], exclude_sets)
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

    sc_df['gear_list'] = sc_df.apply(lambda row: fx.gear_split(row) , axis=1)
    sc_df[['0','1','2','3','4','5']] = pd.DataFrame(sc_df.gear_list.values.tolist(), index= sc_df.index)
    sc_df = sc_df.drop_duplicates(['0','1','2','3','4','5'])

    ### add current gear setting stats
    current_gear = pd.DataFrame(columns = ['Set_1', 'Set_2', 'Set_3', 'Complete', 'Gear', 'gear_list', '0', '1', '2', '3', '4', '5' ], index = ['0'])
    try:
        nix=0
        for gid in range(0,6):
            current_gear[str(gid)] = sc.df_items[(sc.df_items.hero == char) & (sc.df_items.Type == gid)][['id']].values
            val = sc.df_items[(sc.df_items.hero == char) & (sc.df_items.Type == gid)][['reco']].values
            if (val > '') & (val!=char): nix = 1
        current_gear = fx.get_set_bonus(current_gear, sc.df_items)
        if nix==1: current_gear['Complete'] = 'PREVIOUS'
        elif nix==0: current_gear['Complete'] = 'CURRENT'
        sc_df = sc_df.append(current_gear)
        sc_df = sc_df.reset_index()
        hero_with_gear = 1
    except:
        hero_with_gear = 0

    ### final stats for each combination
    output = fx.get_combo_stats(sc_df, df_hero, fx.mainst_sum(sc_df, sc.df_items), fx.subst_sum(sc_df, sc.df_items), \
                                fx.set_sum(sc_df), fx.bonus_eqp_sum(df_hero[df_hero.Name == char]), char, target_stats[char2])
    print('Progress: Step 2/4 Complete.  Number of unique combinations for optimization', len(output) , "   ", datetime.now())

    if hero_with_gear == 1:
        choice_df = output.iloc[-1:,:].copy()
        output = output.sort_values(by = ['WW'], ascending = False )  ## faster than inplace
    else:
        output = output.sort_values(by = ['WW'], ascending = False )  ## faster than inplace
        choice_df = output.iloc[:1,:].copy()

    ## regular process
    output2 = output.copy()
    for stat in fx.set_df[fx.set_df.Bonus_Stat != 'NA'].Bonus_Stat.values:
        output2.drop( output2[(output2[stat]).astype(int) < target_stats[char2][stat]['Min']].index, inplace=True)
        output2.drop( output2[(output2[stat]).astype(int) > target_stats[char2][stat]['Max']].index, inplace=True)
    print("Progress: Step 3/4 Complete.  The number of combinations available with stats in specified range is: ",len(output2))
    if len(output2)==0:
        output2 = output
        print("Since no combinations meet criteria, best alternative combinations will be shown based on desired stat weighting.")

    ## get top options for key stats
    if st.MANUAL_SELECTION == 1:
        choice_df = choice_df.append(output.iloc[:3,:])
        for STAT in np.unique(target_stats[char2]['Prio']):
            choice_df = choice_df.append(output.sort_values(by = STAT, ascending = False ).iloc[:3,:] )
        choice_df = choice_df.append(output2.sort_values(by = ['WW'], ascending = False ).iloc[:3,:] )
        for STAT in np.unique(target_stats[char2]['Prio']):
            choice_df = choice_df.append(output2.sort_values(by = STAT, ascending = False ).iloc[:3,:] )

    for i in range(0,len(target_stats[char2]['Prio'])):
        target = target_stats[char2]['Prio'][i]
        cut_off = output2[target].quantile(0.9)
        output2 = output2[ output2[target] >= cut_off ]
    print("combinations after prio sortings ", len(output2) )

    if st.MANUAL_SELECTION == 1:
        choice_df = choice_df.append(output2.sort_values(by = ['WW'], ascending = False ).iloc[:3,:] )
        choice_df = choice_df.append(output2[(output2.Set_1.isin(['Unity','Immunity','Penetration'])) | (output2.Set_2.isin(['Unity','Immunity'])) | \
                (output2.Set_3.isin(['Unity','Immunity']))].sort_values(by = ['WW'], ascending = False ).iloc[:3,:] )
        choice_df = choice_df.append(output2[(output2.Set_1.isin(['Counter','Lifesteal','Rage','Injury','Revenge']))].sort_values(by = ['WW'], ascending = False ).iloc[:3,:] )
        for STAT in np.unique(target_stats[char2]['Prio']):
            choice_df = choice_df.append(output2.sort_values(by = STAT, ascending = False ).iloc[:3,:] )
        choice_df = choice_df.drop(axis = 1, columns = ['gear_list','Gear']).drop_duplicates()
        print("Enter the index value (the top number of the stat output) for the stats you would like to assign to your hero:")
        screen_options = choice_df[['Set_1','Set_2','Set_3','WW','ATK','HP','DEF','SPD','CRIT','CDMG','EFF','RES','Dmg_Rating','EHP']].transpose()
        print(screen_options)
        row_idx = int(input(""" Please enter index corresponding with gear selection """ ))
        output['Complete'].loc[row_idx] = 'RECO'
        gear_selected = output.loc[row_idx]
    if st.MANUAL_SELECTION != 1:
        output2['Complete'].iloc[0,:] = 'RECO'
        gear_selected = output2.iloc[0,:]
        choice_df = choice_df.append(gear_selected)
    if hero_with_gear == 1:  print("No starting gear was equipped on this hero")
    print(choice_df[choice_df.Complete.isin(['CURRENT','PREVIOUS','RECO'])][['Complete','Set_1','Set_2','Set_3','WW','ATK','HP','DEF','SPD','CRIT','CDMG','EFF','RES','Dmg_Rating','EHP']])
    reco_list = gear_selected['gear_list']
    try: reco_df.append(gear_selected)
    except: reco_df = pd.DataFrame(gear_selected)
    sc.df_items['reco'] = np.where( sc.df_items.id.isin(reco_list) , char, sc.df_items['reco'])

    print("Progress: Step 4/4 Complete.  Recommended gear selected.  Completed hero: ", char)

    sc.df_items['hero'] = np.where((sc.df_items.hero == char)&(sc.df_items.hero != sc.df_items.reco),'',sc.df_items.hero) ##unlocks gear for next hero

    sc.df_items = sc.df_items.sort_values(by = ['reco','Type','hero','efficiency','enhance'])
    sc.df_items.to_pickle('../outp/upd_items.pkl') ##saves interim results in case of error
##end for loop

print("Saving final results.  Results can be viewed in gear_reco.csv or upd_items.json.")
print("If you are happy with the results, you can move gear over in Erpic Seven and update the items section in master_data.json")

sc.df_items[~sc.df_items.reco.isnull()][['start_loc','reco','slot','set','level','rarity','enhance','mainStat','subStat1','subStat2','subStat3','subStat4','efficiency','rating','Type']].to_csv('../reco/gear_reco.csv')
sc.df_items['hero'] = np.where( ~sc.df_items.reco.isnull(), sc.df_items['reco'],sc.df_items['hero'])
sc.df_items.to_pickle('../outp/equip_potential.pkl')

sc.df_items = sc.df_items.sort_values(by = ['hero','Type','efficiency','enhance'])
export2 = sc.df_items[['efficiency','hero','enhance','slot','level','set','rarity','mainStat','subStat1','subStat2','subStat3','subStat4','id','p_id','locked']].to_dict('records')
with open('../outp/upd_items.json', 'w') as fp: json.dump(export2, fp)
