<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# results/

Machine-readable outputs written by the runner (schema `evolve.run_result` 1.1.0 from 2026-11-24; the M2 exploratory runs used 1.0.0, which remains readable).

- `exploratory/`: runs executed before the protocol freeze, on the exploratory test pool and run seeds of at least 1000 (D-006). **Not findings.** Each folder holds `config.json`, `matrix_manifest.json`, `manifests/` (one run manifest per run) and `report/` (tables, figures, report, PDF, report manifest). The per-run result files in `runs/` are git-ignored and regenerated deterministically with the command recorded in `research/experiment_journal.jsonl`.
- `confirmatory/`: written only by `run` on a frozen protocol. Empty: no protocol is frozen.
- `raw/`: git-ignored scratch space for large outputs.
