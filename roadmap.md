<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Roadmap

Effort is a planning estimate in focused development days (five-day target). Statuses: done, in progress, not started, blocked. Section 11.6 additions of the master prompt are mandatory and listed per milestone.

| ID | Milestone | Depends on | Priority | Effort | Status | Blockers |
|---|---|---|---|---|---|---|
| M0 | Bootstrap and feasibility | none | P0 | 0.5 d | done (2026-11-24), pending owner review of scope and cost | none |
| M1 | Research and preregistration | M0 | P0 | 0.5 d | in progress: drafts written, freeze pending | owner freeze of protocols (G-FREEZE) |
| M2 | Core implementation | M1 drafts (freeze not required to implement) | P0 | 1 d | not started | none |
| M3 | Experiments | M2, M1 freeze | P0 | 1 d | not started | owner freeze |
| M4 | Interpretation | M3 | P0 | 0.75 d | not started | none |
| M5 | Interactive experience | M3 results (M4 for labels) | P1 | 0.75 d | not started | none |
| M6 | Release candidate | M4, M5 | P0 | 0.5 d | not started | owner approval for any publication (G-PUBLIC) |

## M0. Bootstrap and feasibility
Acceptance: control files of master prompt section 2 exist; hardware, tools, budget, sources and licences audited (`research/protocol.md` Part A); scope, exclusions and fallback stated; lockfile produced. 11.6: registry, manuscript skeleton and experiment protocols initialised; zero-cost toolchain confirmed (pandoc to Typst smoke build, D-003). Gate: the owner can understand the question, the cost (zero) and the exclusions.

## M1. Research and preregistration
Acceptance: evidence review of verified sources; formal model; baselines; draft protocol (H0/H1, primary metric, unit, seeds, sample size, uncertainty, exclusion and stopping rules, smoke and full matrices, invalidating sensitivity analysis); EXP-001 to EXP-003 protocols; fixture manifest. 11.6: freeze confirmatory protocols before execution, with SHA-256 recorded by the owner. Gate: protocol frozen before confirmatory runs; exploratory results visibly separated.

## M2. Core implementation
Acceptance: environment, policy, mutation, selection, RS, NOSEL, EVO, metrics and runner implemented as pure seeded functions; tests for mutation bounds, fitness scoring, environment determinism, train/test seed isolation, invalid inputs, golden fixtures and an integration test from config to results, all actually run. 11.6: versioned output schemas, reproducibility manifests and report generators built alongside the core. Gate: correctness before UI polish.

## M3. Experiments
Acceptance: exploratory smoke matrix run and runtime measured; metrics validated; frozen full matrix run; every arm, seed, config, metric and failure exported; plots with uncertainty. 11.6: individual reports generated as experiments finish; failures and deviations recorded; provenance captured at run time. Gate: complete planned matrix or documented failure; no silently dropped runs.

## M4. Interpretation
Acceptance: confounders inspected; sensitivity analyses (EXP-003, exploit audit) reported; expected versus observed compared; claims register and limitations completed. 11.6: experiment reports and evidence audit finished; cross-experiment synthesis in the manuscript, including contradictory results. Gate: each numerical claim maps to result ID, config and figure; each external claim to a verified source.

## M5. Interactive experience
Acceptance: static page with animated organisms, ancestry and fitness curves with replay; measured results distinguished from sandbox results; accessibility checks. 11.6: demo, paper, reports and articles use identical verified results, labels and scope. Gate: offline after initial load, responsive, keyboard usable, no fabricated data, no runtime service.

## M6. Release candidate
Acceptance: clean clone, locked install, tests, smoke reproduction, demo build, manifest and link verification, secret and licence scan, actual outputs recorded. 11.6: manuscript and report PDFs compiled and visually inspected; references, cross-links, equations, figures and metadata verified; owner review checklist completed. Gate: verified facts only; the owner approves any publication.

## Cut order if the five-day target is threatened
1. EXP-003 E = 8000 condition. 2. Optional demo features. 3. Test-set size M from 200 to 100. Never cut: EXP-001 primary matrix, controls, reports, evidence audit.
