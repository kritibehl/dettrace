#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p build
cmake -S . -B build
cmake --build build

./build/dettrace_incident_forensics

echo
echo "=== Incident cards ==="
cat artifacts/reports/incident_cards.md

echo
echo "=== Scenario summary ==="
cat artifacts/reports/scenario_summary.md

echo
echo "=== Cluster summary ==="
cat artifacts/reports/cluster_summary.json
