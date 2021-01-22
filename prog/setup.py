## SET UP FILE

## THESE SETTINGS WILL DETERMINE HOW THE PROGRAM RUNS

## RUN SETTINGS
MANUAL_SELECTION = 1    ##  MANUAL RUN VERSUS AUTOMATED RUN {1:  Program will run with user prompt to select gear from a refined list}
GEAR_LIMIT = 5         ## This variable impacts run time.  It is the default number of gear items for each slot to use in optimization
AUTO_ADJ_GEAR_LIMIT = 1 ## Adjusts the number of gear pieces selected based on combinations to optimize run time vs available selections

## GEAR SELECTION
USE_BROKEN_SETS = 0      ## This program will only generate complete gear sets at this time
NO_EQUIPPED_GEAR = 1    ## {0,1)} {1: will use unequipped gear only;  0: uses equipped gear that is not locked}
KEEP_CURR_GEAR = 0      ## Keeps any currently equipped gear on the hero

## HERO CRITERIA
MIN_LEVEL = 50          ## Default Hero level of either 50 or 60 for stat calculation
## STAT SELECTION
GEAR_ENHANCE = 12         ## Enhance gear to minimum level for stat selection/optimization
FLAT_SUB = 0.8          ## Weight flat stat values in substats {range 0.0-1.0, default:0.8}
FLAT_MAIN = 0.5         ## Weight value attributed to [Necklace, Ring, Boots] with flat main stats {range 0.0-1.0, default:0.5}
    ## Note, although users typically prefer scaled % stats to flat stats, Epic Seven has balanced flat stats to be quite useful for many heroes.
    ## For example: LVL60 Mascot Hazel flat attack stats will give better healing than attack %
    ## Heroes like Violet can benefit from flat defense stats over Def% (but an HP% mainstat will be much better than Def flat mainstat)
    ## Additionally, lvl50 heroes are more likely to benefit from flat stats given their lower base stats

primary_sort_stat = 'WW'  ##recommend not changing this for now
