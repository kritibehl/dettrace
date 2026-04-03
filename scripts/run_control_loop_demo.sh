#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p build
cmake -S . -B build
cmake --build build

./build/dettrace_control_loop

echo
echo "=== Scenario comparison ==="
cat reports/control_scenario_comparison.json

echo
echo "=== Visual proof artifact ==="
ls -1 reports/control_debug_summary.svg

echo
echo "=== Per-scenario reports ==="
ls -1 reports/control_*_report.json reports/control_*_timing_budget.json 2>/dev/null || true
