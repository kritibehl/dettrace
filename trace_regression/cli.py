#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from trace_regression.ingest import load_span_file

from trace_regression.analyzer import (
    analyze_cohort,
    choose_primary_localized_regression,
    find_end_to_end_regression,
)
from trace_regression.cohorts import (
    group_traces_by_shape,
)
from trace_regression.normalize import (
    group_by_trace,
)


def load_raw_traces(
    path,
):
    spans = load_span_file(
        path
    )

    grouped = group_by_trace(
        spans
    )

    return list(
        grouped.values()
    )


def analyze_shapes(
    baseline_raw,
    candidate_raw,
    latency_threshold_pct,
    error_threshold_pp,
):
    baseline_shapes = (
        group_traces_by_shape(
            baseline_raw
        )
    )

    candidate_shapes = (
        group_traces_by_shape(
            candidate_raw
        )
    )

    baseline_keys = set(
        baseline_shapes
    )

    candidate_keys = set(
        candidate_shapes
    )

    matched = sorted(
        baseline_keys
        & candidate_keys
    )

    baseline_only = sorted(
        baseline_keys
        - candidate_keys
    )

    candidate_only = sorted(
        candidate_keys
        - baseline_keys
    )

    cohorts = []

    for fingerprint in matched:
        baseline_group = (
            baseline_shapes[
                fingerprint
            ]
        )

        candidate_group = (
            candidate_shapes[
                fingerprint
            ]
        )

        analysis = analyze_cohort(
            baseline_group[
                "traces"
            ],
            candidate_group[
                "traces"
            ],
            regression_threshold_pct=(
                latency_threshold_pct
            ),
            error_threshold_pp=(
                error_threshold_pp
            ),
        )

        analysis[
            "shape"
        ] = baseline_group[
            "shape"
        ]

        cohorts.append(
            analysis
        )

    overall_decision = (
        "FAIL"
        if any(
            cohort[
                "decision"
            ] == "FAIL"
            for cohort in cohorts
        )
        else "PASS"
    )

    return {
        "schema_version":
            2,
        "baseline_trace_count":
            len(
                baseline_raw
            ),
        "candidate_trace_count":
            len(
                candidate_raw
            ),
        "matched_shape_count":
            len(
                matched
            ),
        "baseline_only_shapes": [
            baseline_shapes[key][
                "shape"
            ]
            for key in baseline_only
        ],
        "candidate_only_shapes": [
            candidate_shapes[key][
                "shape"
            ]
            for key in candidate_only
        ],
        "cohorts":
            cohorts,
        "decision":
            overall_decision,
    }


