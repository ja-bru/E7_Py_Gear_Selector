
import pandas as pd
import numpy as np
import pickle
import yaml
import setup as st

df_items = pd.read_pickle('../outp/equip_potential.pkl')

x1 = df_items['efficiency'].quantile(q=0.4)
x2 = df_items['max_eff'].quantile(q=0.3)
x3 = df_items['rating'].quantile(q=0.4)
x4 = df_items['current_eff'].quantile(q=0.3)

print("number of items" , len(df_items))
print("number of unequipped items" , len(df_items[df_items.hero=='']))

low_items = df_items[(df_items.efficiency <= x1) & (df_items.max_eff <= x2) & (df_items.rating <= x3) & (df_items.current_eff <= x4) & (df_items.SPD <= 8)].copy()

print("number of items to delete" , len(low_items))
print("number of unequipped items to delete" , len(low_items[low_items.hero=='']))

low_items[low_items.hero==''].id.to_csv('../outp/remove_list.csv')
