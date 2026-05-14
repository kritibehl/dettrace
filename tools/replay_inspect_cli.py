#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


def cmd_inspect_trace(args):
    data = load(args.file)
    print(json.dumps({
        "file": args.file,
        "scenario": data.get("scenario") or data.get("incident_name"),
        "keys": sorted(data.keys())
    }, indent=2))


def cmd_show_divergence(args):
    data = load(args.file)
    diag = data.get("diagnosis") or data.get("divergence_summary") or data.get("analysis", {}).get("divergence")
    print(json.dumps(diag or {"divergence": "not_found"}, indent=2))


def cmd_show_timeouts(args):
    data = load(args.file)
    text = json.dumps(data).lower()
    result = {
        "file": args.file,
        "timeout_detected": "timeout" in text or "deadline_exceeded" in text,
        "timeout_mentions": text.count("timeout") + text.count("deadline_exceeded")
    }
    print(json.dumps(result, indent=2))


def cmd_show_retries(args):
    data = load(args.file)
    text = json.dumps(data).lower()
    result = {
        "file": args.file,
        "retry_detected": "retry" in text,
        "retry_mentions": text.count("retry")
    }
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Inspect DetTrace replay artifacts")
    sub = parser.add_subparsers(required=True)

    for name, fn in [
        ("inspect-trace", cmd_inspect_trace),
        ("show-divergence", cmd_show_divergence),
        ("show-timeouts", cmd_show_timeouts),
        ("show-retries", cmd_show_retries),
    ]:
        p = sub.add_parser(name)
        p.add_argument("file")
        p.set_defaults(func=fn)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
