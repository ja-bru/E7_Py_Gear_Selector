"""Runtime settings loaded from config.py with validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import config as cfg


@dataclass
class Settings:
    manual_selection: int = 1
    gear_limit: int = 5
    auto_adj_gear_limit: int = 1
    combo_count_limit: int = 1_000_000
    use_broken_sets: int = 0
    no_equipped_gear: int = 1
    keep_curr_gear: int = 0
    min_level: int = 50
    gear_enhance: int = 12
    flat_sub: float = 0.8
    flat_main: float = 0.5
    ignore_flat_main_stats: int = 0
    primary_sort_stat: str = "WW"

    @classmethod
    def from_config(cls) -> Settings:
        return cls(
            manual_selection=cfg.MANUAL_SELECTION,
            gear_limit=cfg.GEAR_LIMIT,
            auto_adj_gear_limit=cfg.AUTO_ADJ_GEAR_LIMIT,
            combo_count_limit=cfg.COMBO_COUNT_LIMIT,
            use_broken_sets=cfg.USE_BROKEN_SETS,
            no_equipped_gear=cfg.NO_EQUIPPED_GEAR,
            keep_curr_gear=cfg.KEEP_CURR_GEAR,
            min_level=cfg.MIN_LEVEL,
            gear_enhance=cfg.GEAR_ENHANCE,
            flat_sub=cfg.FLAT_SUB,
            flat_main=cfg.FLAT_MAIN,
            ignore_flat_main_stats=cfg.IGNORE_FLAT_MAIN_STATS,
            primary_sort_stat=cfg.primary_sort_stat,
        )

    def apply_to_config(self) -> None:
        cfg.MANUAL_SELECTION = self.manual_selection
        cfg.GEAR_LIMIT = self.gear_limit
        cfg.AUTO_ADJ_GEAR_LIMIT = self.auto_adj_gear_limit
        cfg.COMBO_COUNT_LIMIT = self.combo_count_limit
        cfg.USE_BROKEN_SETS = self.use_broken_sets
        cfg.NO_EQUIPPED_GEAR = self.no_equipped_gear
        cfg.KEEP_CURR_GEAR = self.keep_curr_gear
        cfg.MIN_LEVEL = self.min_level
        cfg.GEAR_ENHANCE = self.gear_enhance
        cfg.FLAT_SUB = self.flat_sub
        cfg.FLAT_MAIN = self.flat_main
        cfg.IGNORE_FLAT_MAIN_STATS = self.ignore_flat_main_stats
        cfg.primary_sort_stat = self.primary_sort_stat

    def validate(self) -> Settings:
        if self.min_level != 60:
            self.min_level = 50
        if not isinstance(self.gear_enhance, int):
            self.gear_enhance = 12
        elif self.gear_enhance < 0 or self.gear_enhance > 15:
            self.gear_enhance = 12
        if self.flat_sub > 1 or self.flat_sub < 0:
            print(type(self.flat_sub))
            print("Flat sub weighting is outside limits, set to default of 80%")
            self.flat_sub = 0.8
        if self.flat_main > 1 or self.flat_main < 0:
            print("Flat main stat weighting (Neck,Ring,Boot) is outside limits, set to default of 50%")
            self.flat_main = 0.5
        return self

    def print_summary(self) -> None:
        print("Checking program configuration")
        if self.manual_selection != 1:
            print("Automated optimization is set, all heroes will run in order without user input to select gear")
        if self.keep_curr_gear == 1:
            print("Gear currently equipped on the hero will be kept")
        else:
            print("Gear currently equipped on your heroes may be replaced during optimization")


def verify_settings(settings: Settings | None = None) -> Settings:
    """Validate settings, sync them to config.py, and print a summary."""
    settings = (settings or Settings.from_config()).validate()
    settings.apply_to_config()
    settings.print_summary()
    return settings


def get_active_setting(name: str) -> Any:
    """Read a validated setting value from config (backward compatible)."""
    return getattr(cfg, name)
