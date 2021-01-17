# #### SET UP
import pandas as pd
import numpy as np
import math
import itertools
import setup as st
import gear_ref_table as grt

# ### PULL IN FIXED LOOKUP TABLES FOR GEAR
gear_rating_lookup = grt.gear_rating_lookup.copy()
grl = gear_rating_lookup.to_dict()
gear_tier = pd.read_csv("../inp/gear_tiers.csv")
type_df = grt.type_df.copy()
set_df = grt.set_df.copy()
set_4 = set_df[['Set','Set_Nm','Set_Lg']][set_df.Set_Lg == 4]
set_2 = set_df[['Set','Set_Nm','Set_Lg']][set_df.Set_Lg == 2]
subs_cols = ['subStat1','subStat2','subStat3','subStat4']

# ******************************************
# ### QA functions
def verify_setup():
    print("Checking program configuration")
    if st.MANUAL_SELECTION != 1:  print("Automated optimization is set, all heroes will run in order without user input to select gear")
    if st.MIN_LEVEL != 60:  st.MIN_LEVEL = 50
    if ~(isinstance(st.GEAR_ENHANCE, int)): st.GEAR_ENHANCE = 12
    elif (st.GEAR_ENHANCE < 0) | (st.GEAR_ENHANCE > 15): st.GEAR_ENHANCE = 12
    if (st.FLAT_SUB>1)|(st.FLAT_SUB<0):
        print(type(st.FLAT_SUB))
        st.FLAT_SUB = 0.8
        print("Flat sub weighting is outside limits, set to default of 80%")
    if (st.FLAT_MAIN>1)|(st.FLAT_MAIN<0):
        st.FLAT_MAIN = 0.5
        print("Flat main stat weighting (Neck,Ring,Boot) is outside limits, set to default of 50%")
    if st.KEEP_CURR_GEAR == 1:  print("Gear currently equipped on the hero will be kept")
    else:  print("Gear currently equipped on your heroes may be replaced during optimization")
    return

def verify_item_input(df):
    check_error = 0
    gear_lvl = df['level']
    enhance = df['enhance']
    tier = gear_tier[gear_tier.Level == gear_lvl]['Tier'].values[0]
    ##check main stat and enhance level
    main_type = df['mainStat'][0]
    main_val = df['mainStat'][1]
    gear_type = df['Type']
    check_error += verify_main_stats(gear_lvl, enhance, main_type, main_val, gear_type)
    ##check substats
    grt_col = "max_" + tier.lower()
    pwrup = math.floor( enhance / 3 )
    tot_pwr = 0
    for stat in gear_rating_lookup.stat.values:
        sub_limit = gear_rating_lookup[gear_rating_lookup.stat == stat][grt_col].values
        if stat in (['CRIT','CDMG','HP%','ATK%','DEF%','EFF','RES']):
            sub_limit = sub_limit * 100
        val = df[stat]
        tot_pwr += math.ceil(val / sub_limit)
        sub_pred = (1+pwrup) * sub_limit
        if sub_pred < val:  check_error+=1
        if (val > 0) & (gear_rating_lookup[gear_rating_lookup.stat == stat]['stat_in'].values == main_type):  check_error+=1
    if (4 - df['grade'] + pwrup) < tot_pwr:
        check_error += 100
    return check_error

def verify_main_stats(gear_lvl, enhance, main_type, main_val, gear_type):
    main_error = 0
    ##main type
    if (gear_type == 0) & (main_type != 'Atk'): main_error = 1
    if (gear_type == 1) & (main_type != 'HP'): main_error = 1
    if (gear_type == 2) & (main_type != 'Def'): main_error = 1
    if (gear_type == 3) & (main_type in(['Eff','Res','Spd'])): main_error = 1
    if (gear_type == 4) & (main_type in(['CChance','CDmg','Spd'])): main_error = 1
    if (gear_type == 5) & (main_type in(['CChance','CDmg','Eff','Res'])): main_error = 1
    ##main stat
    base_stat = gear_tier[(gear_tier.Level == gear_lvl)][main_type].values[0]
    projected_stat = base_stat * grt.gear_scaling[enhance]
    if (main_val > projected_stat*1.01) | (main_val < projected_stat * 0.88):
        main_error += 1
    return main_error*10

# ******************************************
# ###### FILE CONVERSION
def hero_json_to_df(chars, data):
    char_df = pd.read_csv('../inp/character_data.csv')
    char_list = np.sort(char_df['Character'].unique())
    print("Missing hero stats in source file for:",[x for x in chars if x not in char_list])
    data['heroes'] = clean_up_dictionary_input(data['heroes'], 'Artifact', 'BonusStats')
    df = pd.DataFrame( char_list , columns = ['Name'] )
    df2 = pd.DataFrame(data['heroes'])
    df = pd.merge(df,df2[['Name','Lvl','BonusStats']],how='left',on=['Name'])
    df['Lvl'] = df['Lvl'].fillna(st.MIN_LEVEL)
    df['Lvl'] = df['Lvl'].clip(lower=st.MIN_LEVEL)
    df = df.merge(char_df, how='left', left_on = ['Name','Lvl'], right_on = ['Character','Level'])
    if len(df['Character'][df['Atk'].isnull()]) > 0:
        print("Error: Character data missing from source file", df['Name'][df['Atk'].isnull()].values)
        exit()
    return df, char_list

