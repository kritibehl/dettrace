#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p build
cmake -S . -B build
cmake --build build

./build/dettrace_distributed

echo
echo "=== Sample OTEL input ==="
cat samples/otel_spans.jsonl

echo
echo "=== OTEL ingested annotated trace ==="
cat artifacts/otel_ingested_annotated.jsonl

echo
echo "=== Distributed incident report ==="
cat reports/distributed_incident_report.json

echo
echo "=== Distributed semantic diff ==="
cat reports/distributed_semantic_diff.json
