#### These are functions used in Jupyter notebook to enhance display and remove clutter
from ipywidgets import interact, widgets, interactive, VBox, HBox
import fx_lib as fx
import pandas as pd
import numpy as np
import json

def set_widget4(Force_4Set, Speed, Attack, Counter, Lifesteal, Destruction, Rage, Revenge, Injury ):
    return

def set_widget2(Hit, Critical, Defense, Health, Resist, Immunity, Unity, Penetration ):
    return

def weight_widget(spd,atk,crit,cdmg,hp,defense,eff,res,ehp,dmg):
    return

def run_widgets(hero_target,Force_4Set, char_list, st_setting, char):
    widgets.IntSlider(min=-1,max=3,value=1)
    w = interactive(weight_widget,
                    spd = hero_target['SPD']['Weight'], atk = hero_target['ATK']['Weight'],
                    crit = hero_target['CRIT']['Weight'], cdmg = hero_target['CDMG']['Weight'],
                    hp = hero_target['HP']['Weight'], defense = hero_target['DEF']['Weight'],
                    eff = hero_target['EFF']['Weight'], res = hero_target['RES']['Weight'],
                    ehp = hero_target['EHP']['Weight'], dmg = hero_target['Dmg_Rating']['Weight'])
    s4 = interactive(set_widget4,  Force_4Set = Force_4Set==1, Speed = 'Speed' in hero_target['include_sets'], Attack = 'Attack' in hero_target['include_sets'], Counter = 'Counter' in hero_target['include_sets'],  Lifesteal = 'Lifesteal' in hero_target['include_sets'],
                     Destruction = 'Destruction' in hero_target['include_sets'], Rage = 'Rage' in hero_target['include_sets'], Revenge = 'Revenge' in hero_target['include_sets'], Injury = 'Injury' in hero_target['include_sets'])
    s2 = interactive(set_widget2, Hit = 'Hit' in hero_target['include_sets'], Critical = 'Critical' in hero_target['include_sets'], Defense = 'Defense' in hero_target['include_sets'], Health = 'Health' in hero_target['include_sets'],
                     Resist = 'Resist' in hero_target['include_sets'], Immunity = 'Immunity' in hero_target['include_sets'], Unity = 'Unity' in hero_target['include_sets'], Penetration = 'Penetration' in hero_target['include_sets'])
    w1 = widgets.Dropdown(options=char_list,value=char,description="Character")
    w2 = widgets.IntSlider(value= st_setting[0], min=0, max=15, step=1, description='GEAR_ENHANCE:',
        disabled=False, continuous_update=False, orientation='horizontal', readout=True, readout_format='d')
    w3 = widgets.IntSlider(value= st_setting[1], min=0, max=30, step=1, description='GEAR_LIMIT:',
        disabled=False, continuous_update=False, orientation='horizontal', readout=True, readout_format='d')
    w4 = widgets.Checkbox(value= st_setting[2] ==1 , description="Keep gear currently equipped:")
    return w,s4,s2,w1,w2,w3,w4

def update_settings(w0, s4, s2, hero_target):
    include_sets = []
    for i in fx.set_4.Set_Nm.values:
        if s4.kwargs[i]: include_sets.extend([str(i)])
    for i in fx.set_2.Set_Nm.values:
        if s2.kwargs[i]: include_sets.extend([str(i)])
    hero_target['include_sets'] = include_sets
    weight = w0.kwargs
    for i in weight:
        j = i.upper()
        if j == 'DEFENSE': j = 'DEF'
        elif j == 'DMG': j = 'Dmg_Rating'
        hero_target[j]['Weight'] = weight[i]
    return hero_target