def item_json_to_df(data):
    #clean up formatted to increase success of raw input
    data['items'] = clean_up_dictionary_input(data['items'], 'ability', 'enhance')
    for sub in subs_cols:
        data['items'] = clean_up_dictionary_input(data['items'], sub, ['',0])
    #define target input columns and formatting
    default_input_format =  {'hero': '','enhance': 0, 'slot': '', 'level': 0, 'set': '', 'rarity': '',
                            'mainStat': ['X', 0], 'subStat1': ['X', 0], 'subStat2': ['X', 0], 'subStat3': ['X', 0], 'subStat4': ['X', 0],
                            'id': '','locked': False}
    data_list = [default_input_format]
    data_list.extend(data['items'])
    #convert to dataframe
    df = pd.DataFrame(data_list, columns = default_input_format.keys())
    df = df[1:]
    df['grade'] = df['rarity'].map(grt.r_map)
    df['Type'] = df['slot'].map(grt.t_map)
    return df

def clean_up_dictionary_input(input_dict, key1, key2):
    """Specific data cleanup to improves compatibility with compeanansi OCR output"""
    if type(key2) == str:
        for i in range(0,len(input_dict)):
            if key1 in input_dict[i]:
                input_dict[i][key2] = input_dict[i][key1]
    elif type(key2) == list:
        for i in range(0,len(input_dict)):
            if key1 in input_dict[i]:
                if type(input_dict[i][key1]) != list:
                    input_dict[i][key1] = key2
            else:
                input_dict[i][key1] = key2
    return input_dict.copy()

# ******************************************
# ####### START UP MESSAGES AND SET UP
def startup_msg1(target_stats):
    hero_order = target_stats['Hero_Order']
    print("Heroes for optimization:", hero_order)
    if st.NO_EQUIPPED_GEAR == 1:
        print("No equipped gear will be included in optimization.")
    else:
        print("Gear on the following heroes is locked and cannot be stolen from another hero.", target_stats['Lock_Gear'])
    print("Gear will be unlocked if new gear is equipped on that hero")
    return hero_order

def startup_msg2(df, lock_gear):
    df['reco'] = np.where( df['hero'].isin(lock_gear) , df['hero'], df['reco'] )
    print("Total # of items loaded:", len(df) )
    if st.NO_EQUIPPED_GEAR == 1: print("Unequipped gear will be used. # of items: ", len(df[(df.hero == np.nan) | (df.hero == '')]) )
    elif len(lock_gear) > 0:  print("Unequipped and unlocked gear will be used.  # of items", len(df[df.reco == '']) )
    else:  print("All gear will be used.")
    return df

def start_hero(char, target_stats):
    print("Hero: ", char) #, "Level ", df_hero[df_hero.Name == char]['Lvl'].values)
    if char in target_stats:
        build = char
        print("Customer character build")
    elif char in target_stats["Type"]:
        build = target_stats['Type'][char]
        print("Character assigned template build:", build)
    else:
        print("No build assigned to this character")
        build = 'General'
    print("Build type: ", build, "Stat priority: ", target_stats[build]['Prio'])

    input_sets = target_stats[build]['input_sets']
    exclude_sets = target_stats[build]['exclude_sets']
    include_sets = gen_input_sets(input_sets, exclude_sets)
    print("Sets to include for this character:", include_sets)
    target_stats[build]['include_sets'] = include_sets.tolist()
    if any(item in include_sets for item in set_4.Set_Nm.values) == True:
        FORCE_4SET = 1
        print("Looking for combinations using a four piece set only.")
        print("To include combinations of three 2 gear sets, set FORCE_4SET = 0")
    else:
        FORCE_4SET = 0
        print("Accepts all set combinations (4set+2set or 3x2set)")
    return FORCE_4SET, char, target_stats[build]

# ******************************************
# ####### ITEM POTENTIAL FUNCTIONS
# generates individual gear ratings and substat efficiency
def gear_stats(df):
    newcols = {}
    for code in gear_rating_lookup.code.values:
        col = [0] * len(df)
        for in_col in subs_cols:
            temp_df = df.copy()
            temp_df[['b1', 'b2']] = pd.DataFrame(temp_df[in_col].tolist(), index=temp_df.index)
            m = np.where ( temp_df['b1'] == grl['stat_in'][code], 1, 0)
            t = m * np.where(np.isnan(temp_df['b2']), 0, temp_df['b2'])
            col += t
        newcols[grl['stat'][code]] = col
        #pd.concat(df[stat] , axis=1)
    return pd.concat([df, pd.DataFrame(newcols, index=df.index)], axis=1)

