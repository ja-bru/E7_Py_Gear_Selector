# #### SET UP

import pandas as pd
import numpy as np
import math
import itertools
import setup as st
from datetime import datetime
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

# ### FUNCTIONS
def verify_setup():
    print("Checking program configuration")
    if st.SELECTOR != 1:  print("Automated optimization is set, all heroes will run in order without user input to select gear")
    if st.MIN_LEVEL != 60:  st.MIN_LEVEL = 50
    if ~(isinstance(st.GEAR_LVL, int) & (0<=st.GEAR_LVL<=15)): st.GEAR_LVL = 12
    if ~(0<=st.FLAT_SUB<=1):
        st.FLAT_SUB = 0.8
        print("Flat sub weighting is outside limits, set to default of 80%")
    if ~(0<=st.FLAT_MAIN<=1):
        st.FLAT_MAIN = 0.5
        print("Flat main stat weighting (Neck,Ring,Boot) is outside limits, set to default of 50%")
    if st.KEEP_CURR_EQUIP == 1:  print("Gear currently equipped on the hero will be kept")
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
        print( 4 - df['grade'] + pwrup , tot_pwr)
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

def hero_json_to_df(chars, data):
    df = pd.DataFrame( chars , columns = ['Name'] )
    df2 = pd.DataFrame(data['heroes'])
    df = pd.merge(df,df2[['Name','Lvl','BonusStats']],how='left',on=['Name'])
    print(df)
    df['Lvl'] = df['Lvl'].fillna(st.MIN_LEVEL)
    df['Lvl'] = df['Lvl'].clip(lower=st.MIN_LEVEL)
    char_df = pd.read_csv('../inp/character_data.csv')
    df = df.merge(char_df, how='left', left_on = ['Name','Lvl'], right_on = ['Character','Level'])
    return df

def item_json_to_df(data):
    df = pd.DataFrame(data['items'])
    df.rename(columns={'ability':'enhance'}, inplace=True) ##added this line for anyone using compeanansi OCR tool
    df[subs_cols] = df[subs_cols].applymap(lambda x: [0,0] if x is np.nan else x)
    #df = df.apply(lambda row: ocr_cleanup(row), axis=1)
    df['grade'] = df['rarity'].map(grt.r_map)
    df['Type'] = df['slot'].map(grt.t_map)
    return df

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

## Item Potential Function generates individual gear ratings and substat efficiency
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

def set_combo(item_df, hero_name, l4, l2):
    # ### EVERY COMBINATION OF UNBROKEN SETS
    gear_comb_dict = {}
    temp_df = item_df[ (item_df.reco.isnull()) | (item_df.reco == '') | (item_df.reco == hero_name)].copy()
    if st.NO_EQUIPPED_GEAR == 1:
        temp_df = temp_df[ (temp_df.hero == '') | (temp_df.hero.isnull()) | (temp_df.hero == hero_name) ]
    temp_df.sort_values(by = ['rating'], ascending = False, inplace=True)
    if st.KEEP_CURR_EQUIP == 1:
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

    ##iterate through set gear combinations by set
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

def get_set_bonus(df, item_df):
    #get data for set combinations
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
    y = st.GEAR_LVL
    z = np.where( (x < y) , grt.gear_scaling[y]/x.map(grt.gear_scaling) , 1 )
    return z

def set_sum(df):
    # print("started function set sum:   ", datetime.now())
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
    # print("started function subst sum:   ", datetime.now())
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
    # print("started function mainst sum:   ", datetime.now())
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

