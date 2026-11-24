# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Run-time provenance: git revision, versions, OS, CPU, runtime, peak memory."""

from __future__ import annotations

import datetime as _dt
import platform
import resource
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import ENGINE_VERSION

REPO_ROOT = Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@lru_cache(maxsize=1)
def git_state() -> tuple[str, bool | None]:
    """(revision, dirty). ('unknown', None) if git is unavailable."""
    try:
        rev = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--untracked-files=no"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout
        return rev, bool(status.strip())
    except (OSError, subprocess.SubprocessError):
        return "unknown", None


@lru_cache(maxsize=1)
def cpu_name() -> str:
    if sys.platform == "darwin":
        try:
            return subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True, check=True, timeout=10,
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return platform.processor() or "unknown"


def peak_rss_bytes() -> int | None:
    """Process high-water resident set size in bytes (ru_maxrss is bytes on macOS, KiB on Linux)."""
    try:
        r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (OSError, ValueError):
        return None
    return int(r if sys.platform == "darwin" else r * 1024)


def environment_info() -> dict:
    rev, dirty = git_state()
    return {
        "git_revision": rev,
        "git_dirty": dirty,
        "engine_version": ENGINE_VERSION,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "os": f"{platform.system()} {platform.release()} ({platform.platform()})",
        "machine": platform.machine(),
        "cpu": cpu_name(),
    }