## Item Potential Function
def item_potential(df):
    GR = 0
    spd_ind = 0
    spd_val = 0
    gear_lvl = df['level']
    main_type = df['mainStat'][0]
    main_val = df['mainStat'][1]
    df['main_tp'] = main_type
    df['main_val'] = main_val
    main_rating = gear_tier[gear_tier.Level == gear_lvl]['X_Factor'].values[0]
    main_rating = np.where( (df['Type'] >= 3)&(main_type in ['Atk','HP','Def']) , main_rating*st.FLAT_MAIN , main_rating )
    rarity = df['grade']
    for stat in gear_rating_lookup.stat.values:
        val = df[stat]
        x = gear_rating_lookup[gear_rating_lookup.stat == stat]['multiplier'].values
        z = x[0] / 9
        rating = val * z * np.where( stat in ['ATK','HP','DEF'] , st.FLAT_SUB , 1 )
        GR = GR + rating
    df['GR'] = GR
    spd_ind = np.where(df['SPD'] > 0, 1, 0)
    spd_val = df['SPD']
    enhance = df['enhance']
    pwrup = int( (15-enhance) / 3 )
    minp = GR + pwrup/18 * np.where(gear_lvl<86,0.87,1)*np.where(gear_lvl<58,0.87,1)
    df['minp'] = minp
    maxp = GR + pwrup/9 * np.where(gear_lvl<86,0.87,1)*np.where(gear_lvl<72,0.87,1)*np.where(gear_lvl<58,0.87,1)
    df['maxp'] = maxp
    df['spdp'] = np.where(main_type=='Spd',0,spd_potential(pwrup,rarity,spd_ind)) \
            * np.where(gear_lvl>88, 5, np.where(gear_lvl>57,4,3) )  + spd_val
    df['rating'] = main_rating * 1.4 + (minp+maxp)/2 + np.where(main_type == 'Spd', 0.2, 0) + spd_val*0.01
    df['efficiency'] =  int(main_rating * 44 + GR * 66 + np.where(main_type == 'Spd', 2, 0) + spd_val * 0.1)
    df['max_eff'] =  int(main_rating * 44 + maxp * 66 + np.where(main_type == 'Spd', 2, 0) + spd_val * 0.1)
    df['current_eff'] = GR * 6.6 + main_rating * grt.gear_scaling[enhance]/5 * 4.4
    return df

def spd_potential(p,g,s):  ## p = power ups remaining, item rarity, if speed is currently a substat
    v1 = np.where( (s==0)&(g>0)&(p>g) , 2, 0 )  ##returns 2 for heroic gear below enhance 9 or rare gear below enhance 6 if no speed sub currently
    v2 = np.where( s==1 , max(min(p,p-g),np.where(p>0,1,0)),0 )
    return (v1+v2)

# ******************************************
# ####### GENERATE COMBINATIONS TO PRODUCE COMPLETE SETS
# ### GET COMBINATIONS OF EACH SET
L = [0,1,2,3,4,5]
l4 = [",".join(map(str, comb)) for comb in itertools.combinations(L, 4)]
l2 = [",".join(map(str, comb)) for comb in itertools.combinations(L, 2)]

