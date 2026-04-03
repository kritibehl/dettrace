#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p build
cmake -S . -B build
cmake --build build

./build/dettrace_control_loop

echo
echo "=== Known-good control report ==="
cat reports/control_loop_known_good_report.json

echo
echo "=== Known-bad control report ==="
cat reports/control_loop_known_bad_report.json

echo
echo "=== Timing budget summary ==="
cat reports/control_timing_budget_summary.json

echo
echo "=== Trajectory artifacts ==="
ls -1 artifacts/control_known_good.jsonl artifacts/control_known_bad.jsonl artifacts/control_trajectory.csv artifacts/control_trajectory.svg
