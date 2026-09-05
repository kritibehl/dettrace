from __future__ import annotations

from trace_regression.compare import (
    compare_traces,
)
from trace_regression.critical_path import (
    compare_critical_paths,
)
from trace_regression.errors import (
    compare_error_rates,
)
from trace_regression.normalize import (
    normalize_trace,
)


def choose_primary_localized_regression(
    regressions,
):
    localized = [
        regression
        for regression in regressions
        if regression[
            "parent"
        ] != "ROOT"
    ]

    candidates = (
        localized
        or regressions
    )

    if not candidates:
        return None

    return max(
        candidates,
        key=lambda item: (
            item["delta_pct"],
            item["delta_ms"],
        ),
    )


def find_end_to_end_regression(
    regressions,
):
    roots = [
        regression
        for regression in regressions
        if regression[
            "parent"
        ] == "ROOT"
    ]

    if not roots:
        return None

    return max(
        roots,
        key=lambda item:
            item["delta_ms"],
    )


def _tuple_to_dict(
    value,
):
    return {
        "service":
            value[0],
        "span":
            value[1],
        "parent":
            value[2],
    }


def analyze_cohort(
    baseline_raw,
    candidate_raw,
    regression_threshold_pct=50.0,
    error_threshold_pp=5.0,
):
    baseline_normalized = [
        normalize_trace(trace)
        for trace in baseline_raw
    ]

    candidate_normalized = [
        normalize_trace(trace)
        for trace in candidate_raw
    ]

    comparison = compare_traces(
        baseline_normalized,
        candidate_normalized,
        regression_threshold_pct=(
            regression_threshold_pct
        ),
    )

    error_analysis = (
        compare_error_rates(
            baseline_normalized,
            candidate_normalized,
            threshold_percentage_points=(
                error_threshold_pp
            ),
        )
    )

    critical_path = (
        compare_critical_paths(
            baseline_raw,
            candidate_raw,
        )
    )

    regressions = comparison[
        "regressions"
    ]

    primary = (
        choose_primary_localized_regression(
            regressions
        )
    )

    end_to_end = (
        find_end_to_end_regression(
            regressions
        )
    )

    error_regressions = (
        error_analysis[
            "regressions"
        ]
    )

    decision = (
        "FAIL"
        if (
            regressions
            or comparison[
                "added_spans"
            ]
            or error_regressions
        )
        else "PASS"
    )

    return {
        "baseline_trace_count":
            len(
                baseline_raw
            ),
        "candidate_trace_count":
            len(
                candidate_raw
            ),
        "latency_threshold_pct":
            regression_threshold_pct,
        "error_threshold_percentage_points":
            error_threshold_pp,
        "added_spans": [
            _tuple_to_dict(
                item
            )
            for item in comparison[
                "added_spans"
            ]
        ],
        "removed_spans": [
            _tuple_to_dict(
                item
            )
            for item in comparison[
                "removed_spans"
            ]
        ],
        "regressions":
            regressions,
        "primary_localized_regression":
            primary,
        "end_to_end_regression":
            end_to_end,
        "error_regressions":
            error_regressions,
        "critical_path":
            critical_path,
        "decision":
            decision,
    }
