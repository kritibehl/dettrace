#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p build artifacts/scenario_runs
cmake -S . -B build
cmake --build build -j

SCENARIOS=(
  timeout_chain
  retry_storm
  stale_state
  delayed_dependency
  duplicate_ack
  misordered_recovery
)

echo "=== DetTrace Scenario Runner ==="

for scenario in "${SCENARIOS[@]}"; do
  echo ""
  echo ">>> Running scenario: $scenario"
  ./build/dettrace || true

  OUT_DIR="artifacts/scenario_runs/$scenario"
  mkdir -p "$OUT_DIR"

  for f in artifacts/expected.jsonl artifacts/actual.jsonl artifacts/replayed.jsonl artifacts/divergence_report.json; do
    if [ -f "$f" ]; then
      cp "$f" "$OUT_DIR/$(basename "$f")"
    fi
  done

  if [ -f "artifacts/divergence_report.json" ]; then
    echo "Saved divergence artifact for $scenario -> $OUT_DIR/divergence_report.json"
  else
    echo "No divergence_report.json found for $scenario"
  fi
done

echo ""
echo "Scenario artifacts saved under artifacts/scenario_runs/"
