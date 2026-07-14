#!/usr/bin/env python3
import json
from pathlib import Path

TRACE = Path("sensor_replay_pack/synthetic_gps_imu_trace.json")
REPORT_JSON = Path("sensor_replay_pack/sensor_integrity_report.json")
REPORT_MD = Path("sensor_replay_pack/sensor_integrity_report.md")


def main():
    data = json.loads(TRACE.read_text())
    expected = data["expected_events"]
    observed = data["observed_events"]
    thresholds = data["thresholds"]

    dropped = []
    duplicated = []
    delayed = []
    out_of_order = []
    first_divergence = None

    expected_ids = [event["event_id"] for event in expected]
    observed_ids = [event["event_id"] for event in observed]

    for event_id in expected_ids:
        if event_id not in observed_ids:
            dropped.append(event_id)

    seen = set()
    for idx, event in enumerate(observed):
        event_id = event["event_id"]
        if event_id in seen:
            duplicated.append({
                "index": idx,
                "event_id": event_id
            })
        seen.add(event_id)

        if idx > 0:
            previous = observed[idx - 1]
            delta = event["timestamp_ms"] - previous["timestamp_ms"]

            if delta < 0:
                out_of_order.append({
                    "index": idx,
                    "previous_timestamp_ms": previous["timestamp_ms"],
                    "current_timestamp_ms": event["timestamp_ms"],
                    "event_id": event_id
                })

            if delta > thresholds["max_expected_interval_ms"]:
                delayed.append({
                    "index": idx,
                    "event_id": event_id,
                    "interval_ms": delta,
                    "threshold_ms": thresholds["max_expected_interval_ms"]
                })

    for idx, (expected_event, observed_event) in enumerate(zip(expected, observed)):
        if (
            expected_event["event_id"] != observed_event["event_id"]
            or expected_event["timestamp_ms"] != observed_event["timestamp_ms"]
        ):
            first_divergence = {
                "index": idx,
                "expected_event_id": expected_event["event_id"],
                "observed_event_id": observed_event["event_id"],
                "expected_timestamp_ms": expected_event["timestamp_ms"],
                "observed_timestamp_ms": observed_event["timestamp_ms"]
            }
            break

    invalid_segment_start = first_divergence["index"] if first_divergence else None
    invalid_segment_end = len(observed) - 1 if first_divergence else None

    report = {
        "workflow": "synthetic-gps-imu-sensor-replay",
        "safe_claim": "synthetic GPS/IMU-style trajectory data validation; not production autonomy or map creation",
        "expected_event_count": len(expected),
        "observed_event_count": len(observed),
        "first_divergence": first_divergence,
        "dropped_events": dropped,
        "duplicated_events": duplicated,
        "delayed_events": delayed,
        "out_of_order_events": out_of_order,
        "invalid_trajectory_segment": {
            "start_index": invalid_segment_start,
            "end_index": invalid_segment_end
        },
        "trajectory_valid_for_downstream_mapping": not any([
            dropped,
            duplicated,
            delayed,
            out_of_order,
            first_divergence
        ])
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))

    REPORT_MD.write_text(
        "# Sensor Stream Integrity Report\n\n"
        "## Safe claim\n\n"
        f"{report['safe_claim']}\n\n"
        "## Summary\n\n"
        f"- expected event count: `{report['expected_event_count']}`\n"
        f"- observed event count: `{report['observed_event_count']}`\n"
        f"- first divergence index: `{first_divergence['index'] if first_divergence else 'none'}`\n"
        f"- dropped events: `{len(dropped)}`\n"
        f"- duplicated events: `{len(duplicated)}`\n"
        f"- delayed events: `{len(delayed)}`\n"
        f"- out-of-order events: `{len(out_of_order)}`\n"
        f"- trajectory valid for downstream mapping: `{report['trajectory_valid_for_downstream_mapping']}`\n\n"
        "## First divergence\n\n"
        f"- details: `{first_divergence}`\n\n"
        "## Invalid trajectory segment\n\n"
        f"- start index: `{invalid_segment_start}`\n"
        f"- end index: `{invalid_segment_end}`\n\n"
        "## Interpretation\n\n"
        "The observed sensor stream contains integrity failures before downstream trajectory or map-generation use. "
        "The replay isolates the earliest divergence and reports dropped, duplicated, delayed, and out-of-order records.\n"
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
