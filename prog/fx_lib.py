# #### SET UP

import pandas as pd
import numpy as np
import itertools
import setup as st
from datetime import datetime

# ### THIS SECTION GENERATES SOME FIXED LOOKUP TABLES FOR GEAR

d = [
    ['ATK%', 'AtkP',  0,  0.13,  0.09,  0.05,  0.11111,  0.08,  0.07,  0.06],
    ['DEF%', 'DefP',  7,  0.13,  0.09,  0.05,  0.11111,  0.08,  0.07,  0.06],
    ['HP%',  'HPP',  5,  0.13,  0.09,  0.05,  0.11111,  0.08,  0.07,  0.06],
    ['EFF',  'Eff',  9,  0.13,  0.09,  0.05,  0.11111,  0.08,  0.07,  0.06],
    ['RES',  'Res',  10,  0.13,  0.09,  0.05,  0.11111,  0.08,  0.07,  0.06],
    ['CDMG', 'CDmg',  4,  0.14,  0.08,  0.04,  0.125,  0.07,  0.06,  0.05],
    ['CRIT', 'CChance',  3,  0.12,  0.06,  0.04,  0.166667,  0.05,  0.04,  0.04],
    ['SPD',  'Spd',  2,  9,  5,  2,  0.2,  4,  4,  3],
    ['DEF',  'Def',  8,  62,  40,  24,  0.025,  35,  30,  30],  ##assumes the maximum flat defense sub for lvl 85 gear is 40
    ['ATK',  'Atk',  1,  103,  50,  30,  0.02222,  40,  35,  35], ##assumes the maximum flat attack sub for lvl 85 gear is 50
    ['HP',   'HP',  6,  540,  225,  140,  0.005556,  155,  145,  140] ##assumes the maximum flat hp sub for lvl 85 gear is 225
]
cols = ['stat',  'stat_in','code','main_t7','max_t7','min_t7','multiplier','max_t6','max_t5','max_t4']
gear_rating_lookup = pd.DataFrame(data = d, columns = cols)
gear_rating_lookup.sort_values(by = ['code'], inplace=True)
gear_rating_lookup.reset_index(inplace=True)
grl = gear_rating_lookup.to_dict()

gear_tier = pd.read_csv("../inp/gear_tiers.csv")

gear_type = [
    ['Type',0,'weapon'],
    ['Type',1,'helm'],
    ['Type',2,'armor'],
    ['Type',3,'necklace'],
    ['Type',4,'ring'],
    ['Type',5,'boots']
    ]
gear_set = [
    ['Set',0,'Speed',25,'SPD',4],
    ['Set',1,'Hit',20,'EFF',2],
    ['Set',2,'Critical',12,'CRIT',2],
    ['Set',3,'Defense',15,'DEF',2],
    ['Set',4,'Health',15,'HP',2],
    ['Set',5,'Attack',35,'ATK',4],
    ['Set',6,'Counter',20,'NA',4],
    ['Set',7,'Lifesteal',0,'NA',4],
    ['Set',8,'Destruction',40,'CDMG',4],
    ['Set',9,'Resist',20,'RES',2],
    ['Set',10,'Rage',30,'NA',4],
    ['Set',11,'Immunity',0,'NA',2],
    ['Set',12,'Unity',4,'NA',2],
    ['Set',13,'Revenge',0,'NA',4],
    ['Set',14,'Injury',0,'NA',4],
    ['Set',15,'Penetration',0,'NA',2]
    ]
type_df = pd.DataFrame(data = gear_type, columns = ['Ind','Type','Type_Nm'])
set_df = pd.DataFrame(data = gear_set, columns = ['Ind','Set','Set_Nm','Bonus','Bonus_Stat','Set_Lg'])
set_4 = set_df[['Set','Set_Nm','Set_Lg']][set_df.Set_Lg == 4]
set_A = set_df[['Set','Set_Nm','Set_Lg']]
set_2 = set_df[['Set','Set_Nm','Set_Lg']][set_df.Set_Lg == 2]

gear_scaling = {0: 1, 1: 1.2, 2: 1.4, 3: 1.6, 4: 1.8, 5: 2.0, 6: 2.2, \
                7: 2.4, 8: 2.6, 9: 2.8, 10: 3.0, 11: 3.3, 12: 3.6, 13: 3.9, 14: 4.25, 15: 5.0}

subs_cols = ['subStat1','subStat2','subStat3','subStat4']

r_map = {'Epic':0,'Heroic':1,'Rare':2}
t_map = {'Weapon':0,'Helmet':1,'Armor':2,'Necklace':3,'Ring':4,'Boots':5}

s_map = {}
for i in range(0,11):
    a = grl['stat'][i]
    b = grl['stat_in'][i]
    s_map[b] = a

# ### FUNCTIONS
def hero_json_to_df(chars, data):
    df = pd.DataFrame( chars , columns = ['Name'] )
    df2 = pd.DataFrame(data['heroes'])
    df = pd.merge(df,df2[['Name','Lvl','BonusStats']],how='left',on=['Name'])
    df['Lvl'] = df['Lvl'].fillna(50)
    df['Lvl'] = df['Lvl'].clip(lower=50)
    char_df = pd.read_csv('../inp/character_data.csv')
    df = df.merge(char_df, how='left', left_on = ['Name','Lvl'], right_on = ['Character','Level'])
    return df

def hero_json_to_df_v2(data):
    df = pd.DataFrame(data['heroes'])
    for j in range (0,6):
        gear = []
        for i in df.index:
            if df['Gear'][i]:
                if df['Gear'][i][j]:
                    dc = df['Gear'][i][j]
                    gear.append(dc["ID"])
                else: gear.append(None)
            else: gear.append(None)
        col_name = ('gear_id_'+str(j))
        df[col_name] = gear
    df['Lvl'] = df['Lvl'].clip(lower=50)
    char_df = pd.read_csv('../inp/character_data.csv')
    df = df.merge(char_df, how='left', left_on = ['Name','Lvl'], right_on = ['Character','Level'])
    return df

def item_json_to_df(data):
    df = pd.DataFrame(data['items'])
    df.rename(columns={'ability':'enhance'}, inplace=True) ##added this line for anyone using compeanansi OCR tool
    df[subs_cols] = df[subs_cols].applymap(lambda x: [0,0] if x is np.nan else x)
    #df = df.apply(lambda row: ocr_cleanup(row), axis=1)
    df['grade'] = df['rarity'].map(r_map)
    df['Type'] = df['slot'].map(t_map)
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
    df['current_eff'] = GR * 6.6 + main_rating * gear_scaling[enhance]/5 * 4.4
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
    if st.USE_CURR_EQUIP == 1:
        temp_slots = temp_df[(temp_df.hero == hero_name)].Type.values
        temp_df = temp_df[(~temp_df.Type.isin(temp_slots)) | (temp_df.hero == hero_name)]
        temp_df = temp_df.groupby('slot').head(st.GEAR_LIMIT).reset_index(drop=True)
    if st.USE_CURR_EQUIP == 0:
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
    y = np.where( (st.GEAR_12 == 1) & (x < 12) , 3.3/x.map(gear_scaling) , 1 )
    return y

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
            mainst_df[stat] += np.where( mainst_df[col1].map(s_map) == stat, (mainst_df[col2] * enh_mult).astype(int), 0)
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
