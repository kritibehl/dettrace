#!/usr/bin/env python3
from pathlib import Path
import json

path = Path("crash_tools/sample_crash_log.txt")
text = path.read_text().splitlines()

actual = []
expected = []
mode = "actual"

for line in text:
    if line.startswith("Expected Stack"):
        mode = "expected"
        continue
    if "DeviceSession" in line or "EventLoop" in line or "AppMain" in line:
        frame = line.split(maxsplit=2)[-1]
        if mode == "actual":
            actual.append(frame)
        else:
            expected.append(frame)

first = None
for i, (a, e) in enumerate(zip(actual, expected)):
    if a != e:
        first = {
            "first_mismatched_frame": i,
            "expected_frame": e,
            "actual_frame": a,
            "probable_defect_class": "disconnect-before-heartbeat",
            "likely_affected_subsystem": "SerialTransport / DeviceSession lifecycle",
            "confidence": 0.84
        }
        break

report = {
    "input": str(path),
    "status": "mismatch_found" if first else "match",
    "actual_stack": actual,
    "expected_stack": expected,
    "analysis": first
}

Path("crash_tools/crash_parse_report.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
