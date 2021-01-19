## Jupyter Notebook Walkthrough
### Using the optimization notebook
<br> First off, in order to make the most of the Jupyter notebook, there are a few things you should do before you even open or run the notebook.
<br> MUST DO:
<br> 1. You need to add your items into the `master_data.json`
<br> OPTIONAL:
<br> 3. Add your heroes into `master_data.json`.  You don't have to do this step, in fact, I don't add all my heroes.  I do add the ones with exclusive equipment or specialty change.  This is because you can use the `"BonusStats"` key to add in stats from exclusive equipment, fixed stat specialty change runes, or artifacts.  The sample file includes a few SC and EE heroes in there already.
<br> 4. If you know the heroes you'd like to optimize, or heroes that you don't want touched, you can add them in an ordered list to `character_inputs.yaml`; but you can do this directly in the notebook as well (see below).

#### Using the notebook
So, you've downloaded the source code, you have Jupyter installed, and you've got your gear input.  You're ready to open `Hero_Optimization_Notebook`.
<br><br><b>Step 1:</b>  <br>Run each of the cells to initialize the notebook.
<br><img alt="Initial cells" src="https://github.com/ja-bru/E7_Py_Gear_Selector/blob/gh-pages/_image/1_initialize_notebook.png?raw=true">
<br>In the notebook there is a description of the settings and you can uncomment and edit any of the settings before proceeding.  To uncomment cells, remove the leading _#s_.
<br><img alt="Settings" src="https://github.com/ja-bru/E7_Py_Gear_Selector/blob/gh-pages/_image/2_setup_fields.png?raw=true">
If you do not edit any of these fields, it will take the default values from the `setup.py` file.
<br>
<br><b>Step 2:</b>  <br>Keep running the cells until you reach the image below.  Here you can uncomment and specify a list of heroes.
> hero_order:  if you put the heroes in order you want to optimize them, and stick to that order, you won't need to manually select a hero each time in Step 3.
> lock_gear:  When you have the setting `st.NO_EQUIPPED_GEAR` = 0 (you can use equipped gear in the optimization), you will want to specify any heres to lock.  By locking heroes, you can't steal any gear from them unless you've already replaced the gear through optimization.  Gear equipped in the same optimization session gets locked automatically.

<br><img alt="Hero Startup" src="https://github.com/ja-bru/E7_Py_Gear_Selector/blob/gh-pages/_image/3_optional_specify_heroes.png?raw=true">
<br>
<br><b>Step 3:</b>  <br>Hero selection.  You can update the hero using the dropdown menu if you're choosing to stray from the `hero_order` field.
<br> You have the option of choosing to keep any currently equipped gear on your hero (ie, you might use this for a hero that has a few equipped pieces but you don't want to make many changes to)
<br> You can also adjust the enhancement level of the gear (main stats get boosted, but never lowered).  By selecting 15, it applies the maximum main stats during gear selection, but substats are not adjusted at all.
<br><img alt="Choose Hero" src="https://github.com/ja-bru/E7_Py_Gear_Selector/blob/gh-pages/_image/choosing_hero.png?raw=true">
<br> Next, you can choose the sets you want to run through optimization.  At this time, broken sets are not calculated.
<br> You can weight stats to help select gear with the desired stats.  Weighting is used for the field `WW` described [here](stat-guide.md)
<br><img alt="Choose Sets/Subs" src="https://github.com/ja-bru/E7_Py_Gear_Selector/blob/gh-pages/_image/choosing_sets_stats.png?raw=true">
<br>
<br><b>Step 4:</b>
<br> Run all the cells until you get to Section 4 in the notebook.  At the beginning of Section 4, some automated gear combinations will be displayed, and you can get a sense of what's available.  You can use the next cell (see below) to filter the outputs in the `print_df` cell output.
<br><img alt="Filter Output" src="https://github.com/ja-bru/E7_Py_Gear_Selector/blob/gh-pages/_image/filter_outputs.png?raw=true">
<br> As you can play through the outputs, take note of the index number (the first number in each row), as you'll use that row index to select the desired output.
<br>
<br><b>Step 5:</b>
<br> Select your gear by putting the row_index into the field the pops up.  The next cell confirms the value.  If that value is correctly displayed, follow the remaining instructions in the notebook to save your output and go run your next hero.
<br>
<br> Hope this guide was helpful and thanks for using the Gear Selector.
