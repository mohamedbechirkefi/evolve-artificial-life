<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# EXP-001 reproduction

Simulation only, no external data. From the repository root, with the frozen files unchanged (`research/freeze.json`) and the code at the provenance revision 5d39c9bf1eae7356b1fa837642e02e4bde68e186:

1. `uv sync --frozen --all-groups --all-extras` (uv 0.9.5; in the development environment the binary is `../.tools/py/bin/uv`, relative to the repository root)
2. `.venv/bin/python -m pytest -q` (all tests must pass)
3. `./scripts/run_confirmatory.sh EXP-001 2` into an empty `results/confirmatory/EXP-001`
4. `PYTHONPATH=src .venv/bin/python -m evolve report --results results/confirmatory/EXP-001`
5. `.venv/bin/python scripts/validate_results.py results/confirmatory/EXP-001`
6. `.venv/bin/python scripts/analyse_frozen.py EXP-001`

Expected: the `metrics`, `episodes` and `trace` fields of every run file are identical at the same revision and NumPy version. Whole-file hashes in `results/confirmatory/EXP-001/sha256_manifest.json` identify the committed files; a re-execution produces different file hashes because each run file embeds its own timing and host manifest.