def set_combo(item_df, hero_name, l4, l2):
    # ### EVERY COMBINATION OF UNBROKEN SETS
    gear_comb_dict = {}
    temp_df = item_df[ (item_df.reco.isnull()) | (item_df.reco == '') | (item_df.reco == hero_name)].copy()
    if st.NO_EQUIPPED_GEAR == 1:
        temp_df = temp_df[ (temp_df.hero == '') | (temp_df.hero.isnull()) | (temp_df.hero == hero_name) ]
    temp_df.sort_values(by = ['rating'], ascending = False, inplace=True)
    if st.KEEP_CURR_GEAR == 1:
        temp_slots = temp_df[(temp_df.hero == hero_name)].Type.values
        temp_df = temp_df[(~temp_df.Type.isin(temp_slots)) | (temp_df.hero == hero_name)]
        temp_df = temp_df.groupby('slot').head(st.GEAR_LIMIT).reset_index(drop=True)
    else:
        temp_df_b = temp_df.groupby('slot').head(st.GEAR_LIMIT).reset_index(drop=True)
        temp_df_c = temp_df.groupby(['slot','set']).head(1).reset_index(drop=True)
        temp_df.sort_values(by = ['efficiency'], ascending = False, inplace=True)
        temp_df_d = temp_df.groupby(['slot','set']).head(1).reset_index(drop=True)
        temp_df = temp_df_b.copy()
        temp_df = temp_df.append([temp_df_c,temp_df_d])
        temp_df = temp_df.drop_duplicates(['id'])
        temp_df.reset_index(inplace=True)
    ##iterate through set gear combinations for two piece sets
    for set_nm in set_2.Set_Nm:
        temp_dict = {}
        temp_df2 = temp_df[ (temp_df.set == set_nm) ]
        for i in range(0,len(l2)):
            temp_l = list(set(l2[i]))
            temp_l.remove(',')
            itr = list(itertools.product( temp_df2[(temp_df2.Type == int(temp_l[0]))].id.values, \
                                   temp_df2[(temp_df2.Type == int(temp_l[1]))].id.values ))
            app = [ [set_nm], temp_l, itr ]
            temp_dict[l2[i]] = itr
        for i in range(0,len(l4)):
            temp_l = list(set(l4[i]))
            temp_l.remove(',')
            itr = list(itertools.product( temp_df2[(temp_df2.Type == int(temp_l[0]))].id.values, \
                                temp_df2[(temp_df2.Type == int(temp_l[1]))].id.values, \
                                temp_df2[(temp_df2.Type == int(temp_l[2]))].id.values, \
                                temp_df2[(temp_df2.Type == int(temp_l[3]))].id.values))
            app = [ [set_nm], temp_l, itr ]
            temp_dict[l4[i]] = itr
        gear_comb_dict[set_nm] = temp_dict
    ##iterate through set gear combinations for four piece sets
    for set_nm in set_4.Set_Nm:
        temp_dict = {}
        temp_df2 = temp_df[ (temp_df.set == set_nm) ]
        for i in range(0,len(l4)):
            temp_l = list(set(l4[i]))
            temp_l.remove(',')
            itr = list(itertools.product( temp_df2[(temp_df2.Type == int(temp_l[0]))].id.values, \
                                temp_df2[(temp_df2.Type == int(temp_l[1]))].id.values, \
                                temp_df2[(temp_df2.Type == int(temp_l[2]))].id.values, \
                                temp_df2[(temp_df2.Type == int(temp_l[3]))].id.values))
            app = [ [set_nm], temp_l, itr ]
            temp_dict[l4[i]] = itr
        gear_comb_dict[set_nm] = temp_dict
    return gear_comb_dict

def l4comb(l4,l2):
    l4_comb = []
    zz = 0
    for i in range(0,len(l4)):
        for j in range(0,len(l2)):
            x4 = list(set(l4[i]))
            x4.remove(',')
            x2 = list(set(l2[j]))
            x2.remove(',')
            x6 = x2.copy()
            x6.extend(x4)
            if len(np.unique(x6)) == 6:
                zz += 1
                add_list = [l4[i],l2[j]]
                l4_comb.append(add_list)
    return l4_comb

def l2comb(l2):
    l2_comb = []
    zz = 0
    for i in range(0,5):
        for j in range(5,len(l2)):
            for k in range(5,len(l2)):
                x21 = sorted(list(set(l2[i])))
                x21.remove(',')
                x22 = sorted(list(set(l2[j])))
                x22.remove(',')
                x23 = sorted(list(set(l2[k])))
                x23.remove(',')
                x6 = x21.copy()
                x6.extend(x22)
                x6.extend(x23)
                if (x21[0]<x22[0]) & (x22[0]<x23[0]) & (len(np.unique(x6))==6):
                    zz += 1
                    add_list = [l2[i],l2[j],l2[k]]
                    l2_comb.append(add_list)
    return l2_comb

# ### ALL GEAR COMBINATIONS WHERE UNBROKEN
def set_combination_iterate(gear_comb_dict, set4_list, set2_list, FORCE_4SET):
    ##df columns
    Itr_Sets = []
    Set_1 = []
    Set_2 = []
    Set_3 = []
    Gear = []
    Gear2 = []
    Complete = []
    l4_comb = l4comb(l4,l2)
    l2_comb = l2comb(l2)
    for set_nm4 in set4_list:
        for set_nm2 in set2_list:
            for a in range(0,len(l4_comb)):
                code4 = l4_comb[a][0]
                code2 = l4_comb[a][1]
                g4_set = gear_comb_dict[set_nm4][code4]
                g2_set = gear_comb_dict[set_nm2][code2]
                Itr_Sets.append([set_nm4,set_nm2])
                itr = list(itertools.product( g4_set, g2_set ) )
                Set_1.extend([set_nm4]*len(itr))
                Set_2.extend([set_nm2]*len(itr))
                Set_3.extend([None]*len(itr))
                Gear.extend(itr)
                Complete.extend([1]*len(itr))
    if FORCE_4SET != 1:
        for set_nm in itertools.combinations(set2_list, 3):
            for a in range(0,len(l2_comb)):
                code1 = l2_comb[a][0]
                code2 = l2_comb[a][1]
                code3 = l2_comb[a][2]
                g2_set1 = gear_comb_dict[set_nm[0]][code1]
                g2_set2 = gear_comb_dict[set_nm[1]][code2]
                g2_set3 = gear_comb_dict[set_nm[2]][code3]
                Itr_Sets.append([set_nm[0],set_nm[1],set_nm[2]])
                itr = list(itertools.product( g2_set1, g2_set2, g2_set3 ) )
                Set_1.extend([set_nm[0]]*len(itr))
                Set_2.extend([set_nm[1]]*len(itr))
                Set_3.extend([set_nm[2]]*len(itr))
                Gear.extend(itr)
                Complete.extend([1] * len(itr))
    return list(zip(Set_1,Set_2,Set_3,Complete,Gear))

