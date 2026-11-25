# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Build the manuscript, supplementary and experiment-report PDFs (M6).

    .venv/bin/python scripts/build_pdfs.py [--keep-typ]

Each PDF is built by `evolve.report.build_pdf` (pandoc Markdown to Typst,
compiled with the `typst` Python package, D-003). The manuscript is compiled
with `research/` as the Typst root because its figures live under
`research/experiments/`. The intermediate `.typ` files are removed unless
`--keep-typ` is given (they are needed to render pages to PNG for inspection).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from evolve.report import build_pdf  # noqa: E402

TARGETS = [
    ("research/paper/manuscript.md", "research"),
    ("research/paper/supplementary.md", "research/paper"),
    ("research/experiments/EXP-001/report.md", "research/experiments/EXP-001"),
    ("research/experiments/EXP-002/report.md", "research/experiments/EXP-002"),
    ("research/experiments/EXP-003/report.md", "research/experiments/EXP-003"),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--keep-typ", action="store_true")
    args = ap.parse_args(argv)
    for md, root in TARGETS:
        pdf = build_pdf(REPO / md, root=REPO / root)
        typ = pdf.with_suffix(".typ")
        if not args.keep_typ and typ.exists():
            typ.unlink()
        print(f"{pdf.relative_to(REPO)} ({pdf.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
