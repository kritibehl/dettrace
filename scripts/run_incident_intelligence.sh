#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p build artifacts/benchmarks artifacts/history
cmake -S . -B build
cmake --build build -j

./build/dettrace || true
python3 scripts/collect_metrics.py
python3 scripts/fingerprint_incident.py
python3 scripts/predict_propagation.py
python3 scripts/find_similar_incidents.py
python3 scripts/save_incident_history.py

echo ""
echo "Saved intelligence artifacts:"
ls -1 artifacts/benchmarks || true
echo ""
echo "Saved history artifacts:"
ls -1 artifacts/history || true