def print_cohort(
    cohort,
):
    shape = cohort[
        "shape"
    ]

    print()
    print("=" * 64)

    print(
        "REQUEST SHAPE"
    )

    print(
        f"  service: "
        f"{shape['service']}"
    )

    print(
        f"  root:    "
        f"{shape['root_span']}"
    )

    print(
        f"  method:  "
        f"{shape['method']}"
    )

    print(
        f"  route:   "
        f"{shape['route']}"
    )

    print(
        f"  baseline traces:  "
        f"{cohort['baseline_trace_count']}"
    )

    print(
        f"  candidate traces: "
        f"{cohort['candidate_trace_count']}"
    )

    if cohort[
        "added_spans"
    ]:
        print()
        print(
            "STRUCTURAL CHANGES"
        )

        for item in cohort[
            "added_spans"
        ]:
            print(
                f"  {item['parent']} "
                f"-> {item['span']} "
                f"[service="
                f"{item['service']}]"
            )

    end_to_end = cohort[
        "end_to_end_regression"
    ]

    if end_to_end:
        print()
        print(
            "END-TO-END LATENCY REGRESSION"
        )

        print(
            f"  p95: "
            f"{end_to_end['baseline_p95_ms']:.2f}"
            f" -> "
            f"{end_to_end['candidate_p95_ms']:.2f}"
            f" ms"
        )

        print(
            f"  delta: "
            f"+{end_to_end['delta_ms']:.2f}"
            f" ms"
        )

        print(
            f"  change: "
            f"+{end_to_end['delta_pct']:.1f}%"
        )

    primary = cohort[
        "primary_localized_regression"
    ]

    if primary:
        print()
        print(
            "PRIMARY LOCALIZED REGRESSION"
        )

        print(
            f"  service: "
            f"{primary['service']}"
        )

        print(
            f"  span:    "
            f"{primary['span']}"
        )

        print(
            f"  p95: "
            f"{primary['baseline_p95_ms']:.2f}"
            f" -> "
            f"{primary['candidate_p95_ms']:.2f}"
            f" ms"
        )

    error_regressions = cohort[
        "error_regressions"
    ]

    if error_regressions:
        print()
        print(
            "ERROR-RATE REGRESSIONS"
        )

        for item in error_regressions:
            print(
                f"  "
                f"{item['service']}."
                f"{item['span']}"
            )

            print(
                f"    "
                f"{item['baseline_errors']}/"
                f"{item['baseline_count']} "
                f"("
                f"{item['baseline_error_rate'] * 100:.1f}%"
                f")"
                f" -> "
                f"{item['candidate_errors']}/"
                f"{item['candidate_count']} "
                f"("
                f"{item['candidate_error_rate'] * 100:.1f}%"
                f")"
            )

            print(
                f"    delta: "
                f"+"
                f"{item['delta_percentage_points']:.1f}"
                f" percentage points"
            )

    cp = cohort[
        "critical_path"
    ]

    cp_primary = cp[
        "primary_critical_path_regression"
    ]

    if cp_primary:
        print()
        print(
            "PRIMARY CRITICAL-PATH CONTRIBUTOR"
        )

        print(
            f"  service: "
            f"{cp_primary['service']}"
        )

        print(
            f"  span:    "
            f"{cp_primary['span']}"
        )

        print(
            f"  contribution delta: "
            f"+{cp_primary['delta_ms']:.2f}"
            f" ms p95"
        )

    new_path = [
        item
        for item in cp[
            "contributors"
        ]
        if item[
            "is_new_on_path"
        ]
    ]

    if new_path:
        print()
        print(
            "NEW CRITICAL-PATH CONTRIBUTORS"
        )

        for item in new_path:
            print(
                f"  "
                f"{item['parent']} "
                f"-> "
                f"{item['span']} "
                f"[service="
                f"{item['service']}] "
                f"+{item['delta_ms']:.2f}"
                f" ms"
            )

    print()
    print(
        f"COHORT DECISION: "
        f"{cohort['decision']}"
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "DetTrace "
            "request-shape-aware "
            "OpenTelemetry trace "
            "regression gate"
        )
    )

    parser.add_argument(
        "--baseline",
        required=True,
    )

    parser.add_argument(
        "--candidate",
        required=True,
    )

    parser.add_argument(
        "--regression-threshold-pct",
        type=float,
        default=50.0,
    )

    parser.add_argument(
        "--error-threshold-pp",
        type=float,
        default=5.0,
    )

    parser.add_argument(
        "--output",
        default=(
            "reports/"
            "trace_regression_report.json"
        ),
    )

    args = parser.parse_args()

    baseline_raw = (
        load_raw_traces(
            args.baseline
        )
    )

    candidate_raw = (
        load_raw_traces(
            args.candidate
        )
    )

    report = analyze_shapes(
        baseline_raw,
        candidate_raw,
        latency_threshold_pct=(
            args.regression_threshold_pct
        ),
        error_threshold_pp=(
            args.error_threshold_pp
        ),
    )

    output = Path(
        args.output
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        json.dumps(
            report,
            indent=2,
        )
    )

    print()
    print(
        "DETTRACE TRACE REGRESSION GATE"
    )

    print(
        "=" * 64
    )

    print(
        f"baseline traces:  "
        f"{report['baseline_trace_count']}"
    )

    print(
        f"candidate traces: "
        f"{report['candidate_trace_count']}"
    )

    print(
        f"matched request shapes: "
        f"{report['matched_shape_count']}"
    )

    for cohort in report[
        "cohorts"
    ]:
        print_cohort(
            cohort
        )

    if report[
        "baseline_only_shapes"
    ]:
        print()
        print(
            "BASELINE-ONLY REQUEST SHAPES"
        )

        for shape in report[
            "baseline_only_shapes"
        ]:
            print(
                " ",
                shape[
                    "fingerprint"
                ],
            )

    if report[
        "candidate_only_shapes"
    ]:
        print()
        print(
            "CANDIDATE-ONLY REQUEST SHAPES"
        )

        for shape in report[
            "candidate_only_shapes"
        ]:
            print(
                " ",
                shape[
                    "fingerprint"
                ],
            )

    print()
    print(
        "=" * 64
    )

    print(
        f"CI DECISION: "
        f"{report['decision']}"
    )

    print(
        f"report: "
        f"{output}"
    )

    return (
        1
        if report[
            "decision"
        ] == "FAIL"
        else 0
    )


if __name__ == "__main__":
    sys.exit(
        main()
    )
