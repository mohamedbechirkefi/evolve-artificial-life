<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Decision log

Append-only. Each entry: id, date, decision, decided by, rationale, alternatives, consequences.

## D-001 (2026-11-24): licence is the owner's custom non-commercial licence

- **Decided by:** the owner.
- **Decision:** all original material is licensed under the EVOLVE Source-Available Non-Commercial Research License v1.0 (SPDX `LicenseRef-EVOLVE-NC-Research-1.0`), with a CLA for contributions. Files: `LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, `CONTRIBUTING.md`, `.github/`.
- **Rationale:** the master prompt (section 2) asks for an "owner-approved permissive code license". On 2026-11-24 the owner chose this protective licence instead, for their own protection.
- **Consequences:** the code is source-available, not OSI open source; README and CITATION.cff say so. Data licences are recorded separately in `data/manifest.json`. Sessions do not change the licence files.

## D-002 (2026-11-24): no external dataset; synthetic procedurally generated environments

- **Decided by:** AI assistant (M0 proposal), subject to owner review.
- **Decision:** all environments are generated locally from recorded seeds by our own generator. Farama Minigrid (Apache-2.0, verified) was considered and not used.
- **Rationale:** the master prompt asks to build the grid environment; no licence or redistribution risk; full control of determinism and seed isolation tests.
- **Consequences:** results hold only within the synthetic environment family (external-validity limit recorded in `research/limitations.md`).

## D-003 (2026-11-24): zero-cost publication toolchain without TeX

- **Decided by:** AI assistant per the M0 brief, subject to owner review.
- **Decision:** Markdown is canonical. PDFs are built by pandoc 3.6.3 (`-t typst`) and compiled with the `typst` 0.15.0 Python package. `manuscript.tex` is generated from Markdown by pandoc and not compiled locally.
- **Rationale:** no TeX distribution is installed (`tex`, `pdflatex`, `xelatex` not found); installing one is not needed and Typst is free and local.
- **Consequences:** LaTeX output is unverified by compilation until a TeX toolchain is available; this is disclosed in the reproducibility report.

## D-004 (2026-11-24): dependency pinning by date cutoff

- **Decided by:** AI assistant per the M0 brief.
- **Decision:** `pyproject.toml` sets `[tool.uv] exclude-newer = "2026-11-09T00:00:00Z"`, so `uv.lock` resolves only releases published at least two weeks before 2026-11-24. Runtime: numpy, matplotlib. Dev: pytest, hypothesis.
- **Consequences:** resolved versions are recorded in `uv.lock` (numpy 2.5.4, matplotlib 3.11.2, pytest 9.2.0, hypothesis 6.170.15).

## D-005 (2026-11-24): draft protocol v0.1 proposed, not frozen

- **Decided by:** AI assistant (proposal only).
- **Decision:** `research/protocol.md` Part B and EXP-001 to EXP-003 protocols are drafts. Primary comparator RS, primary metric held-out test fitness, 20 paired run seeds.
- **Consequences:** no confirmatory run until the owner freezes the protocols and records their SHA-256 here (G-FREEZE).
