from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.main import (
    build_fingerprint,
    detect_retry_storm,
    detect_timeout_chain,
    first_divergence,
    root_cause_explanation,
    sort_events,
)

def load_events(path: str):
    p = Path(path)
    if p.suffix == ".json":
        data = json.loads(p.read_text())
        if isinstance(data, dict) and "events" in data:
            return data["events"]
        if isinstance(data, list):
            return data
    if p.suffix == ".jsonl":
        return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    raise SystemExit(f"Unsupported file format: {path}")

def cmd_replay(args):
    events = sort_events(load_events(args.input))
    print(json.dumps({
        "event_count": len(events),
        "first_divergence": first_divergence(events),
    }, indent=2))

def cmd_diff(args):
    expected = sort_events(load_events(args.expected))
    actual = sort_events(load_events(args.actual))
    merged = expected + actual
    print(json.dumps({
        "first_divergence": first_divergence(merged),
        "expected_count": len(expected),
        "actual_count": len(actual),
    }, indent=2))

def cmd_fingerprint(args):
    events = sort_events(load_events(args.input))
    divergence = first_divergence(events)
    print(json.dumps({
        "fingerprint": build_fingerprint(events, divergence),
        "retry_storm_detection": detect_retry_storm(events),
        "timeout_chain_detection": detect_timeout_chain(events),
        "root_cause_explanation": root_cause_explanation(events, divergence),
    }, indent=2))

def cmd_compare_incidents(args):
    left = json.loads(Path(args.left).read_text())
    right = json.loads(Path(args.right).read_text())
    left_fp = left.get("analysis", {}).get("fingerprint", {})
    right_fp = right.get("analysis", {}).get("fingerprint", {})
    print(json.dumps({
        "left_incident": left.get("incident_name"),
        "right_incident": right.get("incident_name"),
        "left_fingerprint": left_fp,
        "right_fingerprint": right_fp,
        "same_fingerprint": left_fp.get("incident_fingerprint") == right_fp.get("incident_fingerprint"),
    }, indent=2))

def main():
    parser = argparse.ArgumentParser(prog="dettrace-cli")
    sub = parser.add_subparsers(dest="cmd", required=True)

    replay = sub.add_parser("replay")
    replay.add_argument("input")
    replay.set_defaults(func=cmd_replay)

    diff = sub.add_parser("diff")
    diff.add_argument("expected")
    diff.add_argument("actual")
    diff.set_defaults(func=cmd_diff)

    fp = sub.add_parser("fingerprint")
    fp.add_argument("input")
    fp.set_defaults(func=cmd_fingerprint)

    comp = sub.add_parser("compare-incidents")
    comp.add_argument("left")
    comp.add_argument("right")
    comp.set_defaults(func=cmd_compare_incidents)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
