#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

for f in case_studies/*.json; do
  echo ">>> ingesting $f"
  curl -s -X POST http://127.0.0.1:8010/ingest \
    -H "Content-Type: application/json" \
    --data @"$f" | python3 -m json.tool
done
