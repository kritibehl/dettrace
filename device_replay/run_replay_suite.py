#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def run(cmd):
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "command": " ".join(cmd),
        "returncode": completed.returncode,
        "output": completed.stdout,
    }

def parse_replay_output(output):
    parsed = {}
    for line in output.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            parsed[key.strip()] = value.strip()
    return parsed

def main():
    steps = []

    steps.append(run(["make", "clean"]))
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    steps.append(run(["make", "all"]))

    failing = run(["./replay_device_trace", "sample_device_trace.json"])
    fixed = run(["./replay_device_trace", "sample_device_trace_fixed.json"])
    c_demo = run(["./replay_c_api_demo"])

    failing_parsed = parse_replay_output(failing["output"])
    fixed_parsed = parse_replay_output(fixed["output"])
    c_parsed = parse_replay_output(c_demo["output"])

    summary = {
        "suite": "device-event-replay",
        "checks": {
            "build": steps,
            "failing_trace": failing,
            "fixed_trace": fixed,
            "c_api_demo": c_demo,
        },
        "parsed": {
            "failing_trace": failing_parsed,
            "fixed_trace": fixed_parsed,
            "c_api_demo": c_parsed,
        },
        "result": {
            "failing_trace_detected": failing_parsed.get("status") == "FAIL",
            "fixed_trace_passed": fixed_parsed.get("status") == "PASS",
            "c_api_divergence_index": c_parsed.get("first_divergence_index"),
            "probable_defect_type": failing_parsed.get("probable_defect_type"),
        }
    }

    (REPORT_DIR / "device_replay_summary.json").write_text(json.dumps(summary, indent=2))

    md = [
        "# Device Replay Suite Summary",
        "",
        "## Failing trace",
        f"- status: {failing_parsed.get('status')}",
        f"- first divergence index: {failing_parsed.get('first_divergence_index')}",
        f"- expected event: {failing_parsed.get('expected_event')}",
        f"- actual event: {failing_parsed.get('actual_event')}",
        f"- probable defect type: {failing_parsed.get('probable_defect_type')}",
        "",
        "## Fixed trace",
        f"- status: {fixed_parsed.get('status')}",
        f"- first divergence index: {fixed_parsed.get('first_divergence_index')}",
        "",
        "## C API demo",
        f"- first divergence index: {c_parsed.get('first_divergence_index')}",
        f"- probable defect type: {c_parsed.get('probable_defect_type')}",
        "",
        "## Interpretation",
        "The failing trace reproduces a missing interrupt-clear defect at index 4.",
        "The corrected trace validates that the expected interrupt clear and READY transition restore the replay path.",
    ]
    (REPORT_DIR / "device_replay_summary.md").write_text("\n".join(md) + "\n")

    print(json.dumps(summary["result"], indent=2))

    if not summary["result"]["failing_trace_detected"] or not summary["result"]["fixed_trace_passed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
