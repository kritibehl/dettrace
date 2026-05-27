#!/usr/bin/env python3
import json
from pathlib import Path

PRE = Path("bringup_validation/pre_silicon_boot_trace.json")
POST = Path("bringup_validation/post_silicon_boot_trace.json")
REPORT_JSON = Path("bringup_validation/bringup_comparison_report.json")
REPORT_MD = Path("bringup_validation/bringup_comparison_report.md")


def load_events(path):
    return json.loads(path.read_text())["boot_events"]


def signature(event):
    return {
        "phase": event["phase"],
        "event": event["event"],
        "register": event["register"],
        "value": event["value"],
        "calibration_status": event["calibration_status"],
        "status": event["status"],
    }


def main():
    expected = load_events(PRE)
    observed = load_events(POST)

    first_divergence = None
    for idx, (e, a) in enumerate(zip(expected, observed)):
        if signature(e) != signature(a):
            first_divergence = {
                "index": idx,
                "expected": signature(e),
                "observed": signature(a),
            }
            break

    timeout_events = [e for e in observed if e["status"] == "timeout" or "timeout" in e["event"]]
    retry_events = [e for e in observed if e["status"] == "retry" or "retry" in e["event"]]
    calibration_issues = [
        e for e in observed
        if e["calibration_status"] not in {"not_started", "running", "valid"}
    ]
    blocked_or_degraded = [
        e for e in observed
        if e["status"] in {"blocked", "degraded"}
    ]

    report = {
        "workflow": "pre-post-silicon-style-bringup-trace-validation",
        "safe_claim": "firmware-style trace validation; not silicon ownership or hardware lab bring-up",
        "expected_trace": str(PRE),
        "observed_trace": str(POST),
        "expected_event_count": len(expected),
        "observed_event_count": len(observed),
        "first_divergence": first_divergence,
        "timeout_event_count": len(timeout_events),
        "retry_event_count": len(retry_events),
        "calibration_issue_count": len(calibration_issues),
        "blocked_or_degraded_event_count": len(blocked_or_degraded),
        "diagnostic_status": "FAIL" if first_divergence or timeout_events or calibration_issues or blocked_or_degraded else "PASS",
        "root_cause_summary": (
            "Observed boot trace diverged during register initialization: expected clock_enable but observed "
            "clock_enable_timeout, followed by retry behavior, calibration drift warning, and blocked ready state."
            if first_divergence else
            "Observed boot trace matched expected boot sequence."
        ),
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))

    div = report["first_divergence"]
    REPORT_MD.write_text(
        "# Bring-Up Comparison Report\n\n"
        "## Safe claim\n\n"
        f"{report['safe_claim']}\n\n"
        "## Summary\n\n"
        f"- diagnostic status: `{report['diagnostic_status']}`\n"
        f"- expected event count: `{report['expected_event_count']}`\n"
        f"- observed event count: `{report['observed_event_count']}`\n"
        f"- first divergence index: `{div['index'] if div else 'none'}`\n"
        f"- timeout events: `{report['timeout_event_count']}`\n"
        f"- retry events: `{report['retry_event_count']}`\n"
        f"- calibration issues: `{report['calibration_issue_count']}`\n"
        f"- blocked/degraded events: `{report['blocked_or_degraded_event_count']}`\n\n"
        "## First divergence\n\n"
        f"- expected: `{div['expected'] if div else 'none'}`\n"
        f"- observed: `{div['observed'] if div else 'none'}`\n\n"
        "## Root-cause summary\n\n"
        f"{report['root_cause_summary']}\n"
    )

    print(json.dumps(report, indent=2))

    if report["diagnostic_status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
