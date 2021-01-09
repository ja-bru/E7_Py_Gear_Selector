## SET UP FILE

## THESE SETTINGS WILL DETERMINE HOW THE PROGRAM RUNS

## RUN SETTINGS
SELECTOR = 1            ##  MANUAL RUN VERSUS AUTOMATED RUN {1:  Program will run with user prompt to select gear from a refined list}
GEAR_LIMIT = 15         ## This variable impacts run time.  It is the default number of gear items for each slot to use in optimization
AUTO_ADJ_GEAR_LIMIT = 1 ## Adjusts the number of gear pieces selected based on combinations to optimize run time vs available selections

## GEAR SELECTION
COMPLETE_SETS = 1       ## This program will only generate complete gear sets at this time
NO_EQUIPPED_GEAR = 1    ## {1: will use unequipped gear only;  0: uses equipped gear that is not locked}
USE_CURR_EQUIP = 0      ## Keeps any currently equipped gear on the hero

## STAT SELECTION
GEAR_12 = 1             ## Enhance all main stats to at least 12
FLAT_SUB = 0.8          ## Weight flat stat values in substats {range 0.0-1.0}
FLAT_MAIN = 0.5         ## Weight value attributed to [Necklace, Ring, Boots] with flat main stats {range 0.0-1.0}
    ## Note, although users typically prefer scaled % stats to flat stats, Epic Seven has balanced flat stats to be quite useful for many heroes.
    ## For example: LVL60 Mascot Hazel flat attack stats will give better healing than attack %
    ## Heroes like Violet can benefit from flat defense stats over Def% (but an HP% mainstat will be much better than Def flat mainstat)
    ## Additionally, lvl50 heroes are more likely to benefit from flat stats given their lower base stats
