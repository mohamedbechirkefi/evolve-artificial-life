<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# Owner review checklist (for the owner; not started)

- [ ] Protocols frozen and SHA-256 recorded in `research/decision_log.md`.
- [ ] Author and affiliation metadata approved. (Recorded decision, for the owner to confirm by ticking: 2026-11-24, common decision C3, "Mohamed Bechir Kefi", no affiliation; the AI is disclosed as a research and development assistant, not as an author. This box had been ticked by the AI assistant at commit fc69607 and was unticked in M5, D-015, because only the owner ticks these boxes.)
- [ ] AI-assistance disclosure reviewed (actual AI role and human verification performed). (Record: the owner approved the section 11 wording on 2026-11-25, D-014; the full-text review is M6.)
- [ ] Funding and competing-interest statements reviewed. (Record: wording approved by the owner on 2026-11-25, D-014; "none declared" still needs the owner's confirmation of the facts.)
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

- The manuscript title ("Evolutionary selection versus independent random search at equal evaluation budgets in a simulated foraging grid: a preregistered paired comparison with ablations and a sensitivity analysis") is not covered by the owner's title approval of 2026-11-25, which names other projects (D-015), so the owner approves or revises it.
- In M6 the `CITATION.cff` title was aligned with that manuscript title and the version set to `0.1.0-rc1`, so the owner confirms both or gives others.
- The funding statement "none declared" is marked "[to be confirmed by the owner]" and needs the owner's confirmation of the fact.
- The competing-interests statement "none declared" is marked "[to be confirmed by the owner]" and needs the owner's confirmation of the fact.
- The author line "Mohamed Bechir Kefi" with no affiliation (decision C3) waits for the owner's tick on the second box.
- The public repository URL and the demo URL are placeholders that only the owner can fill, at a release decision (G-PUBLIC).
- `date-released` was removed from `CITATION.cff` under owner-approvals-2026-11-25e, and re-adding it is part of the owner's publication step.
- In M6 the citing sentences for Such et al. (2017) and Cobbe et al. (2019) were updated after the free full texts were consulted (`research/literature_review.md`, M6 section), and the owner reviews the new wording.
- In M6 the PDF builder gained table layout rules and the supplementary S1 and S3 tables were restructured for readability with no number changed, and the owner reviews the PDFs.
- Any push, release, licence change or publication stays with the owner (G-PUBLIC); M6 prepared a release candidate and released nothing.

### Remaining owner placeholders (file and line, at the M6 commit)

- `CITATION.cff` line 4: repository-code placeholder.
- `README.md` line 47: demo URL placeholder.
- `README.md` line 74: repository URL placeholder.
- `articles/README.md` line 4: articles not published (publication placeholder).
- `articles/linkedin.md` line 14: repository and demo placeholders.
- `articles/medium.md` line 43: repository and demo placeholders.
- `demo/src/App.tsx` line 53: repository and demo URL placeholders (also in the built page).
- `research/paper/manuscript.md` line 245: public repository URL placeholder.
- `research/paper/manuscript.md` line 249: funding and competing interests "[to be confirmed by the owner]".
- `research/paper/manuscript.tex` lines 952, 958 and 959: the same three placeholders, generated from the manuscript.
