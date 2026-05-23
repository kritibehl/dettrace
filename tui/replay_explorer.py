#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("usage: python3 tui/replay_explorer.py <trace.json>")
        return 1

    path = Path(sys.argv[1])
    data = json.loads(path.read_text())

    print("DetTrace Replay Explorer")
    print("========================")
    print(f"file: {path}")
    print(f"scenario: {data.get('scenario', data.get('incident_name', 'unknown'))}")
    print(f"safe_claim: {data.get('safe_claim', 'n/a')}")
    print("")

    diag = data.get("diagnosis") or data.get("divergence") or {}
    if diag:
        print("Divergence")
        print("----------")
        for k, v in diag.items():
            print(f"{k}: {v}")
    else:
        print("No divergence block found.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
