# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""M6: every relative link in the tracked Markdown files resolves (scripts/check_links.py)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("check_links", REPO / "scripts" / "check_links.py")
check_links = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_links)


def test_repository_links_resolve():
    checked, problems = check_links.check()
    assert checked > 0
    assert problems == []


def test_detects_missing_file_and_anchor(tmp_path):
    (tmp_path / "target.md").write_text("# Results and limits\n\n## S1. Matrix\n", encoding="utf-8")
    doc = tmp_path / "doc.md"
    doc.write_text(
        "[ok](target.md#s1-matrix) [ok2](target.md#results-and-limits) [web](https://example.org/x)\n"
        "[bad file](missing.md) [bad anchor](target.md#nowhere) `[in code](ignored.md)`\n"
        "```\n[in fence](ignored.md)\n```\n",
        encoding="utf-8",
    )
    checked, problems = check_links.check(repo=tmp_path, files=[doc])
    assert checked == 4
    assert len(problems) == 2
    assert any("missing.md: missing file" in p for p in problems)
    assert any("#nowhere: missing anchor" in p for p in problems)


def test_slug_matches_github_style():
    assert check_links.slug("5.1 EXP-001: selection versus random search (primary)") == \
        "51-exp-001-selection-versus-random-search-primary"
