#!/usr/bin/env python3
import json
from pathlib import Path

EXPECTED = Path("artifacts/expected.jsonl")
ACTUAL = Path("artifacts/actual.jsonl")
OUT = Path("reports/divergence_report.json")

def read_jsonl(path: Path):
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def first_divergence(a, b):
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    if len(a) != len(b):
        return n
    return None

def main():
    expected = read_jsonl(EXPECTED)
    actual = read_jsonl(ACTUAL)

    idx = first_divergence(expected, actual)

    report = {
        "trace_a": str(EXPECTED),
        "trace_b": str(ACTUAL),
        "first_divergence_event": idx,
        "expected": expected[idx] if idx is not None and idx < len(expected) else {},
        "actual": actual[idx] if idx is not None and idx < len(actual) else {},
        "invariant_failures": [],
        "notes": "Generated from trace comparison."
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        json.dump(report, f, indent=2)
        f.write("\n")

    print(f"Wrote {OUT}")
    if idx is not None:
        print(f"First divergence at event index {idx}")

if __name__ == "__main__":
    main()
