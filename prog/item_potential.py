# #### SET UP

import pandas as pd
import numpy as np
import itertools
import json
import pickle
import yaml
import setup as st
import fx_lib as fx

# #### DATA IMPORT
with open('../inp/lellian_master.json') as json_file:
    data = json.load(json_file)

# ##### HEROES
#df_hero = fx.hero_json_to_df(data)

# #### ITEMS
df_items = fx.item_json_to_df(data)
df_items = fx.gear_stats(df_items)

# ##### Gear potential
df_items = df_items.apply(lambda row: fx.item_potential(row), axis=1)

df_items = df_items.sort_values(by = ['hero','Type','efficiency','enhance'])
df_items.to_csv('../outp/equip_potential.csv')
df_items.to_pickle('../outp/equip_potential.pkl')
export2 = df_items[['efficiency','hero','enhance','slot','level','set','rarity','mainStat','subStat1','subStat2','subStat3','subStat4','id','p_id','locked']].to_dict('records')
with open('../outp/equip_potential.json', 'w') as fp: json.dump(export2, fp)
