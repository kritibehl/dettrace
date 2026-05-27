#!/usr/bin/env python3
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

LOGS = Path("firmware_logs/firmware_events.jsonl")
SUMMARY_JSON = Path("firmware_logs/firmware_log_summary_report.json")
SUMMARY_MD = Path("firmware_logs/firmware_log_summary_report.md")


def load_events():
    return [json.loads(line) for line in LOGS.read_text().splitlines() if line.strip()]


def filter_events(events, device_id=None, severity=None, boot_phase=None):
    out = events
    if device_id:
        out = [e for e in out if e["device_id"] == device_id]
    if severity:
        out = [e for e in out if e["severity"] == severity]
    if boot_phase:
        out = [e for e in out if e["boot_phase"] == boot_phase]
    return out


def summarize(events):
    retry_events = [e for e in events if "retry" in e["event"]]
    timeout_events = [e for e in events if "timeout" in e["event"]]
    calibration_failures = [e for e in events if "calibration" in e["event"] and e["severity"] in {"WARN", "ERROR"}]

    by_device = defaultdict(list)
    for e in events:
        by_device[e["device_id"]].append(e)

    retry_storms = {
        device: len([e for e in evs if "retry" in e["event"]])
        for device, evs in by_device.items()
    }
    retry_storms = {k: v for k, v in retry_storms.items() if v >= 2}

    timeout_chains = {
        device: len([e for e in evs if "timeout" in e["event"] or "blocked" in e["event"]])
        for device, evs in by_device.items()
    }
    timeout_chains = {k: v for k, v in timeout_chains.items() if v >= 2}

    severity_counts = Counter(e["severity"] for e in events)
    boot_phase_counts = Counter(e["boot_phase"] for e in events)

    report = {
        "event_count": len(events),
        "severity_counts": dict(severity_counts),
        "boot_phase_counts": dict(boot_phase_counts),
        "retry_event_count": len(retry_events),
        "timeout_event_count": len(timeout_events),
        "calibration_failure_count": len(calibration_failures),
        "retry_storms": retry_storms,
        "timeout_chains": timeout_chains,
        "failure_families": {
            "calibration_failure": len(calibration_failures),
            "timeout_chain": len(timeout_events),
            "retry_storm": sum(retry_storms.values())
        }
    }

    SUMMARY_JSON.write_text(json.dumps(report, indent=2))
    SUMMARY_MD.write_text(
        "# Firmware Log Summary Report\n\n"
        "## Summary\n\n"
        f"- event count: `{report['event_count']}`\n"
        f"- retry events: `{report['retry_event_count']}`\n"
        f"- timeout events: `{report['timeout_event_count']}`\n"
        f"- calibration failures: `{report['calibration_failure_count']}`\n"
        f"- retry storms: `{report['retry_storms']}`\n"
        f"- timeout chains: `{report['timeout_chains']}`\n\n"
        "## Failure families\n\n"
        f"- calibration failure: `{report['failure_families']['calibration_failure']}`\n"
        f"- timeout chain: `{report['failure_families']['timeout_chain']}`\n"
        f"- retry storm: `{report['failure_families']['retry_storm']}`\n"
    )
    return report


def main():
    parser = argparse.ArgumentParser(description="Query firmware-style JSONL telemetry")
    parser.add_argument("--device-id")
    parser.add_argument("--severity")
    parser.add_argument("--boot-phase")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    events = filter_events(load_events(), args.device_id, args.severity, args.boot_phase)

    if args.summary:
        print(json.dumps(summarize(events), indent=2))
    else:
        for e in events:
            print(json.dumps(e))


if __name__ == "__main__":
    main()
