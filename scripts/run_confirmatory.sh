#!/bin/sh
# SPDX-License-Identifier: LicenseRef-EVOLVE-NC-Research-1.0
# Run one frozen confirmatory experiment through the run guard, at low priority,
# and record run-time provenance next to its raw results (M3 brief).
#   ./scripts/run_confirmatory.sh EXP-001 [workers]
# Writes results/confirmatory/EXP-NNN/{runs/, manifests/, config.json,
# matrix_manifest.json, run_provenance.json, run.log}. Never overwrites results:
# the CLI refuses an output folder that already holds run files.
set -u
exp="$1"
workers="${2:-2}"
here="$(cd "$(dirname "$0")/.." && pwd)"
cd "$here" || exit 2
out="results/confirmatory/$exp"
cfg="experiments/configs/$exp.json"
mkdir -p "$out"
rev="$(git rev-parse HEAD)"
dirty="$(git status --porcelain --untracked-files=no | wc -l | tr -d ' ')"
cfg_sha="$(shasum -a 256 "$cfg" | cut -d' ' -f1)"
data_sha="$(shasum -a 256 data/manifest.json | cut -d' ' -f1)"
freeze_sha="$(shasum -a 256 research/freeze.json | cut -d' ' -f1)"
cpu="$(sysctl -n machdep.cpu.brand_string 2>/dev/null || uname -m)"
start="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
load_start="$(uptime | sed 's/.*load averages*: //')"
PYTHONPATH="$here/src" nice -n 10 .venv/bin/python -m evolve run --config "$cfg" --out "$out" --workers "$workers" >"$out/run.log" 2>&1
status=$?
end="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
load_end="$(uptime | sed 's/.*load averages*: //')"
cat >"$out/run_provenance.json" <<EOF
{
 "schema": "evolve.run_provenance",
 "schema_version": "1.0.0",
 "experiment_id": "$exp",
 "command": "PYTHONPATH=src nice -n 10 .venv/bin/python -m evolve run --config $cfg --out $out --workers $workers",
 "git_revision": "$rev",
 "tracked_files_modified_at_start": $dirty,
 "config_path": "$cfg",
 "config_file_sha256": "$cfg_sha",
 "freeze_record_sha256": "$freeze_sha",
 "data_manifest_path": "data/manifest.json",
 "data_manifest_sha256": "$data_sha",
 "data_note": "synthetic environments generated from recorded seeds; no external data (D-002)",
 "hardware": "$cpu",
 "workers": $workers,
 "nice": 10,
 "load_average_start": "$load_start",
 "load_average_end": "$load_end",
 "started_utc": "$start",
 "finished_utc": "$end",
 "exit_status": $status
}
EOF
echo "$exp exit $status ($start to $end)"
exit $status
