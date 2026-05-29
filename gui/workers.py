"""Background workers for long-running engine tasks."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QThread, Signal

import fx_lib as fx
from e7_gear.optimizer import HeroOptimizationResult, load_target_stats, optimize_hero_from_template
from e7_gear.scoring import score_all_items


class ScoreGearWorker(QThread):
    """Load master_data.json and score all gear items."""

    finished_ok = Signal(object, object, object, list, dict)
    failed = Signal(str)
    status = Signal(str)

    def __init__(self, master_data_path: Path, parent=None):
        super().__init__(parent)
        self.master_data_path = master_data_path

    def run(self) -> None:
        try:
            self.status.emit("Loading gear data…")
            with open(self.master_data_path, encoding="utf-8") as json_file:
                data = json.load(json_file)

            self.status.emit("Parsing items…")
            df_items = fx.item_json_to_df(data)
            df_items = fx.gear_stats(df_items)

            self.status.emit("Scoring gear…")
            df_items = score_all_items(df_items)
            df_items = df_items.sort_values(by=["hero", "Type", "efficiency", "enhance"])

            self.status.emit("Loading hero templates…")
            target_stats = load_target_stats()
            hero_order = fx.startup_msg1(target_stats)
            lock_gear = target_stats.get("Lock_Gear", [])
            df_hero, char_list = fx.hero_json_to_df(hero_order, data)
            df_items = fx.startup_msg2(df_items, lock_gear)

            self.finished_ok.emit(df_items, df_hero, data, char_list, target_stats)
        except Exception as exc:
            self.failed.emit(str(exc))


class OptimizeWorker(QThread):
    """Run optimize_hero for one character."""

    finished_ok = Signal(object)
    failed = Signal(str)
    status = Signal(str)

    def __init__(
        self,
        char: str,
        df_items: pd.DataFrame,
        df_hero: pd.DataFrame,
        target_stats: dict,
        parent=None,
    ):
        super().__init__(parent)
        self.char = char
        self.df_items = df_items
        self.df_hero = df_hero
        self.target_stats = target_stats

    def run(self) -> None:
        try:
            self.status.emit(f"Optimizing {self.char}…")
            result = optimize_hero_from_template(
                self.char,
                self.df_items,
                self.df_hero,
                self.target_stats,
            )
            if result is None:
                self.failed.emit(f"No gear combinations found for {self.char}.")
                return
            self.finished_ok.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))
