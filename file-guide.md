---
layout: default
title: File Guide
nav_order: 5
---

## File Guide

<b>Part 1:  Key Files </b>
<br> Also see [Configuration](input_file_setup.html)
<br>
| File | Folder | Description |
|:------- |:-------:|:------- |
| master_data.json | inp | File that must contains list of "items" and "heroes" as inputs for optimization.  This file must contain all equipments within the "items" section to use in optimization. |
| Hero_Optimization_Notebook.ipynb | prog | Jupyter notebook for running the hero optimization |
| Other_Useful_Features.ipynb | prog | Jupyter notebook for running other scripts (such as viewing hero stats) |
| setup.py | prog | File with global variables used for running the optimization.  These variables can be adjusted in the Jupyter notebook. |
| item_potential.py | prog | Runs directly from `Hero_Optimization_Notebook.ipynb` or run in CLI.  Running this file overwrites any saved data with the lastest version of `master_data.json`.  If you're using the notebook, skip this cell if you haven't updated the `master_data.json` since your last run |
| run_hero_opt.py | prog | CLI file to run simplified version of hero optimization (instead of using notebook) |
| character_inputs.yaml | inp | Optional file to save and preload hero settings to improve/customize optimization results |
| character_data.csv | inp | This contains the base hero stats for level 50 and 60 fully awakened heroes.  This file must contain the hero (with the same spelling) in order to run the optimization. |
| gear_tiers.csv | inp | Contains hard-coded data on equipment stats based on level |
| Other `prog/*.py` files | prog | These are the background files to run the program |

<br><b>Part 2:  Outputs </b>
<br>
| File | Folder | Description |
| ----------- | ----------- | ----------- |
| upd_items.json | outp | Saved data from optimization runs.  Outputs the updated version of `master_data['items']`.  Recommend copying this data to replace the items in `master_data.json` once you've regeared your heroes. |
| gear_reco.csv | reco | Outputs the gear/heroes that have changed in the optimization runs |
| equip_potential.csv | outp | Output from running `item_potential.py` that saved gear into `.csv` and provides efficiency ratings |
| equip_potential.pkl | outp | Input file for items in optimization.  Pickle file format output of `item_potential.py` & gets overwritten when each hero completes via `Hero_Optimization_Notebook.ipynb` or `run_hero_opt.py`. |
| upd_items.pkl | outp | Additional backup file saved from hero optimization. If you ever overwrite `equip_potential.pkl` by accident via `item_potential.py`, this is your data! |
