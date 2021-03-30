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
with open('../inp/master_data.json') as json_file:
    data = json.load(json_file)

# #### ITEMS
df_items = fx.item_json_to_df(data)
df_items = fx.gear_stats(df_items)
df_items['error_check'] = df_items.apply(lambda row: fx.verify_item_input(row), axis=1)
err_ids = df_items[df_items.error_check > 0]['id'].copy()
print("Hey, we noticed some of your gear had abnormal values, so we think you should take a quick look. ")
print("There are", err_ids.count(),"items we picked up in QA: ", err_ids.values )
print("Note: Epic Seven does not use consistent main stat or sub stat values based on gear level, so this alert may produce false positives with event gear or lvl90 gear")

# ##### Gear potential
df_items = df_items.apply(lambda row: fx.item_potential(row), axis=1)

df_items = df_items.sort_values(by = ['hero','Type','efficiency','enhance'])
df_items.to_csv('../outp/equip_potential.csv')
df_items.to_pickle('../outp/equip_potential.pkl')
export2 = df_items[fx.outp_cols].to_dict('records')
with open('../outp/equip_potential.json', 'w') as fp: json.dump(export2, fp)
