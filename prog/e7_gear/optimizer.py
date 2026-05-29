"""Hero optimization orchestration."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yaml

import paths
from e7_gear.combinator import final_gear_combos, prepare_gear_combinations
from e7_gear.models import BuildConfig
from e7_gear.perf import log_duration
from e7_gear.recommender import prepare_hero_target, run_stat_reco
from e7_gear.stat_engine import bonus_eqp_sum, get_combo_stats, mainst_sum, set_sum, subst_sum


@dataclass
class HeroOptimizationResult:
    char: str
    build: str
    hero_target: BuildConfig
    sc_output: list
    sc_df: pd.DataFrame
    odf: pd.DataFrame
    idx_reco: int
    choice_df: pd.DataFrame
    hero_with_gear: int
    gear_limit: int


def load_target_stats(path=None) -> dict:
    with open(path or paths.CHARACTER_INPUTS_YAML) as file:
        return yaml.load(file, Loader=yaml.FullLoader)


def optimize_hero(
    char: str,
    df_items: pd.DataFrame,
    df_hero: pd.DataFrame,
    hero_target: BuildConfig,
    *,
    build: str = "",
    force_4set: int | None = None,
) -> HeroOptimizationResult | None:
    """
    Run gear combination search, stat calculation, and recommendation for one hero.

    Returns None when no valid gear combinations are found.
    """
    if force_4set is None:
        force_4set = hero_target.get("Force_4Set", 0)

    with log_duration(f"{char}: gear combination search"):
        sc_output, gear_limit = prepare_gear_combinations(
            df_items,
            char,
            hero_target["include_sets"],
            hero_target["Main_Stats"],
            force_4set=force_4set,
        )
    if len(sc_output) == 0:
        return None

    with log_duration(f"{char}: dedupe and score combinations"):
        sc_df, hero_with_gear = final_gear_combos(sc_output, char, df_items)
        odf = get_combo_stats(
            sc_df,
            df_hero,
            mainst_sum(sc_df, df_items),
            subst_sum(sc_df, df_items),
            set_sum(sc_df),
            bonus_eqp_sum(df_hero[df_hero.Name == char]),
            char,
            hero_target,
        )
        idx_reco, choice_df = run_stat_reco(odf, hero_with_gear, hero_target)

    print(f"[perf] {char}: scored {len(odf):,} combinations for recommendation")

    return HeroOptimizationResult(
        char=char,
        build=build,
        hero_target=hero_target,
        sc_output=sc_output,
        sc_df=sc_df,
        odf=odf,
        idx_reco=idx_reco,
        choice_df=choice_df,
        hero_with_gear=hero_with_gear,
        gear_limit=gear_limit,
    )


def optimize_hero_from_template(
    char: str,
    df_items: pd.DataFrame,
    df_hero: pd.DataFrame,
    target_stats: dict,
) -> HeroOptimizationResult | None:
    """Resolve build template from target_stats, then optimize."""
    build, hero_target = prepare_hero_target(char, target_stats)
    return optimize_hero(char, df_items, df_hero, hero_target, build=build)
