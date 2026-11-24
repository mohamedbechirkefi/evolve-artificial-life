# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Command line: smoke, run, report, test.

    python -m evolve smoke  [--config experiments/configs/smoke.json] [--out DIR] [--workers N] [--pdf]
    python -m evolve run    --config PATH [--out DIR] [--workers N]
    python -m evolve report --results DIR [--out DIR] [--pdf] [--project CONFIG ...]
    python -m evolve test   [pytest args]

`run` refuses a confirmatory config unless the protocol is frozen (G-FREEZE,
see evolve.freeze). Exploratory outputs go under results/exploratory/.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path

from .config import load_config
from .errors import EvolveError, ProtocolNotFrozenError
from .freeze import check_config_frozen
from .manifest import REPO_ROOT

EXIT_REFUSED = 3
DEFAULT_SMOKE = REPO_ROOT / "experiments" / "configs" / "smoke.json"


def _stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _default_out(cfg) -> Path:
    if cfg.label == "confirmatory":
        return REPO_ROOT / "results" / "confirmatory" / cfg.experiment_id
    return REPO_ROOT / "results" / "exploratory" / f"{cfg.experiment_id}-{_stamp()}"


def check_runnable(cfg, repo_root: Path = REPO_ROOT) -> None:
    """Raise ProtocolNotFrozenError for a confirmatory config whose protocol is not
    frozen, or whose content differs from the frozen config (research/freeze.json)."""
    if cfg.label != "confirmatory":
        return
    frozen, reason = check_config_frozen(cfg, repo_root)
    if not frozen:
        raise ProtocolNotFrozenError(
            f"refusing confirmatory run: {reason}. Freezing is the owner's decision (G-FREEZE)."
        )


def _run(cfg, out: Path | None, workers: int) -> Path:
    from .runner import run_matrix

    out = out or _default_out(cfg)
    if out.exists() and any((out / "runs").glob("*.json")):
        raise EvolveError(f"{out} already holds results; choose a new --out (raw results are never overwritten)")
    paths = run_matrix(cfg, out, workers=workers)
    print(f"{len(paths)} runs written to {out}")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="evolve", description="EVOLVE research CLI (simulations only)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sm = sub.add_parser("smoke", help="run the exploratory smoke matrix and its report")
    sm.add_argument("--config", type=Path, default=DEFAULT_SMOKE)
    sm.add_argument("--out", type=Path)
    sm.add_argument("--workers", type=int, default=1)
    sm.add_argument("--pdf", action="store_true")
    sm.add_argument("--project", type=Path, nargs="*", default=None,
                    help="planned configs for a runtime projection")

    rn = sub.add_parser("run", help="run a config (confirmatory configs require a frozen protocol)")
    rn.add_argument("--config", type=Path, required=True)
    rn.add_argument("--out", type=Path)
    rn.add_argument("--workers", type=int, default=1)

    rp = sub.add_parser("report", help="build tables, figures and a report from result files")
    rp.add_argument("--results", type=Path, required=True)
    rp.add_argument("--out", type=Path)
    rp.add_argument("--pdf", action="store_true")
    rp.add_argument("--project", type=Path, nargs="*", default=None)
    rp.add_argument("--title")

    ts = sub.add_parser("test", help="run the pytest suite")
    ts.add_argument("pytest_args", nargs=argparse.REMAINDER)

    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["test"]:  # pass every remaining argument through to pytest
        return subprocess.call([sys.executable, "-m", "pytest", *argv[1:]], cwd=REPO_ROOT)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "smoke":
            cfg = load_config(args.config)
            if cfg.label != "exploratory":
                raise EvolveError("smoke only runs exploratory configs")
            out = _run(cfg, args.out, args.workers)
            from .report import build_report

            build_report(out, pdf=args.pdf, planned_configs=args.project)
            print(f"report written to {out / 'report'}")
        elif args.cmd == "run":
            cfg = load_config(args.config)
            check_runnable(cfg)
            _run(cfg, args.out, args.workers)
        elif args.cmd == "report":
            from .report import build_report

            m = build_report(args.results, args.out, pdf=args.pdf, planned_configs=args.project, title=args.title)
            print(f"report written; {len(m['artifacts'])} artifacts" + (f"; pdf {m['pdf']}" if "pdf" in m else ""))
    except ProtocolNotFrozenError as e:
        print(str(e), file=sys.stderr)
        return EXIT_REFUSED
    except EvolveError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0