def final_gear_combos(sc_output, char):
    sc_df = pd.DataFrame(sc_output, columns =['Set_1', 'Set_2', 'Set_3','Complete','Gear'])
    sc_df['gear_list'] = sc_df.apply(lambda row: gear_split(row) , axis=1)
    sc_df[['0','1','2','3','4','5']] = pd.DataFrame(sc_df.gear_list.values.tolist(), index= sc_df.index)
    sc_df = sc_df.drop_duplicates(['0','1','2','3','4','5'])
    current_gear = pd.DataFrame(columns = ['Set_1', 'Set_2', 'Set_3', 'Complete', 'Gear', 'gear_list', '0', '1', '2', '3', '4', '5' ], index = ['0'])
    try:
        nix=0
        for gid in range(0,6):
            current_gear[str(gid)] = df_items[(df_items.hero == char) & (df_items.Type == gid)][['id']].values
            val = df_items[(df_items.hero == char) & (df_items.Type == gid)][['reco']].values
            if (val > '') & (val!=char): nix = 1
        current_gear = get_set_bonus(current_gear, df_items)
        if nix==1: current_gear['Complete'] = 'PREVIOUS'
        elif nix==0: current_gear['Complete'] = 'CURRENT'
        sc_df = sc_df.append(current_gear)
        sc_df = sc_df.reset_index()
        hero_with_gear = 1
    except:
        hero_with_gear = 0
    return sc_df, hero_with_gear

def gear_split(df):
    ##extract gear ids from tuples produced in sc.set_combination_iterate
    if df.Set_3 == None:
        u,v = df.Gear
        m,n,o,p = u
        q,r = v
    else:
        u,v,w = df.Gear
        m,n = u
        o,p = v
        q,r = w
    gear_list = list(np.sort([m,n,o,p,q,r]))
    return gear_list

def gen_input_sets(include, exclude, autofill = 0):
    ##initialize placeholder variables
    x = 0
    iv = 0
    ii = 0
    ##generate list of sets to use in gear analysis based on user inputs
    if len(include) == 0:
        include = set_df[~set_df.Set_Nm.isin(exclude)]['Set_Nm'].values
    else:
        for set_nm in include:
            x += set_df[set_df.Set_Nm == set_nm].iloc[0]['Set_Lg']
            iv = 1 if set_nm in (set_df[set_df.Set_Lg == 4]['Set_Nm'].values) else iv
            ii = 1 if set_nm in (set_df[set_df.Set_Lg == 2]['Set_Nm'].values) else ii
        if iv == 1:
            exclude.extend(list(set(set_df[set_df.Set_Lg == 4]['Set_Nm'].values)-set(include)))
        if ii == 1:
            exclude.extend(list(set(set_df[set_df.Set_Lg == 2]['Set_Nm'].values)-set(include)))
        if (x == 6):
            pass
        elif (x > 6) & (ii == 1):
            pass
        elif (ii == 0) & (iv == 1):
            include.extend(set_df[(set_df.Set_Lg == 2)&(~set_df.Set_Nm.isin(exclude))]['Set_Nm'].values)
        elif (autofill == 0):
            pass
        elif (x == 2):
            include.extend(set_df[(set_df.Set_Lg == 4)&(~set_df.Set_Nm.isin(exclude))&(~set_df.Set_Nm.isin(include))]['Set_Nm'].values)
            include.extend(set_df[(set_df.Set_Lg == 2)&(~set_df.Set_Nm.isin(exclude))&(~set_df.Set_Nm.isin(include))]['Set_Nm'].values)
        elif (x < 6):
            include.extend(set_df[(set_df.Set_Lg == 2)&(~set_df.Set_Nm.isin(exclude))&(~set_df.Set_Nm.isin(include))]['Set_Nm'].values)
            include.extend(set_df[(set_df.Set_Lg == 4)&(~set_df.Set_Nm.isin(exclude))&(~set_df.Set_Nm.isin(include))]['Set_Nm'].values)
    return include

