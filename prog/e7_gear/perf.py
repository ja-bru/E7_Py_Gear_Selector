"""Lightweight performance logging helpers."""

from __future__ import annotations

import time
from contextlib import contextmanager


@contextmanager
def log_duration(label: str):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"[perf] {label}: {elapsed:.2f}s")
