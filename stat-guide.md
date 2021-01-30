## Calculated Stats
### Guide to stat calculations and custom stats in this optimizer

### Combat Power (CP)

I used YufineThrowaway's [Reddit Post](https://www.reddit.com/r/EpicSeven/comments/dvdfqp/guide_combat_power_calculation/) on CP Calculation as a reference.
> This is the final combat power formula:
> <br> - P1 = ((att * 1.6 + att * 1.6 * chc * chd) * (1 + (spd - 45) * 0.02) + hp + def * 9.3) * (1 + (res + eff) / 4)
> <br> - P2 = (1 + artifact + exclusive_equipment + specialty_change + skill_upgrade)
> <br> - CP = math.floor(P1 * P2)

Part 1 is quite easy and this formula has been included in the CP calculation.  However, some components of P2 are not included or require user input, so let's walk through them.
| Factor | Description |
| --- | -------------- |
| Artifact | - Artifact level and rarity contribute to CP but are not included in the calculation, which adds a max value of 0.12 to P2.<br> - The additional stats from Artifacts can be added manually into the BonusStats column to be incorporated into final hero stat and P1 calculation. |
| Exclusive Equipment | - If your hero has exclusive equipment available, the optimizer assume it is equipped, adding 0.02 to P2.  EE availability is marked in a column EE in the input file `character_data.csv` but is manually added for new releases.<br> - The additional stats from EE can be added manually into the BonusStats column to be incorporated into final hero stat and P1 calculation. |
| Specialty Change | - If your hero has is a SC character, I've added 0.08 to P2.  I've also included most (but not all) SC heroes in the `master_data.json` file with stat djustments from runes included in the BonusStats input.<br> - Each SC character can have up to 30 rune upgrades, by adding 0.08, it assumes 16 upgrades to skill or passive-based rune (not directly affecting stats).  Based on SC characters available at this time, it seemed like an accurate average number. |
| Skill Upgrades | This was a bit too complicated to add it so it's completed excluded from the CP calculation.  If you have a +15 hero, guess what you'll see a nice CP boost over what is displayed in this tool. |

### Newly created columns

| Column name | Description | Math |
| --- | --- | ------- |
| <b>EHP</b> | Effective Health Points - a calculation of your hero's bulk <br>Note: I divided by 100 compared to other calculators | HP * (1 + Def / 300) / 100 |
| Dmg_Rating | Custom calculation to estimate attack power <br>Note: This is a completed custom field and should be used sparingly as it does not compare to widely used damage calculators and only offers a rating based on damage for attack based skills  |  Attack/2500 * (Crit% * CDmg% + 1-Crit%) * Speed/150 |
| <b>WW</b> | Weighted ranking tool based on stat increases (See below for example) | Sum of each stat based on Weighting Factor * ( Stat differential ) / Max Substat value for lvl88 gear.<br> The stat differential is calculated either as the difference (subtract final stat from base stat; Spd, Crit, CDmg, Eff, Res) or as a ratio (divide final stat over base stat; for HP, Def, Attack)  |
| <b>GR</b> | Shows the average efficiency of the equipped gear | Sums the field GR calculated for each piece of equipped gear and divides by six |

Example of WW Calculation:<br>
> Let's say you are calculating the weighted stat for Krau and care only about HP, Def, Speed.  You set up a relative weight of _HP: 3 to Def: 1 to Speed: 2_ and assume the remaining stats are weighted at 0.
>
> Krau's base stats at level 60, 6* awakened are:  Health 6405, Defense 752, Speed 100.
>
> Let's calculate WW for two different gear options (i) HP 30000 Def 1000 Speed 140 and (ii) HP 22000 Def 1400 Speed 160.
> <br> Option i:
> <br> - (HP) 30000 / 6405 / .09 * 3 = 156.
> <br> - (Def) 1000 / 752 / .09 * 1 = 14.8
> <br> - (Spd) (140 - 100) / 5 * 2 = 16.
> <br>WW = 187
>
> For (ii) WW = 114 + 20 + 24 = 158
> 
> Based on this rating system, option 1 is preferred.

There are some definite flaws in the way WW is calculated.  For example, it makes a 200 speed Krau equivalent to a 12k HP Krau, essentially doubling speed vs doubling HP, but as we know, one is much harder to do than the other.  I'm definitely willing to make some adjustments to this metric with any feedback, or add one or two new metrics.

<br><img alt="Custom_stat_code" src="https://github.com/ja-bru/E7_Py_Gear_Selector/blob/gh-pages/_image/custom_stat_calculation.png?raw=true">