# ******************************************
# ####### CALCULATE HERO STATS AND RECOMMEND OPTIMAL SETS
def get_set_bonus(df, item_df):
    #get data for set combinations
    if len(df) > 1:
        gears = df[['0','1','2','3','4','5']].values
    else:
        gears = df[['0','1','2','3','4','5']].values[0]
    set_stats = item_df[item_df.id.isin(gears)].groupby(['set']).count()[['id']]
    set_stats = set_df.merge(set_stats, how='inner', left_on='Set_Nm' , right_on='set')
    set_stats['Mult'] = (set_stats.id / set_stats.Set_Lg).astype(int)
    complete_sets_ind = (set_stats.Mult * set_stats.Set_Lg).sum()
    set_list = []
    for set_nm in set_stats.Set_Nm.values:
        v = set_stats[(set_stats.Set_Nm == set_nm)].iloc[0]['Mult']
        for i in range(0, v):
            set_list.append(set_nm)
    #set info
    df['Complete'] = np.where(complete_sets_ind == 6, 1,0)
    df['Set_1'] = set_list[0] if len(set_list) >= 1 else None
    df['Set_2'] = set_list[1] if len(set_list) >= 2 else None
    df['Set_3'] = set_list[2] if len(set_list) >= 3 else None
    return df

def enhance_mult(x):
    y = st.GEAR_ENHANCE
    z = np.where( (x < y) , grt.gear_scaling[y]/x.map(grt.gear_scaling) , 1 )
    return z

def set_sum(df):
    setst_df = df.copy()
    for stat in np.unique(set_df[set_df.Bonus_Stat != 'NA'].Bonus_Stat.values):
        mult = [0]*len(setst_df)
        temp_set = set_df[set_df.Bonus_Stat == stat]
        mult += np.where(setst_df['Set_1'].isin(temp_set.Set_Nm),1,0)
        mult += np.where(setst_df['Set_2'].isin(temp_set.Set_Nm),1,0)
        mult += np.where(setst_df['Set_3'].isin(temp_set.Set_Nm),1,0)
        temp_bonus = temp_set.Bonus.values * mult
        setst_df[stat] = temp_bonus
    return setst_df

def subst_sum(df, item_df):
    subst_cols = list(gear_rating_lookup.stat)
    subst_cols.extend(['id','GR'])
    suff_cols = ['0','1','2','3','4','5']
    subst_df = df.copy()
    for subst in subst_cols:
        subst_df[subst] = 0
    for col in range(0,6):
        subst_df = pd.merge(subst_df, item_df[subst_cols], how='left', \
                              left_on = [str(col)], right_on = ['id'], suffixes=('','_'+str(col)) )
    for subst in gear_rating_lookup.stat.values:
        subst_df[subst] = subst_df[subst+'_0']+subst_df[subst+'_1']+subst_df[subst+'_2']+subst_df[subst+'_3']+subst_df[subst+'_4']+subst_df[subst+'_5']
    drop_cols = []
    for subst in subst_cols:
        for suffix in ['_0','_1','_2','_3','_4','_5']:
            drop_cols.append(subst+suffix)
    drop_cols.extend(['id','Gear'])
    subst_df.drop(columns=drop_cols , axis=1, inplace=True)
    return subst_df

def mainst_sum(df, item_df):
    mainst_df = df.copy()
    mainst_cols = ['id','main_tp','main_val','level','enhance']
    for subst in mainst_cols:
        mainst_df[subst] = 0
    for subst in gear_rating_lookup.stat.values:
        mainst_df[subst] = 0
    for col in range(0,6):
        mainst_df = pd.merge(mainst_df, item_df[mainst_cols], how='left', left_on = [str(col)], right_on = ['id'], suffixes=('','_'+str(col)) )
    for stat in gear_rating_lookup.stat.values:
        for i in range(0,6):
            col1 = 'main_tp_'+str(i)
            col2 = 'main_val_'+str(i)
            col3 = 'enhance_'+str(i)
            enh_mult = enhance_mult(mainst_df[col3])
            mainst_df[stat] += np.where( mainst_df[col1].map(grt.s_map) == stat, (mainst_df[col2] * enh_mult).astype(int), 0)
    drop_cols = []
    for subst in ['id','level','main_val','main_tp','enhance']:
        for suffix in ['_0','_1','_2','_3','_4','_5']:
            drop_cols.append(subst+suffix)
    drop_cols.extend(['id','Gear','main_tp','main_val','level','enhance'])
    mainst_df.drop(columns=drop_cols , axis=1, inplace=True)
    return mainst_df

def bonus_eqp_sum(hero_df):
    bonus_eqp_df = hero_df['Name'].copy()
    hero_bonus = hero_df['BonusStats'].values[0]
    for stat in np.unique(gear_rating_lookup.stat_in.values):
        try: bonus_eqp_df[stat] = hero_bonus[stat]
        except: bonus_eqp_df[stat] = 0
    return bonus_eqp_df

