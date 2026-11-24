# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Read-only check of the protocol freeze (gate G-FREEZE).

This module never freezes anything. A protocol counts as frozen only when the
owner has written, in `research/experiment_registry.csv`, a 64-hex SHA-256 in
`protocol_hash` that equals the hash of the protocol file on disk, and a
status containing the word "frozen" (and not "awaiting"). Any edit to the
protocol after the freeze breaks the hash match, so confirmatory runs are
refused again until the owner records a dated amendment.
"""

from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

from .manifest import REPO_ROOT

REGISTRY = Path("research/experiment_registry.csv")


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def freeze_status(experiment_id: str, repo_root: str | Path = REPO_ROOT) -> tuple[bool, str]:
    """(frozen, reason)."""
    root = Path(repo_root)
    reg = root / REGISTRY
    if not reg.exists():
        return False, f"registry not found: {reg}"
    with reg.open(newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("experiment_id") == experiment_id]
    if len(rows) != 1:
        return False, f"{experiment_id}: expected one registry row, found {len(rows)}"
    row = rows[0]
    h = (row.get("protocol_hash") or "").strip().lower()
    status = (row.get("status") or "").lower()
    if not re.fullmatch(r"[0-9a-f]{64}", h):
        return False, f"{experiment_id}: no protocol hash recorded ({row.get('protocol_hash')!r})"
    if "frozen" not in status or "awaiting" in status:
        return False, f"{experiment_id}: registry status is {row.get('status')!r}, not frozen"
    proto = root / (row.get("protocol_path") or "")
    if not proto.is_file():
        return False, f"{experiment_id}: protocol file missing: {proto}"
    actual = sha256_file(proto)
    if actual != h:
        return False, f"{experiment_id}: protocol file hash {actual} differs from the registered hash {h}"
    return True, f"{experiment_id}: frozen, protocol SHA-256 {h}"
