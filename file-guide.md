---
layout: default
title: File Guide
nav_order: 5
---

## File Guide

<b>Part 1:  Key Files </b>
<br> Also see [Configuration](input_file_setup.html)
<br>
<table>
<tr><th> File </th><th> Folder </th><th> Description </th></tr>
<tr><td> master_data.json </td><td> inp </td><td> File that must contains list of "items" and "heroes" as inputs for optimization.  This file must contain all equipments within the "items" section to use in optimization. </td></tr>
<tr><td> Hero_Optimization_Notebook.ipynb </td><td> prog </td><td> Jupyter notebook for running the hero optimization </td></tr>
<tr><td> Other_Useful_Features.ipynb </td><td> prog </td><td> Jupyter notebook for running other scripts (such as viewing hero stats) </td></tr>
<tr><td> setup.py </td><td> prog </td><td> File with global variables used for running the optimization.  These variables can be adjusted in the Jupyter notebook. </td></tr>
<tr><td> item_potential.py </td><td> prog </td><td> Runs directly from <code>Hero_Optimization_Notebook.ipynb</code> or run in CLI.  Running this file overwrites any saved data with the lastest version of <code>master_data.json</code>.  If you're using the notebook, skip this cell if you haven't updated the <code>master_data.json</code> since your last run </td></tr>
<tr><td> run_hero_opt.py </td><td> prog </td><td> CLI file to run simplified version of hero optimization (instead of using notebook) </td></tr>
<tr><td> character_inputs.yaml </td><td> inp </td><td> Optional file to save and preload hero settings to improve/customize optimization results </td></tr>
<tr><td> character_data.csv </td><td> inp </td><td> This contains the base hero stats for level 50 and 60 fully awakened heroes.  This file must contain the hero (with the same spelling) in order to run the optimization. </td></tr>
<tr><td> gear_tiers.csv </td><td> inp </td><td> Contains hard-coded data on equipment stats based on level </td></tr>
  <tr><td> Other <code>prog/*.py</code> files </td><td> prog </td><td> These are the background files to run the program </td></tr>
</table>

<br><b>Part 2:  Outputs </b>
<br>
<table>
<tr><th> File </th><th> Folder </th><th> Description </th></tr>
<tr><td> upd_items.json </td><td> outp </td><td> Saved data from optimization runs.  Outputs the updated version of <code>master_data['items']</code>.  Recommend copying this data to replace the items in <code>master_data.json</code> once you've regeared your heroes. </td></tr>
<tr><td> gear_reco.csv </td><td> outp </td><td> Outputs the gear/heroes that have changed in the optimization runs </td></tr>
  <tr><td> equip_potential.csv </td><td> outp </td><td> Output from running <code>item_potential.py</code> that saved gear into <code>.csv</code> and provides efficiency ratings </td></tr>
<tr><td> equip_potential.pkl </td><td> outp </td><td> Input file for items in optimization.  Pickle file format output of `item_potential.py` & gets overwritten when each hero completes via <code>Hero_Optimization_Notebook.ipynb</code> or <code>run_hero_opt.py</code>. </td></tr>
<tr><td> upd_items.pkl </td><td> outp </td><td> Additional backup file saved from hero optimization. If you ever overwrite <code>equip_potential.pkl</code> by accident via <code>item_potential.py</code>, this is your data! </td></tr>
 </table>
