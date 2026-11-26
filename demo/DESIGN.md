<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->
# EVOLVE demo: design plan

Owner request of 2026-11-26: each lab demo gets its own brand, motion and premium UI. This file is the plan written before the code, then reviewed against the frontend-design tells and the other demos' directions.

## Subject, audience, job

- **Subject.** Evolutionary selection versus independent random search at an equal budget of 2,000 policy evaluations, in a simulated 16 x 16 foraging grid (three preregistered experiments, 30 paired run seeds each).
- **Audience.** A curious technical reader, an admissions committee reading quickly, a researcher who wants the intervals and the protocol.
- **Primary job.** Answer the question in one sentence at the top, show the three findings on one shared axis, then let the visitor check the evidence: the replay of the committed runs, the sandbox, every registered contrast, the assumptions and the limitations.

## Direction: the petri dish and the field notebook

The study's world is a culture plate and a bench notebook. Organisms grow on a plate; a biologist keeps the plates of successive generations and writes on engineering paper. The page is a bench notebook page in pale green computation paper with a faint grid, blue-black ink, and an amber agar plate. The three search methods are three laboratory stains, which is how a microbiologist tells populations apart on a slide: crystal violet for EVO, safranin for RS, methylene blue for NOSEL.

## Colour (light only; a notebook page is paper)

| Name | Hex | Role |
|---|---|---|
| Computation paper | `#EDF1E8` | page background |
| Grid rule | `#CFDBC6` | notebook grid, hairlines |
| Blue-black ink | `#1C2738` | text, the mark |
| Agar | `#E6C466` | the plate in the hero, the replay cursor band |
| Crystal violet | `#5B2C83` | EVO, links, focus ring |
| Safranin | `#B0244E` | RS |

Supporting tokens: methylene blue `#1F5E9E` (NOSEL), a violet ramp for the mutation-strength sweep (sigma 0 `#9B84C2`, 0.02 `#7A55AE`, 0.1 = EVO, 0.5 `#2D1150`), result-kind colours kept semantic (supported `#2E6B3F`, contradicting `#A3321C`, inconclusive `#7A5D00`), plate surface `#F8FAF4`.

## Type

- **IM Fell English** (OFL 1.1), regular only (the italic was dropped to keep the page light): display face for the headline, section titles and the wordmark. It is a digitised 17th-century English type with inked, irregular edges, the voice of an old natural-history plate.
- **Alegreya Sans** (OFL 1.1), 400, 500 and 700: body, controls and figures. Humanist, warm, legible at small sizes; it has true lining tabular figures (`lnum`, `tnum`) for every number on the page.

Scale (Elements of Typographic Style, 1.25 ratio from an 18 px body): 14.4, 18, 22.5, 28, 35, 44, 55 px. Body line height 1.55, measure under 72 characters.

## Layout

Left-aligned throughout, a 12-column grid at 1200 px, one column below 760 px.

```
+--------------------------------------------------------------------+
| (mark) Evolve        Findings Replay Sandbox Results Method   bar  |  sticky, 56 px
+--------------------------------------------------------------------+
| A simulation study, preprint draft          .-------------.        |
|                                            /  plate gen 39 \       |
| Does selection beat random search          | .-----------. |       |
| at an equal budget, and how robust          \/ plate gen 9 \/      |
| is it?  (IM Fell, 55 px)                    | .---------. |        |
|                                              \ plate 0  /          |
| Answer sentence with 5.791 [4.644, 6.844]    '-------'             |
| author line                                Illustration, not data  |
+--------------------------------------------------------------------+
| Findings: one plate, one shared axis                               |
|  EXP-001 supported      |-----o-----|                    text     |
|  EXP-002 contradicting  |--o--|                          text     |
|  EXP-003 inconclusive        |--o--|                      text     |
|                      0 ... axis ...                                |
+--------------------------------------------------------------------+
| Replay (two curve charts, ancestry)   | Sandbox (stained slide)    |
| Results tables, assumptions, method, footer                         |
+--------------------------------------------------------------------+
```

The sandbox sits on a "slide": a dashed safranin-free border in methylene blue ink, so sandbox output never looks like a measured result.

## Motion

- **One orchestrated hero moment.** Three culture plates (generations 0, 9 and 39 of an illustrative run) slide into a fanned stack, 600 ms each, 160 ms apart, strong ease-out. Then the colonies on the top plate appear in order of founder, 40 ms stagger: many scattered founders on the first plate, a few dense lineages on the last, which is what selection does. Labelled "Illustration, not study data"; it shows no number.
- **Motion that answers actions.** Charts draw in once when scrolled into view (clip-path wipe, 700 ms). The navigation underline slides to the section being read. The sandbox result fades in when a run finishes. The replay generation cursor moves with the slider (no animation: it is triggered many times).
- **Reduced motion.** The plates and colonies appear in place with an opacity fade only; charts appear without the wipe; the underline jumps.
- **Hover** only inside `(hover: hover) and (pointer: fine)`: links thicken their underline; buttons darken. No `transition: all`.

## The one memorable thing

The stack of culture plates in the hero, where scattered founders on generation 0 become a few dominant lineages by generation 39. Everything around it stays quiet: paper, ink, one stain per method.

## Review against the tells and the other demos (revisions made)

1. *First draft:* warm cream paper with a deep green accent and an italic serif headline. That is the cream-plus-accent default. **Changed** to pale green computation paper (`#EDF1E8`) with a visible grid, and stains instead of a single accent.
2. *First draft:* three equal rounded result cards with a coloured top border. That is the SaaS-card kit. **Changed** to one plate with the three findings as rows on one shared axis, which is also the honest picture (they share a scale).
3. *First draft:* an all-caps tracked "KICKER" line above the headline and uppercase provenance labels. **Changed** to sentence-case labels set in Alegreya Sans 700 with a stain underline; no all-caps anywhere.
4. *First draft:* a monospace face for revisions and hashes. **Kept only for code paths and hashes**, which are code; data labels use Alegreya Sans tabular figures.
5. *Against the other demos:* MEMORY uses ink and pencil on index cards, STREAK a warm grade book, VIRAL a network map. EVOLVE is the only one on green computation paper with stains and round culture plates; its display face (IM Fell) is not used elsewhere. SWARM (the sibling of this session) is a dark dusk sky, so the two never meet.
6. *Removed accessory:* a decorative microscope-reticle overlay on the hero plate. It added noise without meaning.
