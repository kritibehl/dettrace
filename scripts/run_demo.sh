#!/usr/bin/env bash
set -euo pipefail

rm -rf build
cmake -S . -B build
cmake --build build

echo
echo "Running DetTrace demo..."
./build/dettrace || true

echo
echo "Generating divergence report..."
python3 scripts/generate_divergence_report.py

echo
echo "Artifacts present:"
ls -la artifacts || true

echo
echo "Preview expected trace:"
sed -n '1,20p' artifacts/expected.jsonl || true

echo
echo "Preview actual trace:"
sed -n '1,20p' artifacts/actual.jsonl || true

echo
echo "Preview replayed trace:"
sed -n '1,20p' artifacts/replayed.jsonl || true

echo
echo "Generated divergence report:"
cat reports/divergence_report.json || true
