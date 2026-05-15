#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

INPUT = Path("instrumentation_demo/mock_instrument_capture.json")
REPORT_JSON = Path("instrumentation_demo/instrument_validation_report.json")
REPORT_MD = Path("instrumentation_demo/measurement_validation_report.md")


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main():
    capture = json.loads(INPUT.read_text())
    samples = capture["samples"]
    expected_count = capture["expected_sample_count"]
    allowed = capture["allowed_range_nm"]

    timestamps = [parse_ts(s["timestamp"]) for s in samples]
    missing_windows = []

    for prev, curr in zip(timestamps, timestamps[1:]):
        gap_seconds = int((curr - prev).total_seconds())
        if gap_seconds > 1:
            missing_windows.append({
                "after": prev.isoformat(),
                "before": curr.isoformat(),
                "missing_sample_count_estimate": gap_seconds - 1
            })

    out_of_range = [
        s for s in samples
        if s["measured_position_nm"] < allowed["min"]
        or s["measured_position_nm"] > allowed["max"]
    ]

    calibration_issues = [
        s for s in samples
        if s["calibration_status"] != "valid"
    ]

    degraded_states = [
        s for s in samples
        if s["device_state"] != "ready"
    ]

    retry_events = [
        s for s in samples
        if s["retry_count"] > 0
    ]

    report = {
        "capture_id": capture["capture_id"],
        "instrument": capture["instrument"],
        "safe_claim": capture["safe_claim"],
        "sample_count": len(samples),
        "expected_sample_count": expected_count,
        "missing_sample_count": max(0, expected_count - len(samples)),
        "incomplete_capture": len(samples) < expected_count,
        "missing_windows": missing_windows,
        "out_of_range_count": len(out_of_range),
        "calibration_issue_count": len(calibration_issues),
        "degraded_state_count": len(degraded_states),
        "retry_event_count": len(retry_events),
        "diagnostic_status": "FAIL" if (
            len(samples) < expected_count
            or out_of_range
            or calibration_issues
            or degraded_states
        ) else "PASS",
        "findings": {
            "out_of_range_samples": out_of_range,
            "calibration_issues": calibration_issues,
            "degraded_states": degraded_states,
            "retry_events": retry_events
        }
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))

    REPORT_MD.write_text(
        "# Measurement Validation Report\n\n"
        f"## Capture\n\n`{report['capture_id']}` from `{report['instrument']}`\n\n"
        "## Safe claim\n\n"
        f"{report['safe_claim']}\n\n"
        "## Summary\n\n"
        f"- diagnostic status: `{report['diagnostic_status']}`\n"
        f"- sample count: `{report['sample_count']}` / expected `{report['expected_sample_count']}`\n"
        f"- missing sample count: `{report['missing_sample_count']}`\n"
        f"- out-of-range samples: `{report['out_of_range_count']}`\n"
        f"- calibration issues: `{report['calibration_issue_count']}`\n"
        f"- degraded states: `{report['degraded_state_count']}`\n"
        f"- retry events: `{report['retry_event_count']}`\n\n"
        "## Diagnostic interpretation\n\n"
        "The capture is marked `FAIL` because it contains an out-of-range measurement, calibration drift warnings, degraded device states, retry events, and incomplete capture windows.\n\n"
        "This demonstrates mock instrument-data parsing and validation for hardware-adjacent diagnostics review.\n"
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
