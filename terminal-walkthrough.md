---
layout: default
title: CLI-Walkthrough
nav_order: 4
---
## CLI Walkthrough
### How to use the optimizer in terminal

### Overview

Using terminal is an option if you want to batch a few heroes at once, particularly on automated selection.  I wouldn't recommend using automated selection unless you've used the notebook manually and are able to get the right configurations for your hero.  When using the notebook, the 'auto-selected' gear option will actually appear as the default value for index selection; feel free to compare that gear to what you actually choose.

You can use CLI manually, but aside from actually making the final selection for gear from a recommended list of options, it has less flexibility and no intermediate selection options built into the program flow.

If you're using CLI, I am assumnig you're familiar enough to navigate folders and run shells scripts or python commands.

### File Set Up

Ensure you've updated each of the following files:
1. `prog/setup.py`
2. `inp/character_inputs.yaml`

### Optimization through CLI

From the `*/prog` folder, you'll need to run two files. 
1. Run `python item_potential.py` to analyze the gear in `master_data.json`.  Once you've done this once, you don't need to do it again unless you want to overwrite the file with whatever updates you've made to `master_data.json` 
2. Run `python hero_opt.py`.  Double check your `setup.py` file before running!

If you have manual selection turned off, you don't need to do anything.  Wait a few seconds to make sure your first hero is running and then it's on autopilot.  Status messages and updates will show on the screen as your heroes run, but it's going in full auto mode so come back later to review your outputs.

As the script starts running, you will see messages similar to this:
<insert image>

Once the optimizer finishes, you will see a refined list of gear options and a prompt to enter the index for the gear stats you prefer:
<insert image>

How is the list of gear sets created?
1.  If you entered priority stats, it shows you a couple sets that give the best overall stat boost to your hero based on the weightings you assigned (highest WW values) and the top priority stats.  For example, if your hero has 'Speed' as a priority stat in the `character_input.yaml` you will see the combinations that produce the highest speed.
2.  After applying the min/max target stats (if any combinations meet that criteria), you will again get the top combinations based on WW & Priority Stats within the min/max stat ranges.
3.  A filtered list that looks for combinations with high performance in each of the Priority Stats combined will be displayed.

The list is typically anywhere from 3 - 20 options depending on the variations for your hero.

You'll quickly see the chosen final stats with a message letting you know the hero is finished before looping back to the next hero.

Once all your heroes are completed, you can visit either `outp/upd_items.json` or `reco/gear_reco.csv`.


