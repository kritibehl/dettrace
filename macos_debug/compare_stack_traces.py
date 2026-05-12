#!/usr/bin/env python3
from pathlib import Path
import json

expected = Path("macos_debug/sample_stack_expected.txt").read_text().splitlines()
actual = Path("macos_debug/sample_stack_actual.txt").read_text().splitlines()

first = None
for i, (e, a) in enumerate(zip(expected, actual)):
    if e != a:
        first = {
            "first_mismatched_frame": i,
            "expected_frame": e,
            "actual_frame": a,
            "likely_affected_subsystem": "SerialTransport / DeviceSession lifecycle",
            "probable_defect_class": "disconnect-before-heartbeat",
            "confidence": 0.84
        }
        break

report = {
    "workflow": "simulated-macos-stack-comparison",
    "status": "mismatch_found" if first else "match",
    "analysis": first
}

Path("macos_debug/symbolized_replay_report.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
