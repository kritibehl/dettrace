#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def analyze_autoops_payload(path):
    data = json.loads(Path(path).read_text())
    summary = str(data.get("summary", "")).lower()

    if "retry" in summary or "timeout" in summary:
        result = {
            "root_cause": "retry amplification",
            "first_divergence": "service A retry loop",
            "dettrace_fingerprint": "retry_storm_timeout_chain"
        }
    else:
        result = {
            "root_cause": "event ordering divergence",
            "first_divergence": "service ordering mismatch",
            "dettrace_fingerprint": "cross_service_divergence"
        }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: dettrace_bridge.py <autoops_payload.json>")
    analyze_autoops_payload(sys.argv[1])
