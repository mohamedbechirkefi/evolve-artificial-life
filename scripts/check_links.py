# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Check that every relative link in the repository's Markdown files resolves (M6).

    .venv/bin/python scripts/check_links.py

Scans tracked Markdown files (git ls-files '*.md'), excluding `master_prompt.md`
(the owner's authority file, never edited). For each inline link or image
`[text](target)` whose target is not an absolute URL (http, https, mailto), the
path part must name an existing file or folder relative to the Markdown file,
and an anchor `#fragment` must match a heading slug of the target file (GitHub
style). Prints one line per broken link and a summary line; exits 1 on any failure.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXCLUDE = {"master_prompt.md"}
LINK = re.compile(r"!?\[(?:[^\]\[]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^(```|~~~)")
EXTERNAL = ("http://", "https://", "mailto:", "ftp://")


def slug(heading: str) -> str:
    """GitHub-style heading anchor."""
    s = heading.strip().lower()
    s = re.sub(r"[`*_~]", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(md: Path) -> set[str]:
    out: set[str] = set()
    seen: dict[str, int] = {}
    in_fence = False
    for line in md.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            base = slug(m.group(2))
            n = seen.get(base, 0)
            out.add(base if n == 0 else f"{base}-{n}")
            seen[base] = n + 1
        for a in re.findall(r"<a\s+(?:name|id)=\"([^\"]+)\"", line):
            out.add(a)
    return out


def links(md: Path) -> list[tuple[int, str]]:
    found = []
    in_fence = False
    for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        text = re.sub(r"`[^`]*`", "", line)  # links inside inline code are not links
        for target in LINK.findall(text):
            found.append((i, target))
    return found


def check(repo: Path = REPO, files: list[Path] | None = None) -> tuple[int, list[str]]:
    if files is None:
        names = subprocess.run(["git", "ls-files", "*.md"], cwd=repo, capture_output=True,
                               text=True, check=True).stdout.split()
        files = [repo / n for n in names if Path(n).name not in EXCLUDE]
    checked = 0
    problems: list[str] = []
    for md in files:
        for lineno, target in links(md):
            if target.startswith(EXTERNAL):
                continue
            checked += 1
            path_part, _, frag = target.partition("#")
            dest = md if not path_part else (md.parent / path_part).resolve()
            where = f"{md.relative_to(repo)}:{lineno}: {target}"
            if not dest.exists():
                problems.append(f"{where}: missing file")
                continue
            if frag and dest.is_file() and dest.suffix == ".md" and frag not in anchors(dest):
                problems.append(f"{where}: missing anchor")
    return checked, problems


def main() -> int:
    checked, problems = check()
    for p in problems:
        print(p)
    print(f"{checked} relative links checked; {len(problems)} broken")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