def stat_range():
    spd_range = widgets.IntRangeSlider(
        value=[80, 350], min=80, max=350, step=1,
        description='Speed:', disabled=False, continuous_update=False, orientation='horizontal',readout=True, readout_format='d')
    atk_range = widgets.IntRangeSlider(
        value=[0, 9999], min=0, max=9999, step=1,
        description='Attack:', disabled=False, continuous_update=False, orientation='horizontal',readout=True, readout_format='d')
    crit_range = widgets.IntRangeSlider(
        value=[0, 101], min=0, max=101, step=1,
        description='Crit Chance:', disabled=False, continuous_update=False, orientation='horizontal',readout=True, readout_format='d')
    cdmg_range = widgets.IntRangeSlider(
        value=[150, 500], min=150, max=500, step=1,
        description='Crit Dmg:', disabled=False, continuous_update=False, orientation='horizontal',readout=True, readout_format='d')
    hp_range = widgets.IntRangeSlider(
        value=[0, 35000], min=3000, max=35000, step=1,
        description='HP:', disabled=False, continuous_update=False, orientation='horizontal',readout=True, readout_format='d')
    def_range = widgets.IntRangeSlider(
        value=[0, 3500], min=300, max=3500, step=1,
        description='Defense:', disabled=False, continuous_update=False, orientation='horizontal',readout=True, readout_format='d')
    eff_range = widgets.IntRangeSlider(
        value=[0, 350], min=0, max=350, step=1,
        description='Effectiveness:', disabled=False, continuous_update=False, orientation='horizontal',readout=True, readout_format='d')
    res_range = widgets.IntRangeSlider(
        value=[0, 350], min=0, max=350, step=1,
        description='Resistance:', disabled=False, continuous_update=False, orientation='horizontal',readout=True, readout_format='d')
    s1 = [spd_range,atk_range,crit_range,cdmg_range,hp_range,def_range,eff_range,res_range]
    return [spd_range,atk_range,crit_range,cdmg_range,hp_range,def_range,eff_range,res_range]

def print_gear_options(odf,s1,s2,w3):
    active_sets = []
    for i in range(1,len(s2)):
        if s2[i].value: active_sets.append(s2[i].description)
    op_cols = ['Complete','Set_1','Set_2','Set_3','WW','ATK','HP','DEF','SPD','CRIT','CDMG','EFF','RES', 'Dmg_Rating','EHP','CP']
    print_df = odf[op_cols][ (odf.SPD >= s1[1].value[0])&(odf.SPD <= s1[1].value[1]) &
                 (odf.ATK >= s1[2].value[0])&(odf.ATK <= s1[2].value[1]) &
                 (odf.CRIT >= s1[3].value[0])&(odf.CRIT <= s1[3].value[1]) &
                 (odf.CDMG >= s1[4].value[0])&(odf.CDMG <= s1[4].value[1]) &
                 (odf.HP >= s1[5].value[0])&(odf.HP <= s1[5].value[1]) &
                 (odf.DEF >= s1[6].value[0])&(odf.DEF <= s1[6].value[1]) &
                 (odf.EFF >= s1[7].value[0])&(odf.EFF <= s1[7].value[1]) &
                 (odf.RES >= s1[8].value[0])&(odf.RES <= s1[8].value[1]) &
                 (odf.Set_1.isin(active_sets)) & (odf.Set_2.isin(active_sets)) &
                 (odf.Set_3.isin(active_sets) | odf.Set_3.isna() ) &
                 ~(odf.Complete.isin(['PREVIOUS','CURRENT']))
                ].sort_values([w3.value],ascending=False).head(20).copy()
    return print_df

def run_stat_selector(uniqueSets):
    w1 = stat_range()
    s1 = [widgets.Label("Stat Range")]
    for i in range(0,len(w1)):
        s1.append(w1[i])
    s2 = [widgets.Label("Sets:")]
    for x in range(len(uniqueSets)):
        var = widgets.Checkbox( value=True, description= str(uniqueSets[x]), disabled=False)
        s2.append(var)
    sort_cols = ['WW','ATK','HP','DEF','SPD','CRIT','CDMG','EFF','RES','Dmg_Rating','EHP','CP']
    w3 = widgets.RadioButtons(options= sort_cols, value='WW', description='Sort:', disabled=False)
    return s1,s2,w3

def save_hero(df, gear_selected, char):
    reco_list = gear_selected['gear_list']
    df['reco'][(df.reco == char)] = ''
    df['reco'] = np.where( df.id.isin(reco_list) , char, df['reco'])
    df['hero'] = np.where((df.hero == char)&(df.hero != df.reco),'',df.hero)
    df = df.sort_values(by = ['hero','reco','Type','efficiency','enhance'])
    df.to_pickle('../outp/upd_items.pkl')
    return df

def save_final_data(df):
    df[~(df.reco=='')][['start_loc','hero','efficiency','rating','reco','Type','slot','set','level','rarity','enhance','mainStat','subStat1','subStat2','subStat3','subStat4']].to_csv('../reco/gear_reco.csv')
    df['hero'] = np.where( df.reco!='', df['reco'], df['hero'])
    df.to_pickle('../outp/equip_potential.pkl')
    df = df.sort_values(by = ['hero','Type','efficiency','enhance'])
    export2 = df[['efficiency','hero','enhance','slot','level','set','rarity','mainStat','subStat1','subStat2','subStat3','subStat4','id','p_id','locked']].to_dict('records')
    with open('../outp/upd_items.json', 'w') as fp: json.dump(export2, fp)
    return