def get_combo_stats(df, df_hero, mainst_df, subst_df, setst_df, hero_ee, char, target_stats):#, mainst_df, subst_df, setst_df):
    print("started function get combo stats:   ", datetime.now())
    df['Char'] = [char] * len(df)
    df['ATK'] =  (df_hero[df_hero.Name == char]['Atk'].values[0]   *(100+mainst_df['ATK%']+subst_df['ATK%']+setst_df['ATK']+hero_ee['AtkP'])/100  +mainst_df['ATK']+subst_df['ATK']+hero_ee['Atk']).astype(int)
    df['HP'] =   (df_hero[df_hero.Name == char]['HP'].values[0]    *(100+mainst_df['HP%']+subst_df['HP%']+setst_df['HP']+hero_ee['HPP'])/100   +mainst_df['HP'] +subst_df['HP']+hero_ee['HP']).astype(int)
    df['DEF'] =  (df_hero[df_hero.Name == char]['Def'].values[0]   *(100+mainst_df['DEF%']+subst_df['DEF%']+setst_df['DEF']+hero_ee['DefP'])/100 +mainst_df['DEF'] +subst_df['DEF']+hero_ee['Def']).astype(int)
    df['SPD'] =  (df_hero[df_hero.Name == char]['Speed'].values[0] * ((100+setst_df['SPD'].values)/100) +mainst_df['SPD']+subst_df['SPD']+hero_ee['Spd'] ).astype(int)
    df['CRIT'] = np.minimum((df_hero[df_hero.Name == char]['Crit Rate'].values[0] +mainst_df['CRIT']+subst_df['CRIT']+setst_df['CRIT']+hero_ee['CChance']).astype(int),100)
    df['CDMG'] = (df_hero[df_hero.Name == char]['Crit Dmg'].values[0]  +mainst_df['CDMG']+subst_df['CDMG']+setst_df['CDMG']+hero_ee['CDmg']).astype(int)
    df['EFF'] =  np.minimum((df_hero[df_hero.Name == char]['Effectiveness'].values[0] +mainst_df['EFF']+subst_df['EFF']+setst_df['EFF']+hero_ee['Eff']).astype(int),100)
    df['RES'] =  np.minimum((df_hero[df_hero.Name == char]['Eff Resist'].values[0]    +mainst_df['RES']+subst_df['RES']+setst_df['RES']+hero_ee['Res']).astype(int),100)

    ### additional columns for prioritization
        #ratings
    df['Dmg_Rating'] = ((df['ATK']/ 2500 \
            * (df['CRIT']/100 * df['CDMG']/100 + (100-df['CRIT'])/100) \
            * df['SPD'] / 150)*10).astype(int)

    # df['CATK'] = (df['ATK'] * df['CDMG'] / 100).astype(int)

    df['EHP'] = (df['HP'] * (1 + df['DEF']/300) / 100).astype(int)

    # df['WR'] = ((df['ATK']/1500 + df['SPD']/100 + df['CRIT']/30 + df['CDMG']/150 \
    #             + df['HP']/5000 + df['DEF']/400 + df['EFF']/30 + df['RES']/30)*10).astype(int)

    df['PI'] = (df['ATK']/df_hero[df_hero.Name == char]['Atk'].values[0]/grl['max_t7'][0] \
                + df['SPD']/df_hero[df_hero.Name == char]['Speed'].values[0]/grl['max_t7'][2] \
                + (df['CRIT'] - df_hero[df_hero.Name == char]['Crit Rate'].values[0])/100/grl['max_t7'][3] \
                + (df['CDMG']-df_hero[df_hero.Name == char]['Crit Dmg'].values[0])/100/grl['max_t7'][4] \
                + df['HP']/df_hero[df_hero.Name == char]['HP'].values[0]/grl['max_t7'][5] \
                + df['DEF']/df_hero[df_hero.Name == char]['Def'].values[0]/grl['max_t7'][7] \
                + (df['EFF'] - df_hero[df_hero.Name == char]['Effectiveness'].values[0])/100/grl['max_t7'][9] \
                + (df['RES'] - df_hero[df_hero.Name == char]['Eff Resist'].values[0])/100/grl['max_t7'][10]).astype(int)

    df['GR'] = subst_df['GR']/6

    df['WW'] = round(df['ATK']/df_hero[df_hero.Name == char]['Atk'].values[0]/grl['max_t7'][0]*target_stats['ATK']['Weight'] \
                + df['SPD']/df_hero[df_hero.Name == char]['Speed'].values[0]/grl['max_t7'][2]*target_stats['SPD']['Weight'] \
                + (df['CRIT']-df_hero[df_hero.Name == char]['Crit Rate'].values[0])/100/grl['max_t7'][3]*target_stats['CRIT']['Weight'] \
                + (df['CDMG']-df_hero[df_hero.Name == char]['Crit Dmg'].values[0])/100/grl['max_t7'][4]*target_stats['CDMG']['Weight'] \
                + df['HP']/df_hero[df_hero.Name == char]['HP'].values[0]/grl['max_t7'][5]*target_stats['HP']['Weight'] \
                + df['DEF']/df_hero[df_hero.Name == char]['Def'].values[0]/grl['max_t7'][7]*target_stats['DEF']['Weight'] \
                + (df['EFF']-df_hero[df_hero.Name == char]['Effectiveness'].values[0])/100/grl['max_t7'][9]*target_stats['EFF']['Weight'] \
                + (df['RES']-df_hero[df_hero.Name == char]['Eff Resist'].values[0])/100/grl['max_t7'][10]*target_stats['RES']['Weight'] , 2)

    cp1 = round( ((df['ATK']*1.6 + df['ATK']*1.6*df['CRIT']*df['CDMG']/10000) * (1+(df['SPD']-45)*0.02) + df['HP'] + df['DEF']*9.3) * (1 + (df['RES']+df['EFF']) / 400) , 0)
    cp2 = 1 + 0.08 * df_hero[df_hero.Name == char]['SC'].values[0] + 0.02 * df_hero[df_hero.Name == char]['EE'].values[0]
    df['CP'] = round(cp1 * cp2,0)

    return df
