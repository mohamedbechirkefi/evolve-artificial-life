<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Evidence audit and claims audit (M4, 2026-11-25)

Master prompt 11.5. This file records the evidence audit of the manuscript (`research/paper/manuscript.md` v1.0), the supplementary file, the three experiment reports, the claims register and the limitations, with its findings and every mismatch fixed. It is internal quality control by the AI assistant, not external peer review.

## 1. Checklist

- [x] Every row of `research/claims_register.csv` has an evidence path that exists (27 rows: C-001 to C-017 results, C-020 to C-029 external).
- [x] Every numerical claim maps to an EXP id, run ids, config hash and figure or table id (register columns `result_id`, `config_hash`, `figure_or_table`, `section`; `research/publication/artifact_manifest.json`).
- [x] Every external claim maps to a source re-opened on 2026-11-25 and listed in `research/literature_review.md`; all are marked abstract-level (C-029, a blog post, was read in full).
- [x] Numbers re-derived from raw outputs: denominators, units, precision, uncertainty, sample counts (section 3).
- [x] No claim of general intelligence or biological evolution evidence (manuscript abstract, sections 7, 8 and 9).
- [x] Simulated results labelled simulated in the manuscript, supplementary file and reports. Demo and articles do not exist yet (M5).
- [x] Second review pass that challenges the preferred hypothesis, recorded with findings (`research/publication/review_pass_2.md`).
- [x] Failed, null and exploratory results present and labelled (no confirmatory run failed; K1 null result and the sigma 0.5 contradicting result in abstract, results and discussion; exploratory work listed in supplementary S6).

## 2. Method

| Step | Tool | Output |
|---|---|---|
| Raw-file integrity: 420 run files against `sha256_manifest.json`; seeds 0 to 29 in every cell; status ok; one code revision; clean tree | `scripts/audit_numbers.py` (check A) | `research/publication/number_audit.json` |
| Summary tables recomputed from raw runs (n_ok, mean, SD, min, max of every metric column) | check B | 506 values, 0 mismatches |
| Frozen analysis recomputed from raw runs (paired differences, mean, SD, 95 percent bootstrap CI with the frozen resamples and seed, n) | check C | 114 values, 0 mismatches |
| EXP-002 reuse of EXP-001 runs | check E | 60 of 60 shared runs have identical metrics |
| Number scan: every decimal number in the 7 documents must equal, at its printed precision, a value in a committed machine-readable result | check D | see section 3 |
| Integer counts (seeds positive and negative, stay-in-place counts, zero scores, replay checks) | ad-hoc commands recorded in `progress.md` | matched |
| Figures: report copies against result copies | `cmp` | 18 of 18 figure files and 3 of 3 metrics files byte-identical |
| External claims | sources re-opened 2026-11-25 | `research/literature_review.md`, M4 re-check |

Units: all fitness quantities are food items per episode (F_test, F_shift, F_train_fresh, F_train_fixed, gap, overfit_drop). Denominators: n = 30 paired run seeds per contrast (29 only in the labelled exploratory exclusion of K1 seed 13). Uncertainty: 95 percent percentile bootstrap over run seeds, 10,000 resamples, seed 0, everywhere a CI is printed without other qualification; Bonferroni and Student t intervals appear only in labelled exploratory text. Precision: three decimals for means and CIs, two for d_z, two significant figures for Wilcoxon p.

## 3. Number-scan result (final run)

| Document | Decimal numbers | Unmatched | Explanation of unmatched |
|---|---|---|---|
| `research/experiments/EXP-001/report.md` | 110 | 0 | |
| `research/experiments/EXP-002/report.md` | 163 | 1 (98.75) | Bonferroni level, defined as 100 x (1 - 0.05/4); the level 0.9875 is stored in `sensitivity.json` |
| `research/experiments/EXP-003/report.md` | 195 | 1 (98.33) | Bonferroni level 100 x (1 - 0.05/3); 0.98333 stored in `sensitivity.json` |
| `research/paper/manuscript.md` | 185 | 2 (98.33, 98.75) | as above |
| `research/paper/supplementary.md` | 96 | 2 (98.33, 98.75) | as above |
| `research/claims_register.csv` | 82 | 0 | |
| `research/limitations.md` | 11 | 0 | |

Hashes, git revisions, arXiv identifiers and URLs are excluded from the scan. Planning quantities (for example d_z = 0.53 at 80 percent power) are labelled as planning approximations in the text and come from the frozen protocol.

## 4. Findings and fixes

