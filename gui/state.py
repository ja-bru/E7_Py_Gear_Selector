"""Shared application state passed between tabs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from e7_gear.optimizer import HeroOptimizationResult


@dataclass
class AppState:
    master_data_path: Path | None = None
    master_data: dict[str, Any] | None = None
    df_items: pd.DataFrame | None = None
    df_hero: pd.DataFrame | None = None
    char_list: list[str] = field(default_factory=list)
    target_stats: dict[str, Any] | None = None
    last_result: HeroOptimizationResult | None = None

    @property
    def is_data_loaded(self) -> bool:
        return self.df_items is not None and self.df_hero is not None

    @property
    def is_scored(self) -> bool:
        return self.is_data_loaded and "efficiency" in self.df_items.columns
