<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Second review pass: arguing against the preferred hypothesis (M4, 2026-11-25)

**Object.** Manuscript draft v0.9 (`research/paper/manuscript.md`, first M4 synthesis), the three experiment reports and the claims register.
**Preferred hypothesis.** "Evolutionary selection with inherited, mutated policies returns foraging policies with higher held-out fitness than independent random search at equal evaluations" (H1 of EXP-001).
**Stance.** Each item below states the strongest case against the preferred reading, checks it against committed results, and records whether it holds and what changed. This is internal quality control by the AI assistant, not peer review. Revised manuscript: v1.0.

## 1. Strongest alternative readings

**R5. The comparator is weak, and the winning ingredient may be local search, not selection.** RS draws 2,000 independent vectors from `N(0, 1)` in 236 dimensions and is never tuned. EVO differs from RS in two ways at once: it takes small steps around good policies, and it keeps a population under truncation selection. NOSEL removes selection but its random walk does not keep the best, and SELONLY removes local steps. No arm is a single-lineage hill climber or local random search that keeps the best policy found, so the data cannot say whether population-based selection adds anything over the simplest local search. *Holds.* v0.9 already said RS is independent sampling, but the abstract and conclusion could be read as "selection beats random search" in general. **Change:** new Discussion paragraph "What the comparator does not show"; abstract adds "says nothing about other local search methods"; conclusion and follow-ups name the missing comparator; limitation 15; C-001 limitation column updated.

**R6. The K1 result admits a second reading.** v0.9 presented "selection fits the single layout" as the other side of the proposed mechanism. An equally consistent reading is that five resampled, noisy training environments per evaluation are what make selected policies transfer, so the "advantage of selection" is an interaction between selection and the training design. The design pairs each condition with one training design and cannot separate the two. *Holds.* **Change:** the K1 mechanism is labelled an interpretation and the alternative reading is stated (Discussion, Mechanism); limitation 17.

**R4. "The advantage grew with the budget" overstates what EXP-003 can show.** Population size and generations scale with the budget (25 x 20, 50 x 40, 100 x 80), and no trend test was frozen. *Holds.* **Change:** Results 5.3 now says the difference "was larger at larger budgets" and that budget is confounded with P and G; C-015 registers the description with that limit; limitation 16.

**Sigma.** A sceptic can argue that the EXP-001 effect is an arbitrary point of a sweep in which a setting seen before the freeze was better, so the headline number is not representative. *Partly holds.* The frozen sigma was kept to avoid tuning on seen data, and the effect size is already described as specific to sigma 0.1 and not an upper bound. The reverse argument (that sigma 0.5 merely moves EVO toward random search) is contradicted by the data: EVO-sigma0.5 scored 12.296 against 4.728 for RS. **Change:** none beyond existing text.

**Elite re-evaluation (EXP-002 section 4).** v0.9 said the elite "is not a plausible source of an 8-item effect". That is an argument, not a test. *Holds as a wording issue.* **Change:** reworded to "argues against, but does not test", with the counts (39 of 2,000 evaluations; returned EVO policy an elite re-evaluation in 2 of 30 runs).

## 2. Overgeneralisation

**R3.** The v0.9 abstract said "Removing selection or mutation removed the advantage". The ablations were compared with EVO, not with RS. *Holds.* **Change:** "lowered held-out fitness by about 8 items".

**R2.** v0.9 Results 5.2 said the ablations fell "to below the RS level of EXP-001". That compares means across experiments; no paired SELONLY minus RS contrast was registered. *Holds.* **Change:** stated as a comparison of means without a registered paired contrast; C-016 limitation column says so.

**Title and claims boundary.** The title names "evolutionary selection" and "a simulated foraging grid"; the abstract ends with the claims-boundary sentence. No statement about biology or general intelligence. *Does not hold.* No change.

**Shifted distribution.** F_shift results are descriptive; no generalisation claim beyond the one shifted generator is made. *Does not hold.* No change.

## 3. Stale figures and numbers

**R1. Double counting.** v0.9 Section 5.4 said 25 returned policies stayed in place on more than half of their steps. The 7 NOSEL cases of EXP-002 are the same runs as EXP-001's (60 of 60 shared runs identical). Distinct count: 18. *Holds.* **Change:** corrected in v1.0 and in C-014 (audit finding A9).

**Figures.** All report figures are byte-identical to the result folders and were generated from the committed runs at revision 5d39c9b; the manuscript reuses the report figures by path rather than copies. *Does not hold.* No change.

**Numbers.** The scripted audit (`scripts/audit_numbers.py`) found no numerical mismatch in v0.9 or v1.0. *Does not hold.*

## 4. Leakage

- Test and training pools are separate `SeedSequence` spawn keys, with a test that no test layout appears among training layouts.
- The test and shifted sets were never used for any choice; hyperparameters were fixed at freeze.
- The pilot used a separate exploratory pool and seeds of 1000 and above (D-006).
- **R7, pre-freeze exposure.** The pilot showed every confirmatory direction before the freeze, and two amendments (C.1 seed count, C.3 NOSEL expectation) were informed by it. This is not leakage of the confirmatory pool, but the NOSEL "prediction" is not an independent prediction. *Partly holds.* **Change:** Table 5 marks the NOSEL expectation as "informed by the pilot"; limitation 18; Limitations section of the manuscript.

## 5. Missing failed runs and hidden analyses

- Confirmatory: 420 of 420 runs ok, 0 failed, retried or dropped (status counts in every `analysis.json`; matrix manifests).
- Exploratory runs are all listed with journal ids (supplementary S6), including smoke, pilot, determinism and timing checks.
- The optional truncation-size test and the EXP-002 sigma sweep at other budgets were not run; both are disclosed.
- No analysis was added after the data except the labelled exploratory M4 re-analysis (J-0012), which changes no verdict.
*Does not hold.* No change.

## 6. Citations

**R16.** v0.9 Discussion repeated that the method of Mania et al. (2018) "is not the independent sampling used here", which the abstract does not support (the same issue fixed in the EXP-001 report, audit A3). *Holds.* **Change:** reworded to "only its abstract was read, and the RS arm here is not a replication of it".

## 7. Summary of changes from v0.9 to v1.0

| Item | Section(s) changed | Claims register / limitations |
|---|---|---|
| R1 double counting | 5.4 | C-014 |
| R2 cross-experiment comparison | 5.2 | C-016 |
| R3 abstract overgeneralisation | Abstract | none |
| R4 budget confounded with P and G | 5.3 | C-015, limitation 16 |
| R5 missing local-search comparator | Abstract, 6, 7, 9 | C-001, limitation 15 |
| R6 second reading of K1 | 6 | limitation 17 |
| R7 pilot-informed predeclarations | 6 (Table 5), 7 | limitation 18 |
| Elite wording | 6 | C-017 |
| R16 citation overstatement | 6 | limitation 20 |

**Verdicts after the challenge.** No frozen verdict changes. H1 of EXP-001 stands within its stated scope; the challenge narrows what it means (this genetic algorithm versus independent sampling, with resampled training) rather than overturning it. The K1 inconclusive result and the sigma 0.5 contradicting result remain in the abstract.
