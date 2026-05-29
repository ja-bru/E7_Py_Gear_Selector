"""Shared gear and hero lookup tables."""

import itertools

import pandas as pd

import gear_ref_table as grt
import paths

gear_rating_lookup = grt.gear_rating_lookup.copy()
grl = gear_rating_lookup.to_dict()
gear_tier = pd.read_csv(paths.GEAR_TIERS_CSV)
type_df = grt.type_df.copy()
set_df = grt.set_df.copy()
set_4 = set_df[["Set", "Set_Nm", "Set_Lg"]][set_df.Set_Lg == 4]
set_2 = set_df[["Set", "Set_Nm", "Set_Lg"]][set_df.Set_Lg == 2]
subs_cols = ["subStat1", "subStat2", "subStat3", "subStat4"]

L = [0, 1, 2, 3, 4, 5]
l4 = [",".join(map(str, comb)) for comb in itertools.combinations(L, 4)]
l2 = [",".join(map(str, comb)) for comb in itertools.combinations(L, 2)]
