# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Report generator: tables, figures and a Markdown report built only from
validated result files, plus a manifest mapping every table and figure to its
runs, metric, result paths, generator and config hashes (master prompt 11.5).

PDF output goes through pandoc (Markdown to Typst, with
`-V mainfont="Libertinus Serif"`) and the `typst` Python package (D-003).
"""

from __future__ import annotations

import csv
import json
import math
import os
import subprocess
from collections import defaultdict
from pathlib import Path

import numpy as np

from .config import load_config
from .errors import EvolveError, SchemaError
from .manifest import environment_info, utc_now
from .schema import load_result
from .stats import minimum_detectable_difference, paired_bootstrap, required_pairs, wilcoxon_signed_rank

GENERATOR = "src/evolve/report.py"
PANDOC = Path("/Users/bechir/research/labs/.tools/pandoc")
TYPST_PY = Path("/Users/bechir/research/labs/.tools/py/bin/python")

METRICS = [
    ("f_test", "held-out test fitness (items/episode)"),
    ("f_train_fresh", "fresh training fitness (items/episode)"),
    ("f_shift", "shifted-distribution fitness (items/episode)"),
    ("generalisation_gap", "F_train_fresh - F_test (items/episode)"),
    ("adaptation_auc", "adaptation AUC (items/episode)"),
    ("best_train_fitness", "training fitness of returned policy (items/episode)"),
    ("genotypic_diversity", "genotypic diversity (parameter units)"),
    ("behavioural_diversity", "behavioural diversity (fraction of steps)"),
]


def load_results(results_dir: str | Path) -> list[dict]:
    """Load and validate every run file. Any invalid file aborts the report (fail closed)."""
    run_dir = Path(results_dir) / "runs"
    files = sorted(run_dir.glob("*.json"))
    if not files:
        raise EvolveError(f"no result files in {run_dir}")
    docs = []
    for f in files:
        try:
            doc = load_result(f)
        except SchemaError as e:
            raise SchemaError(f"{f}: {e}") from e
        doc["_path"] = str(f)
        docs.append(doc)
    return docs


def _fmt(x: float, nd: int = 3) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "n/a"
    return f"{x:.{nd}f}"


def metrics_rows(docs: list[dict]) -> list[dict]:
    rows = []
    for d in docs:
        m = d["metrics"] or {}
        ex = m.get("exploit", {})
        row = {
            "run_id": d["run_id"], "label": d["label"], "experiment_id": d["experiment_id"],
            "condition": d["condition"], "arm": d["arm"], "run_seed": d["run_seed"], "status": d["status"],
        }
        for k, _ in METRICS:
            row[k] = m.get(k)
        row.update({
            "n_evaluations": m.get("n_evaluations"),
            "stay_fraction": ex.get("stay_fraction"), "turn_fraction": ex.get("turn_fraction"),
            "forward_fraction": ex.get("forward_fraction"), "replay_check_passed": ex.get("replay_check_passed"),
            "wall_seconds": d["manifest"]["wall_seconds"], "peak_rss_bytes": d["manifest"]["peak_rss_bytes"],
            "attempts": d["manifest"]["attempts"], "config_hash": d["config_hash"],
            "git_revision": d["manifest"]["git_revision"], "git_dirty": d["manifest"]["git_dirty"],
            "result_path": d["_path"],
        })
        rows.append(row)
    return rows


def _write_csv(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def summary_rows(docs: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for d in docs:
        groups[(d["condition"], d["arm"])].append(d)
    out = []
    for (cond, arm), ds in groups.items():
        ok = [d for d in ds if d["status"] == "ok"]
        row = {"condition": cond, "arm": arm, "n_ok": len(ok), "n_failed": len(ds) - len(ok)}
        for k, _ in METRICS:
            v = np.array([d["metrics"][k] for d in ok], dtype=float)
            row[f"{k}_mean"] = float(v.mean()) if v.size else None
            row[f"{k}_sd"] = float(v.std(ddof=1)) if v.size > 1 else None
            row[f"{k}_min"] = float(v.min()) if v.size else None
            row[f"{k}_max"] = float(v.max()) if v.size else None
        st = np.array([d["metrics"]["exploit"]["stay_fraction"] for d in ok], dtype=float)
        w = np.array([d["manifest"]["wall_seconds"] for d in ds], dtype=float)
        row["stay_fraction_mean"] = float(st.mean()) if st.size else None
        row["wall_seconds_mean"] = float(w.mean())
        row["wall_seconds_max"] = float(w.max())
        out.append(row)
    return out


def default_contrasts(arms: list[str]) -> list[tuple[str, str]]:
    """Every arm minus the first arm (the baseline), and EVO minus every other arm."""
    base = arms[0]
    pairs = [(a, base) for a in arms[1:]]
    if "EVO" in arms:
        pairs += [("EVO", a) for a in arms if a not in ("EVO", base)]
    return pairs


def contrast_rows(docs: list[dict], metric: str, resamples: int, seed: int) -> list[dict]:
    by_cond: dict[str, dict[str, dict[int, float]]] = defaultdict(lambda: defaultdict(dict))
    arm_order: dict[str, list[str]] = defaultdict(list)
    for d in docs:
        if d["arm"] not in arm_order[d["condition"]]:
            arm_order[d["condition"]].append(d["arm"])
        if d["status"] == "ok":
            by_cond[d["condition"]][d["arm"]][d["run_seed"]] = d["metrics"][metric]
    out = []
    for cond, arms in arm_order.items():
        arms_sorted = sorted(arms, key=lambda a: (a != "RS", a))
        for a, b in default_contrasts(arms_sorted):
            common = sorted(set(by_cond[cond][a]) & set(by_cond[cond][b]))
            row = {"condition": cond, "contrast": f"{a} - {b}", "metric": metric, "n_pairs": len(common),
                   "seeds": common}
            if len(common) >= 2:
                diffs = np.array([by_cond[cond][a][s] - by_cond[cond][b][s] for s in common])
                est = paired_bootstrap(diffs, resamples=resamples, seed=seed)
                wx = wilcoxon_signed_rank(diffs)
                row.update({
                    "mean_diff": est.mean, "ci_low": est.ci_low, "ci_high": est.ci_high, "sd_diff": est.sd,
                    "dz": est.dz, "dz_ci_low": est.dz_ci_low, "dz_ci_high": est.dz_ci_high,
                    "wilcoxon_p": wx.p_two_sided, "mde_at_n": minimum_detectable_difference(est.sd, len(common)),
                    "mde_at_20": minimum_detectable_difference(est.sd, 20), "mde_at_30": minimum_detectable_difference(est.sd, 30),
                    "diffs": [float(x) for x in diffs],
                })
            out.append(row)
    return out


def _figures(docs: list[dict], fig_dir: Path, prefix: str) -> list[dict]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_dir.mkdir(parents=True, exist_ok=True)
    conds = sorted({d["condition"] for d in docs})
    ok = [d for d in docs if d["status"] == "ok"]
    figs = []

    # FIG-1: per-seed held-out test fitness by arm and condition.
    widths = [max(2, len({d["arm"] for d in ok if d["condition"] == c})) for c in conds]
    fig, axes = plt.subplots(1, len(conds), figsize=(1.3 * sum(widths) + 1.5, 4.2), squeeze=False,
                             gridspec_kw={"width_ratios": widths})
    for ax, cond in zip(axes[0], conds):
        ds = [d for d in ok if d["condition"] == cond]
        arms = sorted({d["arm"] for d in ds}, key=lambda a: (a != "RS", a))
        for i, arm in enumerate(arms):
            v = [d["metrics"]["f_test"] for d in ds if d["arm"] == arm]
            jitter = np.linspace(-0.12, 0.12, len(v)) if len(v) > 1 else [0.0]
            ax.scatter(np.full(len(v), i) + jitter, v, s=18, color="0.25", zorder=3)
            ax.hlines(np.mean(v), i - 0.25, i + 0.25, color="tab:red", lw=2, zorder=4)
        ax.set_xticks(range(len(arms)), arms, rotation=30, ha="right", fontsize=8)
        ax.set_xlim(-0.6, len(arms) - 0.4)
        ax.set_title(f"condition: {cond}", fontsize=10)
        ax.set_ylabel("F_test (food items per episode)")
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle(f"{prefix}: held-out test fitness per run seed (red bar: mean)", fontsize=10)
    fig.tight_layout()
    p1 = fig_dir / "FIG-1_f_test_by_arm.png"
    fig.savefig(p1, dpi=150)
    fig.savefig(p1.with_suffix(".svg"))
    plt.close(fig)
    figs.append({
        "fig_id": "FIG-1", "path": p1.name, "metric": "f_test",
        "caption": "Held-out test fitness of the returned policy, one point per run seed, per arm and condition. Red bar: mean over seeds. Unit: food items per episode.",
        "alt": "Strip plot of held-out test fitness per run seed for each search arm, one panel per condition.",
        "run_ids": sorted(d["run_id"] for d in ok),
    })

    # FIG-2: best-so-far training fitness against evaluations.
    fig, axes = plt.subplots(1, len(conds), figsize=(4.2 * len(conds), 3.6), squeeze=False)
    colours = {"RS": "tab:gray", "NOSEL": "tab:blue", "EVO": "tab:red", "SELONLY": "tab:green"}
    for ax, cond in zip(axes[0], conds):
        ds = [d for d in ok if d["condition"] == cond]
        arms = sorted({d["arm"] for d in ds}, key=lambda a: (a != "RS", a))
        for arm in arms:
            curves = np.array([np.maximum.accumulate(d["trace"]["train_fitness"]) for d in ds if d["arm"] == arm])
            x = np.arange(1, curves.shape[1] + 1)
            c = colours.get(arm)
            for cur in curves:
                ax.plot(x, cur, color=c, alpha=0.15, lw=0.7)
            ax.plot(x, curves.mean(axis=0), color=c, lw=1.8, label=f"{arm} (n={len(curves)})")
        ax.set_xlabel("evaluations")
        ax.set_ylabel("best-so-far F_train (items/episode)")
        ax.set_title(f"condition: {cond}", fontsize=10)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    fig.suptitle(f"{prefix}: adaptation curves (thin: seeds, thick: mean)", fontsize=10)
    fig.tight_layout()
    p2 = fig_dir / "FIG-2_adaptation.png"
    fig.savefig(p2, dpi=150)
    fig.savefig(p2.with_suffix(".svg"))
    plt.close(fig)
    figs.append({
        "fig_id": "FIG-2", "path": p2.name, "metric": "best-so-far training fitness",
        "caption": "Best-so-far training fitness (mean of K training episodes) against the number of evaluations. Thin lines: individual run seeds; thick lines: mean over seeds. Training fitness of the best of many noisy evaluations is biased upwards (winner's curse); held-out fitness is in FIG-1.",
        "alt": "Line chart of best-so-far training fitness against evaluations for each arm.",
        "run_ids": sorted(d["run_id"] for d in ok),
    })
    return figs


def _md_table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines)


def runtime_projection(docs: list[dict], planned_configs: list[str | Path]) -> dict:
    """Project wall-clock time of planned configs from measured seconds per evaluation.

    Assumption (stated in the output): runtime scales linearly with the number of
    evaluations of an arm kind; fixed per-run scoring cost is included in the
    measured per-evaluation rate. Measured runs with the largest budget are used.
    """
    ok = [d for d in docs if d["status"] == "ok"]
    rate: dict[str, list[float]] = defaultdict(list)
    max_e = max(d["metrics"]["n_evaluations"] for d in ok)
    for d in ok:
        if d["metrics"]["n_evaluations"] == max_e:
            rate[d["config"]["arm"]["kind"]].append(d["manifest"]["wall_seconds"] / max_e)
    rates = {k: float(np.median(v)) for k, v in rate.items()}
    plan = []
    total = 0.0
    total_runs = 0
    for p in planned_configs:
        cfg = load_config(p)
        secs = 0.0
        runs = 0
        for c in cfg.conditions:
            for a in c.arms:
                r = rates.get(a.kind, max(rates.values()))
                secs += r * a.total_evaluations * len(cfg.run_seeds)
                runs += len(cfg.run_seeds)
        plan.append({"config": str(p), "experiment_id": cfg.experiment_id, "runs": runs, "serial_seconds": secs})
        total += secs
        total_runs += runs
    return {
        "seconds_per_evaluation": rates, "measured_at_evaluations": max_e,
        "plan": plan, "total_runs": total_runs, "total_serial_seconds": total,
        "assumption": "linear in evaluations per arm kind, median rate of the measured runs with the largest budget; serial, one core",
    }


def build_report(results_dir: str | Path, out_dir: str | Path | None = None, pdf: bool = False,
                 planned_configs: list[str | Path] | None = None, title: str | None = None) -> dict:
    results_dir = Path(results_dir)
    out = Path(out_dir) if out_dir else results_dir / "report"
    out.mkdir(parents=True, exist_ok=True)
    docs = load_results(results_dir)
    labels = {d["label"] for d in docs}
    exps = sorted({d["experiment_id"] for d in docs})
    exploratory = "exploratory" in labels
    prefix = ", ".join(exps)
    cfg_path = results_dir / "config.json"
    cfg_raw = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    resamples = int(cfg_raw.get("bootstrap_resamples", 10_000))
    aseed = int(cfg_raw.get("analysis_seed", 0))

    rows = metrics_rows(docs)
    _write_csv(rows, out / "metrics.csv")
    summ = summary_rows(docs)
    _write_csv(summ, out / "summary.csv")
    contrasts = contrast_rows(docs, "f_test", resamples, aseed)
    (out / "contrasts_f_test.json").write_text(json.dumps(contrasts, indent=1) + "\n", encoding="utf-8")
    figs = _figures(docs, out / "figures", prefix)
    projection = runtime_projection(docs, planned_configs) if planned_configs else None

    banner = (
        "**EXPLORATORY. NOT A FINDING.** These runs were executed before the protocol freeze, on the "
        "exploratory test pool and exploratory run seeds. They exist to measure runtime, seed spread and "
        "degenerate cases for planning. They must not be cited as evidence or pooled with confirmatory runs."
        if exploratory else "Confirmatory runs under a frozen protocol."
    )
    md = [
        "<!-- SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0 -->",
        f"# {title or 'EVOLVE run report: ' + prefix}",
        "",
        f"Generated {utc_now()} by `{GENERATOR}` from `{results_dir}`. Label(s): {', '.join(sorted(labels))}. "
        "All results are simulations of a synthetic grid world.",
        "",
        banner,
        "",
        "## Runs",
        "",
        f"{len(docs)} runs ({sum(d['status'] == 'ok' for d in docs)} ok, {sum(d['status'] == 'failed' for d in docs)} failed). "
        f"Code revision(s): {', '.join(sorted({d['manifest']['git_revision'][:12] + (' (dirty)' if d['manifest']['git_dirty'] else '') for d in docs}))}.",
        "",
        "## TAB-1. Summary by condition and arm",
        "",
        _md_table(
            ["condition", "arm", "n ok", "n failed", "F_test mean (sd)", "F_test min to max", "F_train_fresh mean",
             "F_shift mean", "gap mean", "AUC mean", "geno div", "behav div", "stay frac", "s/run mean"],
            [[r["condition"], r["arm"], str(r["n_ok"]), str(r["n_failed"]),
              f"{_fmt(r['f_test_mean'])} ({_fmt(r['f_test_sd'])})", f"{_fmt(r['f_test_min'])} to {_fmt(r['f_test_max'])}",
              _fmt(r["f_train_fresh_mean"]), _fmt(r["f_shift_mean"]), _fmt(r["generalisation_gap_mean"]),
              _fmt(r["adaptation_auc_mean"]), _fmt(r["genotypic_diversity_mean"], 2), _fmt(r["behavioural_diversity_mean"]),
              _fmt(r["stay_fraction_mean"]), _fmt(r["wall_seconds_mean"], 2)] for r in summ],
        ),
        "",
        "Units: fitness in food items per episode; gap = F_train_fresh - F_test; s/run = wall-clock seconds.",
        "",
        "## TAB-2. Paired contrasts on F_test (unit: run seed)",
        "",
        "Mean paired difference with a 95 percent percentile bootstrap interval over run seeds "
        f"({resamples} resamples, analysis seed {aseed}); d_z = mean / SD of the differences; Wilcoxon signed-rank "
        "(normal approximation) as a robustness check. MDE = normal-approximation minimum detectable mean "
        "difference at 80 percent power and two-sided alpha 0.05, using the observed SD of differences.",
        "",
        _md_table(
            ["condition", "contrast", "n pairs", "mean diff", "95% CI", "SD diff", "d_z", "Wilcoxon p", "MDE n", "MDE 20", "MDE 30"],
            [[c["condition"], c["contrast"], str(c["n_pairs"]), _fmt(c.get("mean_diff")),
              f"[{_fmt(c.get('ci_low'))}, {_fmt(c.get('ci_high'))}]", _fmt(c.get("sd_diff")), _fmt(c.get("dz"), 2),
              _fmt(c.get("wilcoxon_p"), 4), _fmt(c.get("mde_at_n")), _fmt(c.get("mde_at_20")), _fmt(c.get("mde_at_30"))]
             for c in contrasts],
        ),
        "",
    ]
    if exploratory:
        md += ["In exploratory reports these intervals describe planning quantities (seed spread) only. "
               "They are not tests of the registered hypotheses.", ""]
    for f in figs:
        md += [f"## {f['fig_id']}", "", f"![{f['alt']}](figures/{f['path']})", "", f"*{f['fig_id']}.* {f['caption']}", ""]
    if projection:
        md += ["## Runtime projection for the planned matrix", "",
               f"Assumption: {projection['assumption']}. Measured at E = {projection['measured_at_evaluations']}: "
               + ", ".join(f"{k} {v * 1000:.3f} ms per evaluation" for k, v in projection["seconds_per_evaluation"].items()) + ".", "",
               _md_table(["config", "experiment", "runs", "serial hours"],
                         [[p["config"], p["experiment_id"], str(p["runs"]), _fmt(p["serial_seconds"] / 3600, 2)] for p in projection["plan"]]),
               "", f"Total: {projection['total_runs']} runs, {_fmt(projection['total_serial_seconds'] / 3600, 2)} serial hours "
               f"({_fmt(projection['total_serial_seconds'] / 3600 / 8, 2)} hours on 8 workers if scaling were perfect).", ""]
    failed = [d for d in docs if d["status"] == "failed"]
    md += ["## Failures", ""]
    md += [f"- `{d['run_id']}`: {d['failure'].splitlines()[0]}" for d in failed] or ["None."]
    md += ["", "## Degenerate-case checks", ""]
    zero = [d["run_id"] for d in docs if d["status"] == "ok" and d["metrics"]["f_test"] == 0]
    stay_heavy = [d["run_id"] for d in docs if d["status"] == "ok" and d["metrics"]["exploit"]["stay_fraction"] > 0.5]
    n_food = cfg_raw.get("env", {}).get("n_food", 24)
    ceiling = [d["run_id"] for d in docs if d["status"] == "ok" and d["metrics"]["best_train_fitness"] >= n_food]
    collapsed = [d["run_id"] for d in docs if d["status"] == "ok" and d["metrics"]["behavioural_diversity"] == 0]
    md += [
        f"- Returned policies with F_test = 0: {len(zero)} {zero[:10]}",
        f"- Returned policies with stay fraction above 0.5 on the test set: {len(stay_heavy)} {stay_heavy[:10]}",
        f"- Runs whose best training fitness reached the ceiling ({n_food} items): {len(ceiling)} {ceiling[:10]}",
        f"- Final populations with zero behavioural diversity: {len(collapsed)} {collapsed[:10]}",
        "- Replay check (consumed items equal the decrease of food on the grid): enforced in every simulated episode; a violation aborts the run.",
        "",
    ]
    report_md = out / "report.md"
    report_md.write_text("\n".join(md), encoding="utf-8")

    env = environment_info()
    manifest = {
        "schema": "evolve.report_manifest", "schema_version": "1.0.0", "generated_utc": utc_now(),
        "generator": GENERATOR, "results_dir": str(results_dir), "labels": sorted(labels),
        "code_revision_report": env["git_revision"], "code_revision_runs": sorted({d["manifest"]["git_revision"] for d in docs}),
        "config_hashes": sorted({d["config_hash"] for d in docs}),
        "artifacts": [
            {"id": "TAB-1", "path": "summary.csv", "metric": "all METRICS, mean/sd/min/max per condition x arm",
             "run_ids": sorted(d["run_id"] for d in docs)},
            {"id": "TAB-2", "path": "contrasts_f_test.json", "metric": "f_test paired differences",
             "run_ids": sorted(d["run_id"] for d in docs if d["status"] == "ok")},
            {"id": "metrics", "path": "metrics.csv", "metric": "per-run metrics", "run_ids": sorted(d["run_id"] for d in docs)},
        ] + [{"id": f["fig_id"], "path": f"figures/{f['path']}", "metric": f["metric"], "run_ids": f["run_ids"],
              "caption": f["caption"], "alt": f["alt"]} for f in figs],
        "result_paths": sorted(d["_path"] for d in docs),
        "runtime_projection": projection,
    }
    if pdf:
        manifest["pdf"] = str(build_pdf(report_md))
    (out / "report_manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return manifest


def build_pdf(md_path: Path) -> Path:
    """pandoc Markdown -> Typst -> PDF (typst Python package). Raises on failure."""
    md_path = Path(md_path)
    if not PANDOC.exists() or not TYPST_PY.exists():
        raise EvolveError("pandoc or the typst Python environment is not available")
    typ = md_path.with_suffix(".typ")
    pdf = md_path.with_suffix(".pdf")
    subprocess.run([str(PANDOC), md_path.name, "-f", "markdown", "-t", "typst", "-s",
                    "-V", "mainfont=Libertinus Serif", "-o", typ.name], cwd=md_path.parent, check=True)
    code = "import sys, typst; typst.compile(sys.argv[1], output=sys.argv[2], root=sys.argv[3])"
    subprocess.run([str(TYPST_PY), "-c", code, str(typ), str(pdf), str(md_path.parent)], check=True,
                   env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"})
    if not pdf.exists() or pdf.stat().st_size == 0:
        raise EvolveError("PDF was not produced")
    return pdf


__all__ = ["build_report", "build_pdf", "load_results", "runtime_projection"]
