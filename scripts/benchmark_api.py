#!/usr/bin/env python3
import json
import time
from pathlib import Path
from statistics import mean

from fastapi.testclient import TestClient
from dettrace_platform.app.main import app

client = TestClient(app)

payload = json.loads(Path("dettrace_platform/case_studies/otel/retry_storm_spans.json").read_text())

durations = []
runs = 25

for _ in range(runs):
    start = time.perf_counter()
    r = client.post("/ingest/otel", json={
        "incident_name": "benchmark-otel-retry-storm",
        "payload": payload
    })
    end = time.perf_counter()
    assert r.status_code == 200
    durations.append((end - start) * 1000)

report = {
    "runs": runs,
    "avg_ms": round(mean(durations), 3),
    "min_ms": round(min(durations), 3),
    "max_ms": round(max(durations), 3),
    "scenario": "OTEL retry-storm ingestion",
    "event_count_per_run": 5
}

Path("reports/benchmarks").mkdir(parents=True, exist_ok=True)
Path("reports/benchmarks/api_ingestion_benchmark.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
