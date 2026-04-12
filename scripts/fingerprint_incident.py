#!/usr/bin/env python3
import json
from pathlib import Path

DIV = Path("artifacts/divergence_report.json")
OUT = Path("artifacts/benchmarks/incident_fingerprint.json")

if not DIV.exists():
    print("No divergence_report.json found")
    exit(0)

data = json.loads(DIV.read_text())

features = []

# simple feature extraction
if data.get("divergence_type"):
    features.append(data["divergence_type"])

expected = str(data.get("expected_event", "")).lower()
actual = str(data.get("actual_event", "")).lower()

if "retry" in expected or "retry" in actual:
    features.append("retry_pattern")

if "timeout" in expected or "timeout" in actual:
    features.append("timeout_chain")

if "task" in expected and "task" in actual:
    features.append("task_mismatch")

fingerprint = "_".join(sorted(set(features))) if features else "unknown"

output = {
    "incident_fingerprint": fingerprint,
    "features": features
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(output, indent=2))

print(json.dumps(output, indent=2))
