# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Export the published results for the M5 demo page (master prompt 11.5, 11.6 M5).

Reads committed results only (frozen analyses, summary tables, raw run files,
the committed exploratory pilot and M4 sensitivity files), the experiment
registry, the claims register, the artifact manifest and the manuscript. Runs
no simulation and changes no result.

Writes demo/public/data/results.json in the shared demo schema
(`lab-demo-results` 1.0.0) plus project keys:

  arm_means   per-arm mean F_test (and SD where the reports print it)
  curves      best-so-far training fitness, median and quartiles over run seeds
  replay      per-run traces for the replay: best-so-far per generation,
              training fitness of every evaluated policy and parent slots
              (ancestry), returned index and held-out F_test

Display strings are formatted exactly as the manuscript prints them;
tests/test_demo_export.py checks that each one appears verbatim there (or in
the named report, for the documented exceptions). No timestamps are written,
so the output is a deterministic function of the committed inputs.

Usage: .venv/bin/python scripts/export_demo_data.py [--check]
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "public" / "data" / "results.json"
CONF = ROOT / "results" / "confirmatory"
PILOT = ROOT / "results" / "exploratory" / "pilot-2026-11-24" / "report" / "contrasts_f_test.json"
SENS = ROOT / "results" / "exploratory" / "m4-sensitivity-2026-11-25" / "sensitivity.json"
MANUSCRIPT = ROOT / "research" / "paper" / "manuscript.md"
REGISTRY = ROOT / "research" / "experiment_registry.csv"
CLAIMS = ROOT / "research" / "claims_register.csv"
MANIFEST = ROOT / "research" / "publication" / "artifact_manifest.json"
EXPS = ("EXP-001", "EXP-002", "EXP-003")
B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
CI_LEVEL = 0.95
UNIT = "items per episode"


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


