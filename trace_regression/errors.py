from __future__ import annotations

from collections import defaultdict


def _is_error_status(
    status,
) -> bool:
    return (
        str(status).upper()
        == "ERROR"
    )


def aggregate_error_stats(
    normalized_traces,
):
    counters = defaultdict(
        lambda: {
            "count": 0,
            "errors": 0,
        }
    )

    for trace in normalized_traces:
        for span in trace:
            key = span[
                "semantic_key"
            ]

            counters[
                key
            ]["count"] += 1

            if _is_error_status(
                span.get(
                    "status",
                    "UNSET",
                )
            ):
                counters[
                    key
                ]["errors"] += 1

    result = {}

    for key, values in counters.items():
        count = values["count"]
        errors = values["errors"]

        result[key] = {
            "count":
                count,
            "errors":
                errors,
            "error_rate":
                (
                    errors / count
                    if count
                    else 0.0
                ),
        }

    return result


def compare_error_rates(
    baseline_traces,
    candidate_traces,
    threshold_percentage_points=5.0,
):
    baseline = aggregate_error_stats(
        baseline_traces
    )

    candidate = aggregate_error_stats(
        candidate_traces
    )

    shared_keys = (
        set(baseline)
        & set(candidate)
    )

    regressions = []

    for key in sorted(
        shared_keys
    ):
        before = baseline[key]
        after = candidate[key]

        delta_percentage_points = (
            (
                after["error_rate"]
                - before["error_rate"]
            )
            * 100.0
        )

        if (
            delta_percentage_points
            >= threshold_percentage_points
        ):
            regressions.append(
                {
                    "service":
                        key[0],
                    "span":
                        key[1],
                    "parent":
                        key[2],
                    "baseline_count":
                        before["count"],
                    "candidate_count":
                        after["count"],
                    "baseline_errors":
                        before["errors"],
                    "candidate_errors":
                        after["errors"],
                    "baseline_error_rate":
                        before[
                            "error_rate"
                        ],
                    "candidate_error_rate":
                        after[
                            "error_rate"
                        ],
                    "delta_percentage_points":
                        delta_percentage_points,
                }
            )

    regressions.sort(
        key=lambda item: (
            item[
                "delta_percentage_points"
            ],
            item[
                "candidate_error_rate"
            ],
        ),
        reverse=True,
    )

    return {
        "threshold_percentage_points":
            threshold_percentage_points,
        "baseline":
            baseline,
        "candidate":
            candidate,
        "regressions":
            regressions,
    }
