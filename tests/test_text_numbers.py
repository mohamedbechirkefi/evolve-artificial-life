# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""M6: every decimal number in the README, the articles, the demo README and the
CITATION abstract appears verbatim in the manuscript (the demo itself is covered
by tests/test_demo_export.py)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DECIMAL = re.compile(r"(?<![\w.])-?\d+\.\d+(?![\w.])")
# Version strings and schema versions are not results.
NOT_RESULTS = re.compile(r"\b(?:v|version:?\s*|schema\S*\s+)\d+\.\d+(?:\.\d+)?", re.IGNORECASE)
TEXTS = ["README.md", "articles/README.md", "articles/medium.md", "articles/linkedin.md",
         "demo/README.md", "CITATION.cff"]


def _manuscript_numbers() -> set[str]:
    text = (REPO / "research" / "paper" / "manuscript.md").read_text(encoding="utf-8")
    return {n.lstrip("-") for n in DECIMAL.findall(text.replace("−", "-"))}


@pytest.mark.parametrize("name", TEXTS)
def test_decimals_appear_in_manuscript(name):
    text = (REPO / name).read_text(encoding="utf-8").replace("−", "-")
    if name == "CITATION.cff":
        text = next(line for line in text.splitlines() if line.startswith("abstract:"))
    text = NOT_RESULTS.sub("", text)
    text = re.sub(r"`[^`]*`", "", text)  # code spans hold commands and versions, not results
    known = _manuscript_numbers()
    missing = sorted({n.lstrip("-") for n in DECIMAL.findall(text)} - known)
    assert missing == [], f"{name}: numbers not in the manuscript: {missing}"
