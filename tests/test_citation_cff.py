# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""M6: CITATION.cff is structurally valid CFF 1.2.0 (keys and types), its title
matches the manuscript, it reads as a release candidate and has no release date.

No YAML library is installed, so this parses the file's flat layout (top-level
`key: value` lines and one `authors` list of mappings) and fails on anything else.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ALLOWED = {  # CFF 1.2.0 top-level keys used or permitted here, with their type
    "cff-version": str, "message": str, "title": str, "type": str, "authors": list,
    "version": str, "abstract": str, "keywords": list, "license": str, "license-url": str,
    "repository-code": str, "url": str, "doi": str, "date-released": str, "identifiers": list,
    "preferred-citation": dict, "references": list, "commit": str, "contact": list,
}
PERSON_KEYS = {"family-names", "given-names", "name-particle", "name-suffix", "affiliation",
               "orcid", "alias", "email", "website", "name"}


def _unquote(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def parse(text: str) -> dict:
    data: dict = {}
    current = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw.startswith(" "):
            key, sep, val = raw.partition(":")
            assert sep, f"not a key line: {raw!r}"
            assert key not in data, f"duplicate key {key}"
            if val.strip():
                data[key] = _unquote(val)
                current = None
            else:
                data[key] = []
                current = key
            continue
        assert current is not None, f"indented line outside a list: {raw!r}"
        line = raw.strip()
        if line.startswith("- "):
            data[current].append({})
            line = line[2:]
        k, sep, v = line.partition(":")
        assert sep and data[current], f"bad list item: {raw!r}"
        data[current][-1][k.strip()] = _unquote(v)
    return data


def test_citation_cff_structure_title_and_version():
    cff = parse((REPO / "CITATION.cff").read_text(encoding="utf-8"))
    for key in ("cff-version", "message", "title", "authors"):
        assert key in cff, f"missing required key {key}"
    for key, value in cff.items():
        assert key in ALLOWED, f"unknown key {key}"
        assert isinstance(value, ALLOWED[key]), f"{key} has type {type(value).__name__}"
    assert cff["cff-version"] == "1.2.0"
    assert cff["type"] in ("software", "dataset")
    assert cff["authors"] and all(set(a) <= PERSON_KEYS for a in cff["authors"])
    assert all(a.get("family-names") or a.get("name") for a in cff["authors"])
    assert "date-released" not in cff  # removed until a release exists (owner-approvals-2026-11-25e)
    assert re.fullmatch(r"\d+\.\d+\.\d+-rc\d+", cff["version"])
    manuscript = (REPO / "research" / "paper" / "manuscript.md").read_text(encoding="utf-8")
    ms_title = re.search(r'^title: "(.*)"$', manuscript, re.M).group(1)
    assert cff["title"] == ms_title
    assert "@" not in (REPO / "CITATION.cff").read_text(encoding="utf-8")