def pull_hero_stat_format(df_flag, stat, input_set):
    if df_flag == 1:
        stat_value = input_set[stat].values
    else:
        stat_value = input_set[stat].values[0]
    return stat_value
def get_combo_stats(df, df_hero, mainst_df, subst_df, setst_df, hero_ee, char, target_stats):
    if char == 'all':
        df['Char'] = df_hero['Name']
        df_hero_stat = df_hero
    else:
        df['Char'] = [char] * len(df)
        df_hero_stat = df_hero[df_hero.Name == char]
    if len(df) > 1: df_flag = 1
    else: df_flag = 0
    df['ATK'] =  (pull_hero_stat_format(df_flag, 'Atk', df_hero_stat)   *(100+mainst_df['ATK%']+subst_df['ATK%']+setst_df['ATK']+hero_ee['AtkP'])/100  +mainst_df['ATK']+subst_df['ATK']+hero_ee['Atk']).astype(int)
    df['HP'] =   (pull_hero_stat_format(df_flag, 'HP', df_hero_stat)   *(100+mainst_df['HP%']+subst_df['HP%']+setst_df['HP']+hero_ee['HPP'])/100   +mainst_df['HP'] +subst_df['HP']+hero_ee['HP']).astype(int)
    df['DEF'] =  (pull_hero_stat_format(df_flag, 'Def', df_hero_stat)   *(100+mainst_df['DEF%']+subst_df['DEF%']+setst_df['DEF']+hero_ee['DefP'])/100 +mainst_df['DEF'] +subst_df['DEF']+hero_ee['Def']).astype(int)
    df['SPD'] =  (pull_hero_stat_format(df_flag, 'Speed', df_hero_stat) * ((100+setst_df['SPD'].values)/100) +mainst_df['SPD']+subst_df['SPD']+hero_ee['Spd'] ).astype(int)
    df['CRIT'] = np.minimum((pull_hero_stat_format(df_flag, 'Crit Rate', df_hero_stat) +mainst_df['CRIT']+subst_df['CRIT']+setst_df['CRIT']+hero_ee['CChance']).astype(int),100)
    df['CDMG'] = (pull_hero_stat_format(df_flag, 'Crit Dmg', df_hero_stat)  +mainst_df['CDMG']+subst_df['CDMG']+setst_df['CDMG']+hero_ee['CDmg']).astype(int)
    df['EFF'] =  np.minimum((pull_hero_stat_format(df_flag, 'Effectiveness', df_hero_stat) +mainst_df['EFF']+subst_df['EFF']+setst_df['EFF']+hero_ee['Eff']).astype(int),100)
    df['RES'] =  np.minimum((pull_hero_stat_format(df_flag, 'Eff Resist', df_hero_stat)    +mainst_df['RES']+subst_df['RES']+setst_df['RES']+hero_ee['Res']).astype(int),100)
    ### additional columns for prioritization
    # df['CATK'] = (df['ATK'] * df['CDMG'] / 100).astype(int)
    # df['CMult'] = df['CRIT'] / 100 * df['CDMG'] / 100
    # df['WR'] = ((df['ATK']/1500 + df['SPD']/100 + df['CRIT']/30 + df['CDMG']/150 \
    #             + df['HP']/5000 + df['DEF']/400 + df['EFF']/30 + df['RES']/30)*10).astype(int)
    cp1 = round( ((df['ATK']*1.6 + df['ATK']*1.6*df['CRIT']*df['CDMG']/10000) * (1+(df['SPD']-45)*0.02) + df['HP'] + df['DEF']*9.3) * (1 + (df['RES']+df['EFF']) / 400) , 0)
    cp2 = 1 + 0.08 * df_hero_stat['SC'].values[0] + 0.02 * df_hero_stat['EE'].values[0]
    df['CP'] = round(cp1 * cp2,0)
    df['Dmg_Rating'] = ((df['ATK']/ 2500 \
                    * (df['CRIT']/100 * df['CDMG']/100 + (100-df['CRIT'])/100) \
                    * df['SPD'] / 150)*10).astype(int)
    df['EHP'] = (df['HP'] * (1 + df['DEF']/300) / 100).astype(int)
    df['PI'] = (df['ATK']/df_hero_stat['Atk'].values[0]/grl['max_t7'][0] \
                + df['SPD']/df_hero_stat['Speed'].values[0]/grl['max_t7'][2] \
                + (df['CRIT'] - df_hero_stat['Crit Rate'].values[0])/100/grl['max_t7'][3] \
                + (df['CDMG']-df_hero_stat['Crit Dmg'].values[0])/100/grl['max_t7'][4] \
                + df['HP']/df_hero_stat['HP'].values[0]/grl['max_t7'][5] \
                + df['DEF']/df_hero_stat['Def'].values[0]/grl['max_t7'][7] \
                + (df['EFF'] - df_hero_stat['Effectiveness'].values[0])/100/grl['max_t7'][9] \
                + (df['RES'] - df_hero_stat['Eff Resist'].values[0])/100/grl['max_t7'][10]).astype(int)
    df['GR'] = subst_df['GR']/6
    df['WW'] = round(df['ATK']/df_hero_stat['Atk'].values[0]/grl['max_t7'][0]*target_stats['ATK']['Weight'] \
                + df['SPD']/df_hero_stat['Speed'].values[0]/grl['max_t7'][2]*target_stats['SPD']['Weight'] \
                + (df['CRIT']-df_hero_stat['Crit Rate'].values[0])/100/grl['max_t7'][3]*target_stats['CRIT']['Weight'] \
                + (df['CDMG']-df_hero_stat['Crit Dmg'].values[0])/100/grl['max_t7'][4]*target_stats['CDMG']['Weight'] \
                + df['HP']/df_hero_stat['HP'].values[0]/grl['max_t7'][5]*target_stats['HP']['Weight'] \
                + df['DEF']/df_hero_stat['Def'].values[0]/grl['max_t7'][7]*target_stats['DEF']['Weight'] \
                + (df['EFF']-df_hero_stat['Effectiveness'].values[0])/100/grl['max_t7'][9]*target_stats['EFF']['Weight'] \
                + (df['RES']-df_hero_stat['Eff Resist'].values[0])/100/grl['max_t7'][10]*target_stats['RES']['Weight'] , 2)
    df['Element'] = df_hero_stat['Element']
    df['Role'] = df_hero_stat['Role']
    return df

