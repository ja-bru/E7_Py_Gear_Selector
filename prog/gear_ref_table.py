# #### SET UP

import pandas as pd
import numpy as np
import itertools
import setup as st
from datetime import datetime

# GEAR REFERENCE TABLES
d = [
    ['ATK%', 'AtkP',   0, 0,    0.13,  0.09,  0.05,  0.11111,  0.08,  0.07,  0.06],
    ['DEF%', 'DefP',  7, 1,     0.13,  0.09,  0.05,  0.11111,  0.08,  0.07,  0.06],
    ['HP%',  'HPP',  5, 2,      0.13,  0.09,  0.05,  0.11111,  0.08,  0.07,  0.06],
    ['SPD',  'Spd',  2, 3,         9,  5,  2,  0.2,  4,  4,  3],
    ['CRIT', 'CChance',  3, 4,  0.12,  0.06,  0.04,  0.166667,  0.05,  0.04,  0.04],
    ['CDMG', 'CDmg',  4, 5,     0.14,  0.08,  0.04,  0.125,  0.07,  0.06,  0.05],
    ['EFF',  'Eff',  9, 6,      0.13,  0.09,  0.05,  0.11111,  0.08,  0.07,  0.06],
    ['RES',  'Res',  10, 7,     0.13,  0.09,  0.05,  0.11111,  0.08,  0.07,  0.06],
    ['ATK',  'Atk',  1, 8,       103,  55,  30,  0.02222,  46,  40,  35], ##assumes the maximum flat attack sub for lvl 85 gear is 55
    ['DEF',  'Def',  8, 9,        62,  44,  24,  0.025,  38,  33,  30],  ##assumes the maximum flat defense sub for lvl 85 gear is 44
    ['HP',   'HP',  6, 10,       540,  240,  140,  0.005556,  205,  180,  160] ##assumes the maximum flat hp sub for lvl 85 gear is 240
]
cols = ['stat', 'stat_in','code','order','main_t7','max_t7','min_t7','multiplier','max_t6','max_t5','max_t4']
gear_rating_lookup = pd.DataFrame(data = d, columns = cols)
gear_rating_lookup.sort_values(by = ['order'], inplace=True)
gear_rating_lookup.reset_index(inplace=True)
grl = gear_rating_lookup.to_dict()

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

r_map = {'Epic':0,'Heroic':1,'Rare':2}
t_map = {'Weapon':0,'Helmet':1,'Armor':2,'Necklace':3,'Ring':4,'Boots':5}
s_map = {}
for i in range(0,11):
    a = grl['stat'][i]
    b = grl['stat_in'][i]
    s_map[b] = a

gear_scaling = {0: 1, 1: 1.2, 2: 1.4, 3: 1.6, 4: 1.8, 5: 2.0, 6: 2.2, \
                7: 2.4, 8: 2.6, 9: 2.8, 10: 3.0, 11: 3.3, 12: 3.6, 13: 3.9, 14: 4.25, 15: 5.0}

e7api_map = {
    'cp': 'cp', 'atk': 'atk', 'hp': 'hp', 'spd': 'spd', 'def': 'def',
    'crit': 'chc', 'cdmg': 'chd', 'eff': 'eff', 'res': 'efr',
    'sc': 'sc', 'ee': 'ee',
    'level': 'level', 'role': 'role', 'element': 'attribute',
    'hero': 'name'
}
