import requests
import json
import pandas as pd
import numpy as np

hero_status_dict = {
    'lv50FiveStarFullyAwakened': 50,
    'lv60SixStarFullyAwakened': 60
}

def api_get_status(get_data):
    if get_data.status_code != 200: print("Error", get_data.status_code)
    return

def get_e7_hero_data(hero_name):
    hero_call = requests.get('https://api.epicsevendb.com/hero/'+str(hero_name))
    return hero_call.json()['results'][0]

response_hero_list = requests.get('https://api.epicsevendb.com/hero/')
api_get_status(response_hero_list)

hero_stat_list = []
for i in range(0,len(response_hero_list.json()['results'])):
    try:
        hero_name = response_hero_list.json()['results'][i]['_id']
        hero_data = get_e7_hero_data(hero_name)
        for status in hero_status_dict.keys():
            new_dict = hero_data['calculatedStatus'][status]
            new_dict['hero_id'] = hero_name
            new_dict['name'] = response_hero_list.json()['results'][i]['name']
            new_dict['level'] = hero_status_dict[status]
            new_dict['attribute'] = response_hero_list.json()['results'][i]['attribute']
            new_dict['role'] = response_hero_list.json()['results'][i]['role']
            new_dict['sc'] = 1 if len(hero_data['specialty_change']) > 0 else 0
            new_dict['ee'] = 1 if len(hero_data['ex_equip']) > 0 else 0
            new_dict['ee_stat'] = hero_data['ex_equip'][0]['stat']['type'] if len(hero_data['ex_equip']) > 0 else ''
            hero_stat_list.append(new_dict)
    except:
        pass
#end for loop
df = pd.DataFrame(hero_stat_list)
df['role'] = df['role'].replace(['manauser','assassin'],['soul-weaver','thief'])
df['hp_flat'] = np.where(df['hp'] < 4100, 1, 0)
df['atk_flat'] = np.where(df['atk'] < 790, 1, 0)
df['def_flat'] = np.where(df['def'] < 475, 1, 0)
print("There were", len(df['name'].unique()), "heroes pulled")

df.to_csv('../inp/character_data.csv')