def run_stat_reco(output, hero_with_gear, hero_target):
    print('Progress: Step 2/4 Complete.  Number of unique combinations for optimization', len(output[output.Complete!='PREVIOUS']) )
    if hero_with_gear == 1:
        choice_df = output.iloc[-1:,:].copy()
        output = output.sort_values(by = ['WW'], ascending = False )  ## faster than inplace
    else:
        output = output.sort_values(by = ['WW'], ascending = False )  ## faster than inplace
        choice_df = output.iloc[:1,:].copy()
    ## regular process
    output2 = output.copy()
    for stat in set_df[set_df.Bonus_Stat != 'NA'].Bonus_Stat.values:
        output2.drop( output2[(output2[stat]).astype(int) < hero_target[stat]['Min']].index, inplace=True)
        output2.drop( output2[(output2[stat]).astype(int) > hero_target[stat]['Max']].index, inplace=True)
    print("Progress: Step 3/4 Complete.  The number of combinations available with stats in specified range is: ",len(output2))
    if len(output2)==0:
        output2 = output.copy()
        print("Since no combinations meet criteria, best alternative combinations will be shown based on desired stat weighting.")
    ## record high stat options to output for manual selection dataset
    choice_df = choice_df.append(output.iloc[:3,:])
    choice_df = choice_df.append(output2.sort_values(by = ['WW'], ascending = False ).iloc[:3,:] )
    try:
        for STAT in np.unique(hero_target['Prio']):
            choice_df = choice_df.append(output.sort_values(by = STAT, ascending = False ).iloc[:3,:] )
            choice_df = choice_df.append(output2.sort_values(by = STAT, ascending = False ).iloc[:3,:] )
    except: pass
    ## look for sets with top priority stats and get recommended output
    try:
        for i in range(0,len(hero_target['Prio'])):
            target = hero_target['Prio'][i]
            cut_off = output2[target].quantile(0.9)
            output2 = output2[output2[target] >= cut_off ]
    except: pass
    print("combinations after prio sortings ", len(output2) )
    idx_reco = output2.iloc[[0]].index.values[0]
    ## add final groomed options to output for manual selection dataset
    choice_df = choice_df.append(output2.sort_values(by = ['WW'], ascending = False ).iloc[:3,:] )
    choice_df = choice_df.append(output2[(output2.Set_1.isin(['Unity','Immunity','Penetration'])) | (output2.Set_2.isin(['Unity','Immunity'])) | \
            (output2.Set_3.isin(['Unity','Immunity']))].sort_values(by = ['WW'], ascending = False ).iloc[:3,:] )
    choice_df = choice_df.append(output2[(output2.Set_1.isin(['Counter','Lifesteal','Rage','Injury','Revenge']))].sort_values(by = ['WW'], ascending = False ).iloc[:3,:] )
    try:
        for STAT in np.unique(hero_target['Prio']):
            choice_df = choice_df.append(output2.sort_values(by = STAT, ascending = False ).iloc[:3,:] )
    except: pass
    choice_df = choice_df.drop(axis = 1, columns = ['gear_list','Gear']).drop_duplicates()
    return idx_reco, choice_df
