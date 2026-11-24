<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# tests/

pytest suite (M2): mutation bounds, fitness scoring, environment determinism (in-process and across worker processes), train/test seed isolation, invalid inputs, hand-computed golden examples, property tests (hypothesis), a differential test of the vectorised engine against a scalar reference, schema validation and an integration test from config to report, plus the freeze gate of the CLI. Run with `uv run pytest` or `./scripts/evolve test`. Last recorded run: see `progress.md`.
