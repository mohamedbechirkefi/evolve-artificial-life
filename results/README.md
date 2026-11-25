<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# results/

Machine-readable outputs written by the runner (schema `evolve.run_result` 1.1.0 from 2026-11-24; the M2 exploratory runs used 1.0.0, which remains readable).

- `exploratory/`: runs executed before the protocol freeze, on the exploratory test pool and run seeds of at least 1000 (D-006). **Not findings.** Each folder holds `config.json`, `matrix_manifest.json`, `manifests/` (one run manifest per run) and `report/` (tables, figures, report, PDF, report manifest). The per-run result files in `runs/` are git-ignored and regenerated deterministically with the command recorded in `research/experiment_journal.jsonl`.
- `exploratory/m4-sensitivity-2026-11-25/`: M4 exploratory re-analysis of the committed confirmatory results (J-0012, `scripts/m4_sensitivity.py`); no simulation, never replaces a frozen verdict.
- `confirmatory/`: written only by `run` on a frozen protocol (protocol v1.0, frozen 2026-11-24). `EXP-001/`, `EXP-002/`, `EXP-003/` (M3, 2026-11-25) each hold `runs/` (raw run files, committed: each experiment is under 20 MB), `manifests/`, `config.json`, `matrix_manifest.json`, `run_provenance.json`, `run.log`, `report/` (generator tables and FIG-1, FIG-2), `analysis/` (frozen analysis `analysis.json` and FIG-3, from `scripts/analyse_frozen.py`) and `sha256_manifest.json`.
- `raw/`: git-ignored scratch space for large outputs.
