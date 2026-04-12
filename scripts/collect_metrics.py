#!/usr/bin/env python3
import json
from pathlib import Path

ART = Path("artifacts")
OUT = Path("artifacts/benchmarks")
OUT.mkdir(parents=True, exist_ok=True)

def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open() as f:
        return sum(1 for _ in f)

expected = ART / "expected.jsonl"
actual = ART / "actual.jsonl"
replayed = ART / "replayed.jsonl"
divergence = ART / "divergence_report.json"

metrics = {
    "expected_event_count": count_lines(expected),
    "actual_event_count": count_lines(actual),
    "replayed_event_count": count_lines(replayed),
    "artifact_files_present": {
        "expected.jsonl": expected.exists(),
        "actual.jsonl": actual.exists(),
        "replayed.jsonl": replayed.exists(),
        "divergence_report.json": divergence.exists(),
    },
}

if divergence.exists():
    try:
        report = json.loads(divergence.read_text())
        metrics["first_divergence_index"] = report.get("first_divergence_index")
        metrics["divergence_type"] = report.get("divergence_type")
        metrics["expected_event"] = report.get("expected_event")
        metrics["actual_event"] = report.get("actual_event")
    except Exception as e:
        metrics["divergence_parse_error"] = str(e)

OUT.joinpath("metrics_summary.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))
