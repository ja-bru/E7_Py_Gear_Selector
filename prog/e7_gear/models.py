"""Shared typed structures for public APIs."""

from __future__ import annotations

from typing import Any, TypedDict


class StatTarget(TypedDict):
    Min: int | float
    Max: int | float
    Weight: int | float


class BuildConfig(TypedDict, total=False):
    input_sets: list[str]
    exclude_sets: list[str]
    autofill_sets: int
    include_sets: list[str]
    Main_Stats: list[list[str]]
    Force_4Set: int
    Prio: list[str] | None
    ATK: StatTarget
    CRIT: StatTarget
    CDMG: StatTarget
    SPD: StatTarget
    HP: StatTarget
    DEF: StatTarget
    EFF: StatTarget
    RES: StatTarget
    Dmg_Rating: StatTarget
    EHP: StatTarget


# Gear rows are loaded from JSON/OCR; keep flexible until a stricter schema is enforced.
GearItem = dict[str, Any]
