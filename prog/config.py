## CONFIGURATION
## These settings determine how the program runs.
## For structured access, see e7_gear.settings.Settings.

## RUN SETTINGS
MANUAL_SELECTION = 1    ## {1: prompt user to select gear; 0: fully automated}
GEAR_LIMIT = 5          ## Top-N gear per slot used in optimization (impacts run time)
AUTO_ADJ_GEAR_LIMIT = 1 ## Reduce GEAR_LIMIT when estimated combinations exceed COMBO_COUNT_LIMIT
COMBO_COUNT_LIMIT = 1_000_000  ## Target ceiling for gear combination count per hero

## GEAR SELECTION
USE_BROKEN_SETS = 0     ## Only complete sets are supported at this time
NO_EQUIPPED_GEAR = 1    ## {1: unequipped gear only; 0: may use unlocked equipped gear}
KEEP_CURR_GEAR = 0      ## Keep gear currently equipped on the hero being optimized

## HERO CRITERIA
MIN_LEVEL = 50          ## Default hero level (50 or 60) for stat calculation
## STAT SELECTION
GEAR_ENHANCE = 12       ## Minimum enhance level assumed for stat optimization
FLAT_SUB = 0.8          ## Weight flat substat values {0.0-1.0, default: 0.8}
FLAT_MAIN = 0.5         ## Weight flat main stats on Neck/Ring/Boots {0.0-1.0, default: 0.5}
IGNORE_FLAT_MAIN_STATS = 0  ## Set to 1 to exclude flat-main-stat Neck/Ring/Boots gear
    ## Note, although users typically prefer scaled % stats to flat stats, Epic Seven has balanced flat stats to be quite useful for many heroes.
    ## For example: LVL60 Mascot Hazel flat attack stats will give better healing than attack %
    ## Heroes like Violet can benefit from flat defense stats over Def% (but an HP% mainstat will be much better than Def flat mainstat)
    ## Additionally, lvl50 heroes are more likely to benefit from flat stats given their lower base stats

primary_sort_stat = 'WW'  ## Recommend not changing this for now
