#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

RUNS="${1:-10}"
mkdir -p build artifacts/benchmarks

cmake -S . -B build
cmake --build build -j

CSV="artifacts/benchmarks/run_metrics.csv"
echo "run,expected_event_count,actual_event_count,replayed_event_count,first_divergence_index" > "$CSV"

for i in $(seq 1 "$RUNS"); do
  echo ">>> benchmark run $i/$RUNS"
  ./build/dettrace >/dev/null 2>&1 || true
  python3 scripts/collect_metrics.py > /tmp/dettrace_metrics.json
  python3 scripts/fingerprint_incident.py > /tmp/dettrace_fingerprint.json

  expected_count=$(python3 - <<'PY'
import json
print(json.load(open('/tmp/dettrace_metrics.json')).get('expected_event_count', 0))
PY
)

  actual_count=$(python3 - <<'PY'
import json
print(json.load(open('/tmp/dettrace_metrics.json')).get('actual_event_count', 0))
PY
)

  replayed_count=$(python3 - <<'PY'
import json
print(json.load(open('/tmp/dettrace_metrics.json')).get('replayed_event_count', 0))
PY
)

  first_div=$(python3 - <<'PY'
import json
v = json.load(open('/tmp/dettrace_metrics.json')).get('first_divergence_index')
print("" if v is None else v)
PY
)

  echo "$i,$expected_count,$actual_count,$replayed_count,$first_div" >> "$CSV"
done

python3 - <<'PY'
import csv, json
from pathlib import Path

csv_path = Path("artifacts/benchmarks/run_metrics.csv")
rows = list(csv.DictReader(csv_path.open()))
def nums(key):
    vals = []
    for r in rows:
        v = r.get(key, "")
        if v != "":
            vals.append(float(v))
    return vals

summary = {
    "total_runs": len(rows),
    "avg_expected_event_count": sum(nums("expected_event_count")) / max(len(nums("expected_event_count")), 1),
    "avg_actual_event_count": sum(nums("actual_event_count")) / max(len(nums("actual_event_count")), 1),
    "avg_replayed_event_count": sum(nums("replayed_event_count")) / max(len(nums("replayed_event_count")), 1),
    "avg_first_divergence_index": sum(nums("first_divergence_index")) / max(len(nums("first_divergence_index")), 1) if nums("first_divergence_index") else None,
}
Path("artifacts/benchmarks/benchmark_summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
PY

echo ""
echo "Saved:"
echo "  artifacts/benchmarks/run_metrics.csv"
echo "  artifacts/benchmarks/benchmark_summary.json"
