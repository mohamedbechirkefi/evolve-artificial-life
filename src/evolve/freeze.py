# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
"""Read-only check of the protocol freeze (gate G-FREEZE).

This module never freezes anything. An experiment counts as frozen only when
all of the following hold:

1. `research/experiment_registry.csv` holds, for the experiment, a 64-hex
   SHA-256 in `protocol_hash` equal to the hash of the protocol file on disk,
   and a status containing the word "frozen" (and not "awaiting").
2. The freeze record `research/freeze.json` (written once, after the owner's
   approval) has status "frozen", lists the experiment, and lists the main
   protocol `research/protocol.md`.
3. Every file listed in the record (main protocol, every confirmatory EXP
   protocol, every confirmatory config) still has its recorded SHA-256, and the
   experiment's protocol path and hash agree with the registry.

`check_config_frozen` further requires that the configuration actually being
run has the canonical config hash recorded for its experiment, so an edited
copy of a frozen config is refused wherever it is stored. Any edit to a frozen
file breaks a hash match, so confirmatory runs are refused again until the
owner records a dated amendment and a new freeze record.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from .manifest import REPO_ROOT

REGISTRY = Path("research/experiment_registry.csv")
FREEZE_RECORD = Path("research/freeze.json")
MAIN_PROTOCOL = "research/protocol.md"
_HEX64 = re.compile(r"[0-9a-f]{64}")


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_freeze_record(repo_root: str | Path = REPO_ROOT) -> tuple[dict | None, str]:
    """(record, reason). record is None when absent or malformed."""
    path = Path(repo_root) / FREEZE_RECORD
    if not path.is_file():
        return None, f"freeze record not found: {FREEZE_RECORD}"
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return None, f"freeze record is not valid JSON ({e})"
    if not isinstance(rec, dict) or rec.get("schema") != "evolve.freeze_record":
        return None, "freeze record has the wrong schema"
    if rec.get("status") != "frozen":
        return None, f"freeze record status is {rec.get('status')!r}, not 'frozen'"
    if not isinstance(rec.get("files"), dict) or not isinstance(rec.get("experiments"), dict):
        return None, "freeze record lacks 'files' or 'experiments'"
    return rec, "ok"


def _check_record_files(rec: dict, root: Path) -> tuple[bool, str]:
    files = rec["files"]
    if MAIN_PROTOCOL not in files:
        return False, f"freeze record does not hash the main protocol {MAIN_PROTOCOL}"
    for rel, h in sorted(files.items()):
        if not isinstance(h, str) or not _HEX64.fullmatch(h):
            return False, f"freeze record hash for {rel} is malformed"
        p = root / rel
        if not p.is_file():
            return False, f"frozen file missing: {rel}"
        actual = sha256_file(p)
        if actual != h:
            return False, f"frozen file {rel} changed: SHA-256 {actual} differs from the recorded {h}"
    return True, "ok"


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
    if not _HEX64.fullmatch(h):
        return False, f"{experiment_id}: no protocol hash recorded ({row.get('protocol_hash')!r})"
    if "frozen" not in status or "awaiting" in status:
        return False, f"{experiment_id}: registry status is {row.get('status')!r}, not frozen"
    proto_rel = (row.get("protocol_path") or "").strip()
    proto = root / proto_rel
    if not proto.is_file():
        return False, f"{experiment_id}: protocol file missing: {proto}"
    actual = sha256_file(proto)
    if actual != h:
        return False, f"{experiment_id}: protocol file hash {actual} differs from the registered hash {h}"

    rec, why = load_freeze_record(root)
    if rec is None:
        return False, f"{experiment_id}: {why}"
    ok, why = _check_record_files(rec, root)
    if not ok:
        return False, f"{experiment_id}: {why}"
    exp = rec["experiments"].get(experiment_id)
    if not isinstance(exp, dict):
        return False, f"{experiment_id}: not listed in the freeze record"
    if exp.get("protocol") != proto_rel or rec["files"].get(proto_rel) != h:
        return False, f"{experiment_id}: registry protocol path or hash disagrees with the freeze record"
    cfg_rel = exp.get("config")
    if not cfg_rel or cfg_rel not in rec["files"]:
        return False, f"{experiment_id}: freeze record does not hash the experiment config"
    return True, f"{experiment_id}: frozen, protocol SHA-256 {h}"


def check_config_frozen(cfg, repo_root: str | Path = REPO_ROOT) -> tuple[bool, str]:
    """(ok, reason): the parsed config equals the frozen config of its experiment."""
    from .config import config_hash

    frozen, reason = freeze_status(cfg.experiment_id, repo_root)
    if not frozen:
        return False, reason
    rec, _ = load_freeze_record(repo_root)
    expected = rec["experiments"][cfg.experiment_id].get("config_canonical_hash")
    actual = config_hash(cfg)
    if actual != expected:
        return False, (
            f"{cfg.experiment_id}: configuration differs from the frozen config "
            f"(canonical hash {actual}, frozen {expected})"
        )
    return True, f"{cfg.experiment_id}: frozen config, canonical hash {actual}"
