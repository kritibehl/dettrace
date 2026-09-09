#!/usr/bin/env bash

set +e

SCENARIO="$1"
ITERATIONS="${2:-40}"
WORKERS="${3:-5}"

DETTRACE="$HOME/dettrace"
DEMO="$HOME/opentelemetry-demo"

CAPTURE="$DETTRACE/examples/astronomy-shop/artifacts/capture.otlp.jsonl"
OUT="$DETTRACE/examples/astronomy-shop/artifacts/${SCENARIO}.otlp.jsonl"
WORKLOAD="$DETTRACE/examples/astronomy-shop/artifacts/workloads/${SCENARIO}.json"

mkdir -p \
  "$DETTRACE/examples/astronomy-shop/artifacts/workloads"

cd "$DEMO" || exit 1

docker stop load-generator \
  >/dev/null 2>&1 \
  || true

docker stop otel-collector \
  >/dev/null 2>&1 \
  || true

sleep 2

rm -f "$CAPTURE"
rm -f "$OUT"
rm -f "$WORKLOAD"

docker start otel-collector

if [ $? -ne 0 ]; then
  echo "COLLECTOR START: FAIL"
  exit 1
fi

sleep 5

STATE=$(
  docker inspect \
    otel-collector \
    --format '{{.State.Status}}'
)

echo "collector=$STATE"

if [ "$STATE" != "running" ]; then
  echo "COLLECTOR: FAIL"
  exit 1
fi

cd "$DETTRACE" || exit 1

echo
echo "===== APPLICATION READINESS ====="

python3 - <<'PYREADY'
import time
import urllib.request

url = "http://localhost:8080"

for attempt in range(45):
    try:
        with urllib.request.urlopen(
            url,
            timeout=3,
        ) as response:
            if 200 <= response.status < 400:
                print(
                    "APPLICATION READINESS: PASS"
                )
                raise SystemExit(0)
    except Exception:
        pass

    time.sleep(2)

raise SystemExit(
    "APPLICATION READINESS: FAIL"
)
PYREADY

if [ $? -ne 0 ]; then
  docker stop otel-collector >/dev/null 2>&1 || true
  exit 1
fi

echo
echo "===== DEPENDENCY READINESS ====="

for c in \
  currency \
  payment \
  email \
  product-catalog \
  checkout \
  frontend \
  frontend-proxy
do
  READY=0

  for attempt in $(seq 1 60)
  do
    HEALTH=$(
      docker inspect "$c" \
        --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' \
        2>/dev/null
    )

    echo "$c attempt=$attempt state=$HEALTH"

    if [ "$HEALTH" = "healthy" ] \
      || [ "$HEALTH" = "running" ]; then
      READY=1
      break
    fi

    sleep 2
  done

  if [ "$READY" -ne 1 ]; then
    echo "APPLICATION DEPENDENCY READINESS: FAIL"
    docker stop otel-collector >/dev/null 2>&1 || true
    exit 1
  fi
done

echo
echo "APPLICATION DEPENDENCY READINESS: PASS"

echo
echo "===== $SCENARIO WORKLOAD ====="

.venv/bin/python \
  examples/astronomy-shop/workloads/deterministic.py \
  --iterations "$ITERATIONS" \
  --workers "$WORKERS" \
  --output "$WORKLOAD"

WORKLOAD_STATUS=$?

if [ "$WORKLOAD_STATUS" -ne 0 ]; then
  echo "WORKLOAD: FAIL"
  docker stop otel-collector >/dev/null 2>&1
  exit "$WORKLOAD_STATUS"
fi

sleep 5

docker stop otel-collector

sleep 2

if [ ! -s "$CAPTURE" ]; then
  echo "TRACE CAPTURE: FAIL"
  exit 1
fi

mv \
  "$CAPTURE" \
  "$OUT"

.venv/bin/python - "$OUT" <<'PY'
import json
import sys
from pathlib import Path

path = Path(
    sys.argv[1]
)

lines = [
    line
    for line in path.read_text().splitlines()
    if line.strip()
]

if not lines:
    raise SystemExit(
        "empty OTLP artifact"
    )

for number, line in enumerate(
    lines,
    1,
):
    try:
        json.loads(line)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"invalid JSONL line "
            f"{number}: {exc}"
        )

print(
    "valid OTLP batches:",
    len(lines),
)

print(
    "artifact bytes:",
    path.stat().st_size,
)

print(
    "TRACE CAPTURE: PASS"
)
PY

if [ $? -ne 0 ]; then
  exit 1
fi

echo
echo "===== $SCENARIO COMPLETE ====="
echo "$OUT"
