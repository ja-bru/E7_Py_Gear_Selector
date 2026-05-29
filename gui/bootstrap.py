"""Ensure `prog/` is on sys.path before importing engine modules."""

from __future__ import annotations

import sys
from pathlib import Path

GUI_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = GUI_DIR.parent
PROG_DIR = PROJECT_ROOT / "prog"

if str(PROG_DIR) not in sys.path:
    sys.path.insert(0, str(PROG_DIR))
