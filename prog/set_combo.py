# #### SET UP

import pandas as pd
import numpy as np
import itertools
import pickle
import yaml
import setup as st
import fx_lib as fx

df_items = pd.read_pickle('../outp/equip_potential.pkl')
df_items['reco'] = ''
df_items['start_loc'] = df_items['hero']

def startup_message(lock_gear):
    df_items['reco'] = np.where( df_items['hero'].isin(lock_gear) , df_items['hero'], df_items['reco'] )
    if st.NO_EQUIPPED_GEAR == 1: print("Unequipped gear will be used. # of items: ", len(df_items[(df_items.hero == np.nan) | (df_items.hero == '')]) )
    elif len(lock_gear) > 0:  print("Unequipped and unlocked gear will be used.  # of items", len(df_items[df_items.reco == '']) )
    else:  print("All gear will be used.  # of items:", len(df_items) )
    return

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
    include_sets = fx.gen_input_sets(input_sets, exclude_sets)
    print("Sets to include for this character:", include_sets)
    target_stats[build]['include_sets'] = include_sets.tolist()
    if any(item in include_sets for item in fx.set_4.Set_Nm.values) == True:
        FORCE_4SET = 1
        print("Looking for combinations using a four piece set only.")
        print("To include combinations of three 2 gear sets, set FORCE_4SET = 0")
    else:
        FORCE_4SET = 0
        print("Accepts all set combinations (4set+2set or 3x2set)")
    return FORCE_4SET, char, target_stats[build]

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
    #print(zz , "== 15")
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
    #print(zz, "== 90")
    return l2_comb

# ### GET COMBINATIONS OF EACH SET
L = [0,1,2,3,4,5]
l4 = [",".join(map(str, comb)) for comb in itertools.combinations(L, 4)]
l2 = [",".join(map(str, comb)) for comb in itertools.combinations(L, 2)]

l4_comb = l4comb(l4,l2)
l2_comb = l2comb(l2)

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
###end function
