#!/usr/bin/env python3
import json
from pathlib import Path

DIV = Path("artifacts/divergence_report.json")
OUT = Path("artifacts/benchmarks/propagation_prediction.json")

if not DIV.exists():
    print("No divergence_report.json found")
    raise SystemExit(0)

data = json.loads(DIV.read_text())

expected = str(data.get("expected_event", "")).lower()
actual = str(data.get("actual_event", "")).lower()
div_type = str(data.get("divergence_type", "")).lower()

signals = [expected, actual, div_type]

downstream = []
risk = "medium"

blob = " ".join(signals)

if "timeout" in blob:
    downstream += ["retry_amplification", "dependency_backpressure", "operator_visible_latency"]
    risk = "high"

if "retry" in blob:
    downstream += ["queue_pressure", "duplicate_work_risk", "tail_latency_growth"]
    risk = "high"

if "task" in blob or "dequeue" in blob:
    downstream += ["work_distribution_skew", "missed_or_duplicate_processing"]

if "recovery" in blob or "failover" in blob:
    downstream += ["misordered_recovery", "partial_availability_window", "operator_confusion"]

# preserve order, dedupe
seen = set()
ordered = []
for item in downstream:
    if item not in seen:
        seen.add(item)
        ordered.append(item)

result = {
    "predicted_failure_propagation_path": ordered or ["localized_divergence"],
    "estimated_blast_radius": "cross-service" if len(ordered) >= 3 else "local",
    "risk_level": risk,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
