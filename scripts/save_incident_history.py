#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

bench = Path("artifacts/benchmarks")
hist = Path("artifacts/history")
hist.mkdir(parents=True, exist_ok=True)

fingerprint_path = bench / "incident_fingerprint.json"
propagation_path = bench / "propagation_prediction.json"
metrics_path = bench / "metrics_summary.json"
div_path = Path("artifacts/divergence_report.json")

record = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "incident_fingerprint": None,
    "features": [],
    "predicted_failure_propagation_path": [],
    "risk_level": None,
    "first_divergence_index": None,
    "divergence_type": None,
}

if fingerprint_path.exists():
    fp = json.loads(fingerprint_path.read_text())
    record["incident_fingerprint"] = fp.get("incident_fingerprint")
    record["features"] = fp.get("features", [])

if propagation_path.exists():
    pp = json.loads(propagation_path.read_text())
    record["predicted_failure_propagation_path"] = pp.get("predicted_failure_propagation_path", [])
    record["risk_level"] = pp.get("risk_level")

if metrics_path.exists():
    ms = json.loads(metrics_path.read_text())
    record["first_divergence_index"] = ms.get("first_divergence_index")

if div_path.exists():
    dv = json.loads(div_path.read_text())
    record["divergence_type"] = dv.get("divergence_type")

ts_slug = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
out = hist / f"incident_{ts_slug}.json"
out.write_text(json.dumps(record, indent=2))
print(json.dumps({"saved_incident": str(out), "record": record}, indent=2))
