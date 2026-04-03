#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p build
cmake -S . -B build
cmake --build build

./build/dettrace_control_loop

echo
echo "=== Control loop divergence report ==="
cat reports/control_loop_divergence_report.json

echo
echo "=== Expected trajectory preview ==="
head -n 10 artifacts/control_expected.jsonl || true

echo
echo "=== Actual trajectory preview ==="
head -n 10 artifacts/control_actual.jsonl || true
