# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Tests for the M4 audit helpers (scripts/audit_numbers.py, scripts/m4_sensitivity.py)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_number_match_respects_printed_precision():
    audit = _load("audit_numbers")
    known = np.array([5.791333333, -2.2553, 4.3e-06, 1.7979e-05])
    assert audit.matches("5.791", known)
    assert audit.matches("5.79", known)
    assert not audit.matches("5.792", known)
    assert audit.matches("-2.255", known)
    assert audit.matches("4.3e-06", known)
    assert audit.matches("1.8e-05", known)
    assert not audit.matches("1.7e-05", known)


def test_sensitivity_reading_follows_frozen_rule():
    sens = _load("m4_sensitivity")
    assert sens.reading(0.1, 2.0) == "interval above 0"
    assert sens.reading(-2.0, 0.0) == "interval at or below 0"
    assert sens.reading(-0.5, 2.0) == "interval contains 0"
    lo, hi = sens.t_interval(np.array([1.0, 2.0, 3.0] * 10))
    assert lo < 2.0 < hi
