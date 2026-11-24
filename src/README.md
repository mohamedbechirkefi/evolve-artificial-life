<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# src/

Python package `evolve` (M2). Layers are separate modules: `config` (validated, hashable configs; equal-budget check), `seeds` (stream derivation and pool isolation), `env` (grid world: layout generation, vectorised engine, scalar reference engine), `policy` (236-parameter network), `search` (RS, NOSEL, EVO, SELONLY), `metrics` and `stats` (per-run metrics, paired bootstrap, Wilcoxon, planning formulas), `runner` (runs and matrices with manifests), `schema` and `schemas/` (versioned result schema), `freeze` (read-only freeze check against `research/freeze.json` and the registry), `report` (tables, figures, Markdown and PDF), `cli`. Run with `./scripts/evolve` or `PYTHONPATH=src uv run python -m evolve`.
