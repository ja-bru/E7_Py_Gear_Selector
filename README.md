# Equipment Selection and Hero Optimization for Epic Seven 
## using Python / Jupyter Notebook

### About

This program supports hero/equipment optimization for the mobile game Epic Seven.  I built this program as a way to help sort through equipment and quickly regear heroes during free unequipment events.  Managing equipment and gearing heroes in game can be tedious and I hope you can use this, or other tools available to improve your gameplay.

This tool is built using Python and is not attached to a user interface.  The program can be run either in command line or in the provided Jupyter notebook.

The tool takes in a `.json` file with gear and hero data.  A sample file is included which shows data formatting and works with [Compeanansi's OCR Tool](https://github.com/compeanansi/epic7) or json output from [Zarroc's Gear Optimizer](https://github.com/Zarroc2762/E7-Gear-Optimizer).

### How to use

A detailed how-to is in progress. Here is a guide for [hero optimization via jupyter notebook](https://ja-bru.github.io/E7_Py_Gear_Selector/jupyter-walkthrough.html).  

##### Requirements
- Python 2.7 or higher
- Jupyter Notebook
  - Download and install the 64 bit Anaconda python 3.x distribution for Windows: https://www.anaconda.com/products/individual
- Screenshots of your gear or ready-formatted gear list

##### Quickstart
- Ensure your gear is copied into the `master_data.json` file
- Open the Jupyer Notebook `.ipynb` and follow the instructions

### Features
- Hero optimization
- Can be set to run automatically for several heroes at a time _using command line only_
- Select gear sets to include or exclude
- Able to use unequipped gear, unlocked gear, or all gear 
- Set minimum enhance level to use for optimization (default 12)
- Weight specific stats to prioritize gear selection and substats
- Force final hero stats
- Add in stat bonuses from Exclusive Equipment, Memory Imprint, Artifacts, Specialty Change

#### Restrictions
- Only outputs complete sets
- No feature to select main stat for Necklace/Ring/Boots
- Customizability requires more upfront effort tinkering with settings
- CP calculation does not include Skill Enhance or Artifact [CP calculation explained](https://www.reddit.com/r/EpicSeven/comments/dvdfqp/guide_combat_power_calculation/)
- Assumes max awakened hero at level 50 or 60
- Not yet connected to epic seven api for character data
