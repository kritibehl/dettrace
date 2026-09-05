from __future__ import annotations

from collections import defaultdict

from .statistics import summarize


def aggregate(normalized_traces):
    durations = defaultdict(list)

    for trace in normalized_traces:
        for span in trace:
            durations[span["semantic_key"]].append(
                span["duration_ms"]
            )

    return {
        key: summarize(values)
        for key, values in durations.items()
    }


def percent_change(old, new):
    if old == 0:
        return 0.0 if new == 0 else float("inf")

    return ((new - old) / old) * 100.0


def compare_traces(
    baseline_traces,
    candidate_traces,
    regression_threshold_pct=50.0,
):
    baseline = aggregate(baseline_traces)
    candidate = aggregate(candidate_traces)

    baseline_keys = set(baseline)
    candidate_keys = set(candidate)

    added = sorted(candidate_keys - baseline_keys)
    removed = sorted(baseline_keys - candidate_keys)

    regressions = []

    for key in sorted(baseline_keys & candidate_keys):
        before = baseline[key]
        after = candidate[key]

        delta_ms = (
            after["p95_ms"]
            - before["p95_ms"]
        )

        delta_pct = percent_change(
            before["p95_ms"],
            after["p95_ms"],
        )

        if delta_pct >= regression_threshold_pct:
            regressions.append(
                {
                    "semantic_key": key,
                    "service": key[0],
                    "span": key[1],
                    "parent": key[2],
                    "baseline_p95_ms": before["p95_ms"],
                    "candidate_p95_ms": after["p95_ms"],
                    "delta_ms": delta_ms,
                    "delta_pct": delta_pct,
                }
            )

    regressions.sort(
        key=lambda item: item["delta_ms"],
        reverse=True,
    )

    return {
        "added_spans": added,
        "removed_spans": removed,
        "regressions": regressions,
    }
