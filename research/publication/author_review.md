<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Owner review checklist (for the owner; not started)

- [ ] Protocols frozen and SHA-256 recorded in `research/decision_log.md`.
- [ ] Author and affiliation metadata approved. (Recorded decision, for the owner to confirm by ticking: 2026-11-24, common decision C3, "Mohamed Bechir Kefi", no affiliation; the AI is disclosed as a research and development assistant, not as an author. This box had been ticked by the AI assistant at commit fc69607 and was unticked in M5, D-015, because only the owner ticks these boxes.)
- [ ] AI-assistance disclosure reviewed (actual AI role and human verification performed). (Record: the owner approved the section 11 wording on 2026-11-25, D-014; the full-text review is M6.)
- [ ] Funding and competing-interest statements reviewed. (Record: wording approved by the owner on 2026-11-25, D-014; "none declared" still needs the owner's confirmation of the facts.; 2026-11-26: the owner confirmed no funding and no competing interests, B4, and the box stays for the owner to tick.)
- [ ] Every claim in the manuscript and articles reviewed against the claims register.
- [ ] Licence text and NOTICE reviewed for the release.
- [ ] Publication, push and release explicitly approved.

## Prepared for the owner (M6, 2026-11-25)

No box above was ticked by an agent in M6, and none was ticked when M6 started (the box an agent had ticked at commit fc69607 was unticked in M5, D-015). Only the owner ticks these boxes.

### What to read for each box

1. Protocols frozen: `research/freeze.json` (SHA-256 of `research/protocol.md`, the three EXP protocols and the three configs), `research/decision_log.md` D-010 (freeze and amendments), and `research/paper/supplementary.md` S3 (the same hashes, checked against `research/freeze.json` in M6).
2. Author and affiliation: `CITATION.cff` (authors) and the manuscript front matter (`research/paper/manuscript.md`, line 4); the recorded decision is C3 in `research/decision_log.md`.
3. AI-assistance disclosure: `research/paper/manuscript.md` section 11 and the approval record in `research/decision_log.md` D-014.
4. Funding and competing interests: `research/paper/manuscript.md` section 11 (line 249).
5. Claims against the register: `research/claims_register.csv` (C-001 to C-029), `research/publication/claims_audit.md` (including the M6 reference check), `research/literature_review.md` (M6 full-text check), then the manuscript, the supplementary file, the three reports (`research/experiments/EXP-00N/report.md` and `report.pdf`) and the articles (`articles/medium.md`, `articles/linkedin.md`).
6. Licence and NOTICE: `LICENSE`, `NOTICE.md`, `LICENSE_HISTORY.md`, `CLA.md`, and `research/publication/dependency_licences.md` (no dependency flagged).
7. Publication approval: `research/publication/release_checklist.md` and `research/publication/reproducibility_report.md` (M6 clean-clone record).

### Open decisions for this repository

- The manuscript title ("Evolutionary selection versus independent random search at equal evaluation budgets in a simulated foraging grid: a preregistered paired comparison with ablations and a sensitivity analysis") is not covered by the owner's title approval of 2026-11-25, which names other projects (D-015), so the owner approves or revises it. (Resolved 2026-11-26, B6; see below.)
- In M6 the `CITATION.cff` title was aligned with that manuscript title and the version set to `0.1.0-rc1`, so the owner confirms both or gives others. (Resolved 2026-11-26, B6, B7, B8; see below.)
- The funding statement "none declared" is marked "[to be confirmed by the owner]" and needs the owner's confirmation of the fact. (Resolved 2026-11-26, B4.)
- The competing-interests statement "none declared" is marked "[to be confirmed by the owner]" and needs the owner's confirmation of the fact. (Resolved 2026-11-26, B4.)
- The author line "Mohamed Bechir Kefi" with no affiliation (decision C3) waits for the owner's tick on the second box. (Resolved 2026-11-26, B3; the box itself stays for the owner; see below.)
- The public repository URL and the demo URL are placeholders that only the owner can fill, at a release decision (G-PUBLIC). (Resolved 2026-11-26, B1 and B2; see below.)
- `date-released` was removed from `CITATION.cff` under owner-approvals-2026-11-25e, and re-adding it is part of the owner's publication step.
- In M6 the citing sentences for Such et al. (2017) and Cobbe et al. (2019) were updated after the free full texts were consulted (`research/literature_review.md`, M6 section), and the owner reviews the new wording.
- In M6 the PDF builder gained table layout rules and the supplementary S1 and S3 tables were restructured for readability with no number changed, and the owner reviews the PDFs.
- Any push, release, licence change or publication stays with the owner (G-PUBLIC); M6 prepared a release candidate and released nothing. (Update 2026-11-26: the repository is public since 2026-11-25; no release exists.)

### Remaining owner placeholders (updated 2026-11-26)

None. The placeholders listed at the M6 commit (repository URL in `CITATION.cff`, `README.md`, the articles, the demo footer and the manuscript; demo URL in `README.md`, the articles and the demo footer; funding and competing interests "[to be confirmed by the owner]" in the manuscript and `manuscript.tex`) were filled on 2026-11-26 from the owner's answers (section below). `git grep -n -i "placeholder\|to be confirmed"` outside the append-only logs finds only this file's own history.

## Owner answers recorded (2026-11-26)

Authority: owner, 2026-11-26, decision sheet (`labs/_shared/owner-decision-sheet-2026-11-26.md`, answers in `labs/_shared/owner-approvals-2026-11-26.md`). Applied in wording and configuration only (D-017); no result, figure, config, seed, frozen protocol or hash changed. No box above is ticked.

- **A1.** The repository is public at https://github.com/mohamedbechirkefi/evolve-artificial-life since 2026-11-25 (pushed by the coordinator). The out-of-date "nothing is published" sentences in `README.md` and `release_checklist.md` were corrected; dated entries in the append-only logs stay as written.
- **B1.** Repository URL filled in `CITATION.cff` (`repository-code`), `README.md`, the manuscript section 10 (and `manuscript.tex`), the articles and the demo footer.
- **B2.** Demo URL https://evolve-artificial-life.kefimohamedbechir.workers.dev filled in `README.md`, the articles and the demo footer; `demo/wrangler.jsonc` added (static assets from `./dist`, no Worker script); `demo/README.md` states the hosting (Cloudflare Workers static assets, free plan, deployed by the coordinator). Not deployed from this repository.
- **B3.** Author line "Mohamed Bechir Kefi, independent researcher" in the manuscript, the supplementary file, the three experiment reports (version 1.3, identification table only), `CITATION.cff` (`affiliation: "Independent researcher"`), `README.md`, the articles and the demo footer. This replaces the C3 form "no affiliation"; `research/freeze.json` keeps C3 as frozen text. `pyproject.toml` has no authors field.
- **B4.** Manuscript section 11: "Funding: No funding was received. Competing interests: The author declares no competing interests." The "[to be confirmed by the owner]" marks are removed.
- **B5.** The AI-use statement had been approved on 2026-11-25 (D-014); unchanged.
- **B6, B7.** The manuscript title is owner-approved as written; `CITATION.cff` already carries it.
- **B8.** `0.1.0-rc1` kept, no `date-released`; at the release the version becomes `0.1.0` and `date-released` the release day, `pyproject.toml` staying `0.0.0` (`release_checklist.md`).
- **B9.** Home paths removed from `CLAUDE.md`; what remains and why is listed in `reproducibility_report.md` section 7.
- **B10.** Committed PDFs stay and are attached to a release.
- **B11, B13.** Release notes (draft) in `release_checklist.md`: no small-label figure in this repository; build and check tools used but not redistributed.
- **B14.** Source-level labels accepted (1 read in full, 9 full texts consulted for the cited passage).
- **R-EVOLVE-1** (M6 citing sentences for Such et al. 2017 and Cobbe et al. 2019, and the restructured supplementary tables) belongs to the owner's full-text review (B16); not decided.

### Still open (owner only)

- B15: the article drafts (`articles/medium.md`, `articles/linkedin.md`) and their titles, before any posting.
- B16: the owner's full-text review of the manuscript, supplementary file and reports (including R-EVOLVE-1), then the sign-off of the boxes above.
- B18: the release (tag, GitHub release with the PDFs, optional zero-cost DOI or preprint), with the B8 version and date.
- Freezes: none pending in this repository (all three protocols were frozen before the confirmatory runs, D-010).