| # | Finding | Severity | Fix |
|---|---|---|---|
| A1 | `claims_register.csv` row C-001 was malformed: an unquoted comma inside the evidence path (`{EVO,RS}`) split it into two fields, shifting scope, status and limitations by one column. | medium (machine-readability) | Row repaired and the file rewritten with proper quoting; register restructured with `result_id`, `config_hash`, `figure_or_table` and `section` columns. |
| A2 | `experiment_registry.csv` still said "11.3 report not yet written" for all three experiments, although the reports exist since M3. | low (stale status) | Status updated; the word "frozen" required by the freeze guard is kept. |
| A3 | EXP-001 report (section 9) described the method of Mania et al. (2018) as "a local method with a step rule"; the abstract does not say this. Limitation 12 attributed "tuned local random search" to the same source. | medium (external claim beyond the read source) | Sentence and limitation rewritten to abstract-level content; report version 1.1. |
| A4 | EXP-001 and EXP-002 reports (section 3) attributed "Gaussian mutation and truncation selection" to Such et al. (2017); the abstract names only a simple, gradient-free, population-based genetic algorithm. | medium | Reworded: the operators are this project's design choices. |
| A5 | EXP-003 report (section 3) said Cobbe et al. (2019) show that training on fixed levels and testing on held-out levels exposes overfitting; the abstract does not describe a level split. | medium | Reworded to the abstract's content. |
| A6 | EXP-002 report (section 3) cited Henderson et al. (2017) for variation with seeds; the abstract speaks of variance intrinsic to the methods. | low | Paraphrase aligned with the abstract. |
| A7 | The frozen EXP protocols (section 3) contain the wording of A4 and A5. | low | Not edited (frozen files); disclosed here, in the literature review and in limitation 20. |
| A8 | Number scan of the three reports: 0 numerical mismatches against the raw outputs; the only unmatched tokens were arXiv identifiers (now excluded) and load averages, which are stored as strings in `run_provenance.json` (the scanner now reads them). | none | Scanner improved; no number changed. |
| A9 | Manuscript draft v0.9 said 25 returned policies stayed in place on more than half of their test steps; the 7 NOSEL cases of EXP-002 are the same runs as in EXP-001, so the distinct count is 18. Found by the second review pass (R1). | medium | Corrected to 18 distinct in v1.0 and in C-014. |
| A10 | Manuscript draft v0.9 repeated the overstatement of A3 in its discussion. Found by the second review pass (R16). | medium | Corrected in v1.0. |
| A11 | Report figures and per-run tables were checked for staleness: all copies are byte-identical to the result folders, generated at revision 5d39c9b from the committed runs. | none | none |

No numerical result changed in this audit, and no frozen file, config, seed or verdict was touched.

## 5. Strength and scope of each conclusion

| Conclusion | Claims | Evidence strength | Scope |
|---|---|---|---|
| EVO beats RS on held-out fitness at E = 2,000, K = 5 | C-001 | confirmatory, frozen rule, 29 of 30 seeds, robust to all exploratory checks | one task, one architecture, sigma 0.1, independent-sampling RS |
| Neither mutation nor selection alone reproduces EVO | C-003, C-004 | confirmatory estimates, 30 of 30 seeds each, no multiplicity adjustment (robust to Bonferroni, exploratory) | as above |
| sigma 0.1 is not the best tested setting | C-005, C-006 | confirmatory estimate; contradicting result by the owner's classification | three sigma levels at E = 2,000 only |
| Advantage holds at E = 500 and 8,000 | C-007, C-008, C-015 | confirmatory; trend descriptive only | budget confounded with P and G |
| Advantage depends on resampled training | C-009, C-010 | confirmatory inconclusive result plus overfitting estimate | K = 1 versus K = 5 only |
| No exploit behind the advantage | C-014 | audit of stay-in-place and replay | other exploit routes not enumerated |

## M6 reference check (2026-11-25)

- Every in-text citation of the manuscript (10 author-year citations) resolves to an entry of `research/paper/references.bib`, and every bib entry (10) is cited in the manuscript body and listed in its reference list.
- Source labels: read in full 1 (krakovna2020specification, blog post); full text consulted for the cited passage 9 (all other entries, free arXiv or JMLR open-access PDFs, page or section recorded in `research/literature_review.md`, M6 section and in the `status` column of `research/claims_register.csv`); abstract only 0; unverified 0. Two uncited, unverified sources stay out of the bibliography.
- Every cited claim was confirmed by its passage. Two passages say more than the abstracts did: Such et al. (Section 3) name the operators, and Cobbe et al. (pp. 3-5) describe a train and held-out level split. The M4 sentences that said the abstracts did not describe these were updated in the manuscript (Section 2, Discussion, limitations), the three experiment reports (version 1.2, section 3) and `research/limitations.md` item 20. No number changed; no claim was strengthened beyond the passages.
- The frozen protocols keep their original wording.
