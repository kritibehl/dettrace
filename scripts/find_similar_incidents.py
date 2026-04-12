#!/usr/bin/env python3
import json
from pathlib import Path

HIST = Path("artifacts/history")
CUR = Path("artifacts/benchmarks/incident_fingerprint.json")
OUT = Path("artifacts/benchmarks/similar_incidents.json")

if not CUR.exists():
    print("No incident_fingerprint.json found")
    raise SystemExit(0)

current = json.loads(CUR.read_text())
cur_fp = current.get("incident_fingerprint")
cur_features = set(current.get("features", []))

results = []

for path in sorted(HIST.glob("incident_*.json")):
    try:
        item = json.loads(path.read_text())
    except Exception:
        continue

    score = 0.0
    other_fp = item.get("incident_fingerprint")
    other_features = set(item.get("features", []))

    if cur_fp and other_fp and cur_fp == other_fp:
        score += 0.70

    union = cur_features | other_features
    inter = cur_features & other_features
    if union:
        score += 0.30 * (len(inter) / len(union))

    if score > 0:
        results.append({
            "incident_file": str(path),
            "incident_fingerprint": other_fp,
            "confidence": round(score, 2),
            "first_divergence_index": item.get("first_divergence_index"),
            "risk_level": item.get("risk_level"),
        })

results.sort(key=lambda x: x["confidence"], reverse=True)

output = {
    "current_incident_fingerprint": cur_fp,
    "similar_incidents": results[:5],
    "top_match": results[0] if results else None
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(output, indent=2))
print(json.dumps(output, indent=2))
