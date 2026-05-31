#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def extract_signature(path):
    data = json.loads(Path(path).read_text())
    text = json.dumps(data).lower()

    families = ["usb", "pcie", "displayport", "accessory", "transport"]
    failure_terms = ["timeout", "disconnect", "retry", "stale", "enumeration", "link", "calibration", "state"]

    return {
        "artifact": path,
        "families": [f for f in families if f in text],
        "failure_terms": [t for t in failure_terms if t in text],
        "raw_token_count": len(set(text.replace('"', " ").replace("_", " ").split()))
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 incident_similarity/signature_extractor.py <artifact.json>")
        raise SystemExit(1)
    print(json.dumps(extract_signature(sys.argv[1]), indent=2))
