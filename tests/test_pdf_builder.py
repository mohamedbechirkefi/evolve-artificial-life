# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""M6: PDF builder helpers (title metadata fallback and Typst table layout)."""

from __future__ import annotations

from evolve.report import _fallback_title, _typst_layout


def test_fallback_title_uses_first_heading_without_yaml_title():
    assert _fallback_title("<!-- x -->\n# EXP-001 report: a title\n\n## 1. Section\n") == "EXP-001 report: a title"
    assert _fallback_title("---\ntitle: \"Paper\"\n---\n\n# Abstract\n") is None
    assert _fallback_title("no heading here\n") is None


def test_typst_layout_sizes_columns_and_keeps_caption_with_table():
    typ = (
        "== 5.2 Heading\n#strong[Table 3.] Caption text.\n\n"
        "#figure(\n  align(center)[#table(\n    columns: (25%, 25%, 25%, 25%),\n  )]\n)\n\n"
        "#strong[Table 9.] Caption not followed by a table.\n\nParagraph.\n"
    )
    out = _typst_layout(typ)
    assert out.startswith("// evolve.report layout rules")
    assert "#show table: set par(justify: false)" in out
    assert "columns: 4," in out and "25%" not in out
    assert "== 5.2 Heading\n#block(sticky: true)[#strong[Table 3.] Caption text.]" in out
    assert "#block(sticky: true)[#strong[Table 9.]" not in out
