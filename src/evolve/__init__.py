# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""EVOLVE: inherited policies under selection in a synthetic foraging grid world.

All outputs of this package are simulations. Improved task fitness is never
evidence of general intelligence or of biological evolution.

Layers (kept separate, master prompt section 4):
  config    validated, hashable experiment configurations
  seeds     seed derivation and pool isolation
  env       grid environment: layout generation and batched simulation
  policy    fixed-topology neural policy
  search    RS, NOSEL, EVO and SELONLY search arms
  metrics   per-run metrics; stats: paired analysis
  runner    one run and a matrix of runs, with manifests
  schema    versioned JSON result schema, validated at export and import
  report    tables, figures and Markdown/PDF reports from result files
  cli       smoke, run, report and test commands
"""

__version__ = "0.2.0"
ENGINE_VERSION = "evolve-engine/0.2.0"