class Sources:
    """Collects every file read, with its SHA-256."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}

    def read_bytes(self, p: Path) -> bytes:
        b = p.read_bytes()
        self.files[rel(p)] = hashlib.sha256(b).hexdigest()
        return b

    def json(self, p: Path):
        return json.loads(self.read_bytes(p))

    def text(self, p: Path) -> str:
        return self.read_bytes(p).decode("utf-8")

    def csv(self, p: Path) -> list[dict]:
        return list(csv.DictReader(self.text(p).splitlines()))

    def listing(self) -> list[dict]:
        return [{"path": k, "sha256": v} for k, v in sorted(self.files.items())]


def f3(x: float) -> str:
    return f"{x:.3f}"


def iv(lo: float, hi: float) -> str:
    return f"[{lo:.3f}, {hi:.3f}]"


def find(contrasts: list[dict], condition: str, contrast: str, metric: str = "f_test") -> dict:
    hits = [c for c in contrasts if c["condition"] == condition and c["contrast"] == contrast and c["metric"] == metric]
    if len(hits) != 1:
        raise SystemExit(f"expected one contrast {condition} {contrast} {metric}, found {len(hits)}")
    return hits[0]


def est(c: dict, label: str, reading: str, kind: str, headline: bool = False, dz: bool = True) -> dict:
    """One estimate from a frozen-analysis contrast, formatted as the manuscript prints it."""
    return {
        "label": label,
        "estimate": c["mean_diff"],
        "ci_low": c["ci_low"],
        "ci_high": c["ci_high"],
        "ci_level": CI_LEVEL,
        "unit": UNIT,
        "display": f3(c["mean_diff"]),
        "interval_display": iv(c["ci_low"], c["ci_high"]),
        "n_pairs": c["n_pairs"],
        "dz_display": f"{c['dz']:.2f}" if dz else None,
        "seeds_display": f"{c['n_positive']} / {c['n_negative']}"
        + (f" / {c['n_zero']}" if c.get("n_zero") else ""),
        "reading": reading,
        "kind": kind,
        "headline": headline,
    }


def manuscript_limitations(text: str) -> list[str]:
    sec = text.split("# 7. Limitations and threats to validity", 1)[1].split("\n# ", 1)[0]
    items = [ln[2:].strip() for ln in sec.splitlines() if ln.startswith("- ")]
    if not items:
        raise SystemExit("no limitation bullets found in manuscript section 7")
    return [re.sub(r"\*\*(.+?)\*\*", r"\1", s) for s in items]


def claims_for(rows: list[dict], experiment_id: str) -> list[str]:
    out = []
    for r in rows:
        rid = r["result_id"]
        if experiment_id in rid or (experiment_id == "EXP-001" and rid.startswith("all EXP-001")):
            out.append(r["claim_id"])
        elif rid.startswith("all EXP-001 to EXP-003") or rid.startswith("EXP-001 to EXP-003"):
            out.append(r["claim_id"])
    return sorted(set(out))


def load_runs(src: Sources, exp: str) -> dict[tuple[str, str, int], dict]:
    runs = {}
    for p in sorted((CONF / exp / "runs").glob("*.json")):
        r = src.json(p)
        if r["status"] != "ok":
            raise SystemExit(f"{p}: status {r['status']}")
        runs[(r["condition"], r["arm"], int(r["run_seed"]))] = r
    return runs


def best_so_far(r: dict) -> np.ndarray:
    return np.maximum.accumulate(np.asarray(r["trace"]["train_fitness"], dtype=float))


def curve(runs: dict, condition: str, arm: str, points: int = 40) -> dict:
    seeds = sorted(s for (c, a, s) in runs if c == condition and a == arm)
    mat = np.stack([best_so_far(runs[(condition, arm, s)]) for s in seeds])
    e = mat.shape[1]
    idx = np.unique(np.linspace(0, e - 1, points + 1).round().astype(int))
    q25, med, q75 = np.percentile(mat[:, idx], [25, 50, 75], axis=0)
    r6 = lambda a: [round(float(x), 6) for x in a]  # noqa: E731
    return {"arm": arm, "n_seeds": len(seeds), "evaluation": [int(i) + 1 for i in idx], "median": r6(med), "q25": r6(q25), "q75": r6(q75)}


def encode_trace(r: dict, k: int, p: int) -> dict:
    tf = np.asarray(r["trace"]["train_fitness"], dtype=float)
    counts = np.rint(tf * k).astype(int)
    if not np.allclose(counts / k, tf, atol=1e-9) or counts.min() < 0 or counts.max() > 255:
        raise SystemExit(f"{r['run_id']}: training fitness is not a multiple of 1/K")
    pi = np.asarray(r["trace"]["parent_index"], dtype=int)
    e = tf.size
    slots = []
    for i in range(e):
        if pi[i] < 0:
            slots.append(".")
        else:
            g = i // p
            s = pi[i] - (g - 1) * p
            if not 0 <= s < p or s >= len(B64):
                raise SystemExit(f"{r['run_id']}: parent of {i} is not in the previous generation")
            slots.append(B64[s])
    bsf = np.maximum.accumulate(tf)
    return {
        "seed": int(r["run_seed"]),
        "run_id": r["run_id"],
        "returned_index": int(r["trace"]["returned_index"]),
        "f_test": r["metrics"]["f_test"],
        "best_per_generation": [round(float(bsf[(g + 1) * p - 1]), 6) for g in range(e // p)],
        "fitness_hex": "".join(f"{c:02x}" for c in counts),
        "parents_b64": "".join(slots),
    }


def build() -> dict:
    src = Sources()
    manuscript = src.text(MANUSCRIPT)
    registry = src.csv(REGISTRY)
    claims = src.csv(CLAIMS)
    manifest = src.json(MANIFEST)
    if not manifest.get("artifacts"):
        raise SystemExit("artifact manifest has no artifacts")
    reg = {r["experiment_id"]: r for r in registry}
    if set(reg) != set(EXPS):
        raise SystemExit(f"registry lists {sorted(reg)}, the exporter knows {EXPS}")

    an = {e: src.json(CONF / e / "analysis" / "analysis.json") for e in EXPS}
    summ = {e: src.csv(CONF / e / "report" / "summary.csv") for e in EXPS}
    revs = {rev for e in EXPS for rev in an[e]["run_revisions"]}
    if len(revs) != 1:
        raise SystemExit(f"results come from more than one revision: {revs}")
    code_revision = revs.pop()
    for e in EXPS:
        if an[e]["failed_runs"]:
            raise SystemExit(f"{e}: failed runs present")

    c1, c2, c3 = (an[e]["contrasts"] for e in EXPS)
    experiments = [
        {
            "id": "EXP-001",
            "title": reg["EXP-001"]["title"] + " (primary)",
            "status": "confirmatory, frozen protocol; 90 of 90 runs ok",
            "verdict": "H1 supported under the frozen rule",
            "estimates": [
                est(find(c1, "main", "EVO - RS"), "EVO - RS, F_test (registered primary)", "H1 supported (frozen rule)", "supported", headline=True),
                est(find(c1, "main", "EVO - NOSEL"), "EVO - NOSEL, F_test", "interval above 0 (secondary)", "estimate"),
                est(find(c1, "main", "NOSEL - RS"), "NOSEL - RS, F_test", "below 0, as predeclared", "as-predeclared"),
                est(find(c1, "main", "EVO - RS", "f_shift"), "EVO - RS, F_shift", "interval above 0 (descriptive)", "descriptive"),
                est(find(c1, "main", "EVO - RS", "generalisation_gap"), "EVO - RS, generalisation gap", "contains 0 (descriptive)", "descriptive"),
            ],
            "claim_ids": ["C-001", "C-002", "C-003", "C-011", "C-012", "C-013", "C-014", "C-016"],
            "report_path": reg["EXP-001"]["report_location"],
            "notes": [
                "EVO returned policies with higher held-out fitness than RS in 29 of 30 paired seeds.",
                "NOSEL was predeclared to score below RS (amendment C.3); it is a control for selection, not a competitor to RS.",
            ],
        },
        {
            "id": "EXP-002",
            "title": reg["EXP-002"]["title"],
            "status": "confirmatory, frozen protocol; 150 of 150 runs ok (60 bit-identical to EXP-001)",
            "verdict": "H1a and H1b supported (estimates); the frozen sigma 0.1 was not the best setting tested: a contradicting result under EXP-002's rule for the setting (owner, D-012); H1 of EXP-001 stands",
            "estimates": [
                est(find(c2, "main", "EVO - SELONLY"), "EVO - SELONLY, F_test (H1a)", "supported (estimate)", "supported"),
                est(find(c2, "main", "EVO - NOSEL"), "EVO - NOSEL, F_test (H1b)", "supported (estimate)", "supported"),
                est(find(c2, "main", "EVO - EVO-sigma0.02"), "EVO - EVO-sigma0.02, F_test (sweep)", "sigma 0.02 below 0.1", "estimate"),
                est(find(c2, "main", "EVO - EVO-sigma0.5"), "EVO - EVO-sigma0.5, F_test (sweep)", "contradicting result under EXP-002's rule", "contradicting", headline=True),
            ],
            "claim_ids": ["C-003", "C-004", "C-005", "C-006", "C-013", "C-014", "C-016"],
            "report_path": reg["EXP-002"]["report_location"],
            "notes": [
                "A negative value means sigma 0.5 scored higher than the frozen sigma 0.1: sigma 0.5 exceeded it by 1.776 items per episode.",
                "Owner decision of 2026-11-25 (D-012): a finding against EXP-002's assumption about the setting, under the contradicting-result rule; H1 of EXP-001 stands. The EXP-001 effect size is specific to sigma 0.1 and is not an upper bound.",
            ],
        },
        {
            "id": "EXP-003",
            "title": reg["EXP-003"]["title"] + " (sensitivity)",
            "status": "confirmatory, frozen protocol; 180 of 180 runs ok",
            "verdict": "robustness (positive in every condition) not supported and not contradicted: E500 and E8000 positive, K1 inconclusive",
            "estimates": [
                est(find(c3, "E500", "EVO - RS"), "E500: EVO - RS, F_test", "above 0", "supported", dz=False),
                est(find(c3, "E8000", "EVO - RS"), "E8000: EVO - RS, F_test", "above 0", "supported", dz=False),
                est(find(c3, "K1", "EVO - RS"), "K1: EVO - RS, F_test", "inconclusive (not equivalence)", "inconclusive", headline=True, dz=False),
                est(find(c3, "K1", "EVO - RS", "f_train_fixed"), "K1: EVO - RS, F_train_fixed", "above 0 (descriptive)", "descriptive", dz=False),
                est(find(c3, "K1", "EVO - RS", "overfit_drop"), "K1: EVO - RS, overfit_drop", "EVO overfits more (estimate)", "estimate", dz=False),
            ],
            "claim_ids": ["C-007", "C-008", "C-009", "C-010", "C-013", "C-014", "C-015", "C-016"],
            "report_path": reg["EXP-003"]["report_location"],
            "notes": [
                "With one fixed training environment, EVO's returned policies scored higher than RS's on that environment but not demonstrably on held-out environments, and lost more of their training score on the test set.",
                "Population size and generation count were scaled with the budget, so the larger difference at larger budgets is not an effect of the budget alone.",
                "Two returned policies, both from K1 seed 13, scored 0 on the test set.",
            ],
        },
    ]

    pilot = src.json(PILOT)
    pc = find(pilot, "main", "EVO - RS")
    experiments.append({
        "id": "J-0004",
        "title": "Exploratory pilot at full settings on the exploratory pool (10 seeds)",
        "status": "exploratory, before the freeze; separate test pool and run seeds",
        "verdict": "no verdict: exploratory, not under the frozen rule",
        "estimates": [{
            "label": "EVO - RS, F_test (pilot)",
            "estimate": pc["mean_diff"], "ci_low": pc["ci_low"], "ci_high": pc["ci_high"], "ci_level": CI_LEVEL, "unit": UNIT,
            "display": f3(pc["mean_diff"]), "interval_display": iv(pc["ci_low"], pc["ci_high"]),
            "n_pairs": pc["n_pairs"], "dz_display": None, "seeds_display": None,
            "reading": "exploratory direction seen before the freeze (disclosure C4)", "kind": "exploratory", "headline": False,
        }],
        "claim_ids": [],
        "report_path": "results/exploratory/pilot-2026-11-24/report/report.md",
        "notes": ["The pilot informed amendments C.1 to C.3; sigma was kept at 0.1 despite the pilot (C.4). The confirmatory pools and seeds were never used before the freeze."],
    })

    sens = src.json(SENS)
    by = {(c["experiment_id"], c["condition"], c["contrast"]): c for c in sens["contrast_checks"]}
    s05 = by[("EXP-002", "main", "EVO - EVO-sigma0.5")]
    sk1 = by[("EXP-003", "K1", "EVO - RS")]
    k13 = sens["k1_without_seed_13"]

    def sx(label: str, mean: float, lo: float, hi: float, level: float, n: int, reading: str) -> dict:
        return {
            "label": label, "estimate": mean, "ci_low": lo, "ci_high": hi, "ci_level": level, "unit": UNIT,
            "display": f3(mean), "interval_display": iv(lo, hi), "n_pairs": n, "dz_display": None, "seeds_display": None,
            "reading": reading, "kind": "exploratory", "headline": False,
        }

    experiments.append({
        "id": "J-0012",
        "title": "Exploratory re-analysis of the committed results (M4 sensitivity)",
        "status": "exploratory; re-analysis only, no simulation; never replaces a frozen verdict",
        "verdict": "no verdict: exploratory; no registered reading changed",
        "estimates": [
            sx("EVO - EVO-sigma0.5, Bonferroni-level interval", s05["mean_diff"], *s05["bonferroni_ci"], s05["bonferroni_level"], s05["n_pairs"], "reading unchanged"),
            sx("K1: EVO - RS, Bonferroni-level interval", sk1["mean_diff"], *sk1["bonferroni_ci"], sk1["bonferroni_level"], sk1["n_pairs"], "reading unchanged"),
            sx("K1: EVO - RS without seed 13", k13["mean_diff"], *k13["ci_95"], CI_LEVEL, k13["n_pairs"], "still inconclusive"),
        ],
        "claim_ids": ["C-017"],
        "report_path": "results/exploratory/m4-sensitivity-2026-11-25/sensitivity.json",
        "notes": ["Student t intervals agreed with the bootstrap readings in every case, and no leave-one-seed-out subset changed any reading."],
    })
    for e in experiments:
        for x in e["estimates"]:
            if x["display"] not in manuscript or x["interval_display"] not in manuscript:
                raise SystemExit(f"{e['id']} {x['label']}: display text not printed in the manuscript")
        for cid in e["claim_ids"]:
            if cid not in {r["claim_id"] for r in claims}:
                raise SystemExit(f"{e['id']}: unknown claim {cid}")

    # Arm means (C-016); SDs are printed in the experiment reports' TAB-1.
    arm_means = []
    order = {"EXP-001": [("main", a) for a in ("RS", "NOSEL", "EVO")],
             "EXP-002": [("main", a) for a in ("SELONLY", "EVO-sigma0.02", "EVO-sigma0.5")],
             "EXP-003": [(c, a) for c in ("E500", "E8000", "K1") for a in ("RS", "EVO")]}
    for e, keys in order.items():
        rows = {(r["condition"], r["arm"]): r for r in summ[e]}
        for cond, arm in keys:
            r = rows[(cond, arm)]
            mean, sd = float(r["f_test_mean"]), float(r["f_test_sd"])
            arm_means.append({
                "experiment_id": e, "condition": cond, "arm": arm, "n": int(r["n_ok"]),
                "mean": mean, "sd": sd, "display": f3(mean), "sd_display": f3(sd),
                "sd_source": reg[e]["report_location"],
            })

    runs1 = load_runs(src, "EXP-001")
    runs2 = load_runs(src, "EXP-002")
    runs3 = load_runs(src, "EXP-003")
    curves = []
    for e, runs, cond, arms, budget, pop, gens, k in (
        ("EXP-001", runs1, "main", ("RS", "NOSEL", "EVO"), 2000, 50, 40, 5),
        ("EXP-002", runs2, "main", ("SELONLY", "EVO-sigma0.02", "EVO", "EVO-sigma0.5"), 2000, 50, 40, 5),
        ("EXP-003", runs3, "E500", ("RS", "EVO"), 500, 25, 20, 5),
        ("EXP-003", runs3, "E8000", ("RS", "EVO"), 8000, 100, 80, 5),
        ("EXP-003", runs3, "K1", ("RS", "EVO"), 2000, 50, 40, 1),
    ):
        curves.append({"experiment_id": e, "condition": cond, "budget": budget, "population": pop, "generations": gens,
                       "train_episodes_per_eval": k, "arms": [curve(runs, cond, a) for a in arms]})

    replay_arms = []
    for arm, exp, runs in (("RS", "EXP-001", runs1), ("NOSEL", "EXP-001", runs1), ("EVO", "EXP-001", runs1),
                           ("SELONLY", "EXP-002", runs2), ("EVO-sigma0.5", "EXP-002", runs2)):
        seeds = sorted(s for (c, a, s) in runs if c == "main" and a == arm)
        replay_arms.append({"arm": arm, "experiment_id": exp,
                            "runs": [encode_trace(runs[("main", arm, s)], 5, 50) for s in seeds]})

    return {
        "schema": "lab-demo-results",
        "schema_version": "1.0.0",
        "project": "EVOLVE",
        "question": "Within a fixed budget of policy evaluations, does evolutionary selection with inherited, mutated policies find foraging policies with higher fitness on held-out grid environments than independent random search, and does any advantage survive changes in budget, mutation strength and training-set size?",
        "status_label": "Independent research manuscript / preprint draft, not peer-reviewed. Simulation study. Manuscript v1.0 (M4); the owner's full-text review is pending (M6).",
        "code_revision": code_revision,
        "sources": src.listing(),
        "experiments": experiments,
        "assumptions": [
            {"name": "Environment", "value": "16 x 16 toroidal grid, 24 food items clustered around 3 centres, episodes of T = 100 steps", "source": "manuscript section 3; experiments/configs/EXP-001.json"},
            {"name": "Policy", "value": "feed-forward network, 25 inputs, 8 tanh hidden units, 4 outputs, argmax action; 236 parameters drawn from N(0, 1)", "source": "manuscript section 3"},
            {"name": "Budget", "value": "E = 2,000 evaluations; one evaluation scores one policy on K = 5 training environments", "source": "manuscript sections 3 and 4.4"},
            {"name": "Held-out test set", "value": "M = 200 fixed environments from a pool disjoint from the training pool", "source": "manuscript section 3"},
            {"name": "EVO operators", "value": "population 50, 40 generations, truncation selection (top 10 parents), one elite, Gaussian mutation", "source": "manuscript section 4.3"},
            {"name": "Mutation strength (frozen primary setting)", "value": "sigma = 0.1. This assumption was challenged: sigma 0.5 scored higher in EXP-002 (owner, D-012)", "source": "manuscript sections 4.3 and 5.2; research/protocol.md amendment C.4"},
            {"name": "Seeds", "value": "30 paired run seeds per experiment; with 30 pairs a paired test at alpha 0.05 and 80 percent power detects about d_z = 0.53 (planning approximation)", "source": "manuscript section 4.6; protocol B.6"},
            {"name": "Decision rule (frozen)", "value": an["EXP-001"]["decision_rule"], "source": "results/confirmatory/EXP-001/analysis/analysis.json; manuscript section 4.7"},
            {"name": "Uncertainty", "value": "95 percent percentile bootstrap over run seeds, 10,000 resamples, analysis seed 0", "source": "manuscript section 4.7"},
        ],
        "limitations": manuscript_limitations(manuscript),
        "arm_means": arm_means,
        "curves": {
            "metric": "best-so-far training fitness (items per episode, mean over K training episodes); training signal, not held-out fitness",
            "summary": "median and interquartile range over the 30 run seeds",
            "items": curves,
        },
        "replay": {
            "condition": "main", "budget": 2000, "population": 50, "generations": 40, "train_episodes_per_eval": 5,
            "encoding": "fitness_hex: two hex digits per evaluation = training fitness x K (total items over K episodes); parents_b64: one character per evaluation, the parent's slot in the previous generation in the alphabet A-Z a-z 0-9 + /, '.' for none",
            "arms": replay_arms,
        },
    }


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=False) + "\n"


def main(argv: list[str]) -> int:
    text = render(build())
    if "--check" in argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("results.json is stale; rerun scripts/export_demo_data.py")
            return 1
        print("results.json up to date")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {rel(OUT)} ({len(text.encode())} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
