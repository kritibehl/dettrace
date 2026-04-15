#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "case_studies"
OUT.mkdir(parents=True, exist_ok=True)

start = datetime(2026, 4, 12, 12, 0, 0, tzinfo=timezone.utc)

def ts(offset: int) -> str:
    return (start + timedelta(seconds=offset)).isoformat()

race_condition = {
    "incident_name": "race-condition-bug",
    "source": "seed",
    "events": [
        {"service": "queue-service", "timestamp": ts(0), "trace_id": "baseline-1", "event_type": "dequeue", "message": "worker A dequeued task 1", "status": "ok", "latency_ms": 3},
        {"service": "queue-service", "timestamp": ts(1), "trace_id": "baseline-1", "event_type": "dequeue", "message": "worker B dequeued task 2", "status": "ok", "latency_ms": 4},
        {"service": "queue-service", "timestamp": ts(0), "trace_id": "candidate-1", "event_type": "dequeue", "message": "worker A dequeued task 1", "status": "ok", "latency_ms": 3},
        {"service": "queue-service", "timestamp": ts(1), "trace_id": "candidate-1", "event_type": "dequeue", "message": "worker B dequeued task 1", "status": "ok", "latency_ms": 4},
    ],
}

retry_storm = {
    "incident_name": "retry-storm-meltdown",
    "source": "seed",
    "events": [
        {"service": "api-gateway", "timestamp": ts(0), "trace_id": "retry-1", "event_type": "request", "message": "request enters gateway", "status": "ok", "latency_ms": 12, "upstream": "checkout-service"},
        {"service": "checkout-service", "timestamp": ts(1), "trace_id": "retry-1", "event_type": "dependency_retry", "message": "retrying payment", "status": "timeout", "latency_ms": 800, "upstream": "payment-service"},
        {"service": "checkout-service", "timestamp": ts(2), "trace_id": "retry-1", "event_type": "dependency_retry", "message": "retrying payment again", "status": "timeout", "latency_ms": 900, "upstream": "payment-service"},
        {"service": "checkout-service", "timestamp": ts(3), "trace_id": "retry-1", "event_type": "dependency_retry", "message": "retrying payment third time", "status": "timeout", "latency_ms": 950, "upstream": "payment-service"},
        {"service": "checkout-service", "timestamp": ts(4), "trace_id": "retry-1", "event_type": "dependency_retry", "message": "retrying payment fourth time", "status": "timeout", "latency_ms": 1100, "upstream": "payment-service"},
        {"service": "payment-service", "timestamp": ts(5), "trace_id": "retry-1", "event_type": "response", "message": "upstream overloaded", "status": "timeout", "latency_ms": 1300, "upstream": "db-service"},
    ],
}

cascading_failure = {
    "incident_name": "cascading-failure",
    "source": "seed",
    "events": [
        {"service": "frontend", "timestamp": ts(0), "trace_id": "cascade-1", "event_type": "request", "message": "user search request", "status": "ok", "latency_ms": 30, "upstream": "search-service"},
        {"service": "search-service", "timestamp": ts(1), "trace_id": "cascade-1", "event_type": "call", "message": "fanout to ranking", "status": "ok", "latency_ms": 60, "upstream": "ranking-service"},
        {"service": "ranking-service", "timestamp": ts(2), "trace_id": "cascade-1", "event_type": "call", "message": "downstream call stalled", "status": "timeout", "latency_ms": 1200, "upstream": "feature-store"},
        {"service": "feature-store", "timestamp": ts(3), "trace_id": "cascade-1", "event_type": "response", "message": "storage timeout", "status": "timeout", "latency_ms": 1600, "upstream": "storage"},
        {"service": "search-service", "timestamp": ts(4), "trace_id": "cascade-1", "event_type": "response", "message": "search timeout surfaced", "status": "timeout", "latency_ms": 1800, "upstream": "ranking-service"},
        {"service": "frontend", "timestamp": ts(5), "trace_id": "cascade-1", "event_type": "response", "message": "5xx returned to user", "status": "timeout", "latency_ms": 2000, "upstream": "search-service"},
    ],
}

for name, doc in {
    "race_condition_bug.json": race_condition,
    "retry_storm_meltdown.json": retry_storm,
    "cascading_failure.json": cascading_failure,
}.items():
    (OUT / name).write_text(json.dumps(doc, indent=2))

print("seeded case studies:")
for p in sorted(OUT.glob("*.json")):
    print(" -", p)
