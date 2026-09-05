#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from trace_regression.compare import compare_traces
from trace_regression.critical_path import (
    compare_critical_paths,
)
from trace_regression.normalize import (
    group_by_trace,
    normalize_trace,
)


def load_raw_traces(path):
    spans = json.loads(
        Path(path).read_text()
    )

    grouped = group_by_trace(spans)

    return list(grouped.values())


def normalize_traces(raw_traces):
    return [
        normalize_trace(trace_spans)
        for trace_spans in raw_traces
    ]


def tuple_to_dict(value):
    return {
        "service": value[0],
        "span": value[1],
        "parent": value[2],
    }


def choose_primary_localized_regression(
    regressions,
):
    localized = [
        regression
        for regression in regressions
        if regression["parent"] != "ROOT"
    ]

    candidates = localized or regressions

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
        if regression["parent"] == "ROOT"
    ]

    if not roots:
        return None

    return max(
        roots,
        key=lambda item: item["delta_ms"],
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "DetTrace OpenTelemetry "
            "trace regression gate"
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
        "--output",
        default=(
            "reports/"
            "trace_regression_report.json"
        ),
    )

    args = parser.parse_args()

    baseline_raw = load_raw_traces(
        args.baseline
    )

    candidate_raw = load_raw_traces(
        args.candidate
    )

    baseline = normalize_traces(
        baseline_raw
    )

    candidate = normalize_traces(
        candidate_raw
    )

    comparison = compare_traces(
        baseline,
        candidate,
        regression_threshold_pct=(
            args.regression_threshold_pct
        ),
    )

    critical_path = compare_critical_paths(
        baseline_raw,
        candidate_raw,
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

    report = {
        "baseline_trace_count":
            len(baseline),
        "candidate_trace_count":
            len(candidate),
        "threshold_pct":
            args.regression_threshold_pct,
        "added_spans": [
            tuple_to_dict(item)
            for item in comparison[
                "added_spans"
            ]
        ],
        "removed_spans": [
            tuple_to_dict(item)
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
        "critical_path":
            critical_path,
        "decision": (
            "FAIL"
            if (
                regressions
                or comparison["added_spans"]
            )
            else "PASS"
        ),
    }

    output = Path(args.output)

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
    print("=" * 40)

    print(
        f"baseline traces:  "
        f"{len(baseline)}"
    )

    print(
        f"candidate traces: "
        f"{len(candidate)}"
    )

    if report["added_spans"]:
        print()
        print("STRUCTURAL CHANGES")

        for item in report[
            "added_spans"
        ]:
            print(
                f"  {item['parent']} "
                f"-> {item['span']} "
                f"[service="
                f"{item['service']}]"
            )

    if end_to_end:
        print()
        print("END-TO-END REGRESSION")

        print(
            f"  span:      "
            f"{end_to_end['span']}"
        )

        print(
            f"  baseline:  "
            f"{end_to_end['baseline_p95_ms']:.2f} "
            f"ms p95"
        )

        print(
            f"  candidate: "
            f"{end_to_end['candidate_p95_ms']:.2f} "
            f"ms p95"
        )

        print(
            f"  delta:     "
            f"+{end_to_end['delta_ms']:.2f} ms"
        )

        print(
            f"  change:    "
            f"+{end_to_end['delta_pct']:.1f}%"
        )

    if primary:
        print()
        print(
            "PRIMARY LOCALIZED REGRESSION"
        )

        print(
            f"  service:   "
            f"{primary['service']}"
        )

        print(
            f"  span:      "
            f"{primary['span']}"
        )

        print(
            f"  parent:    "
            f"{primary['parent']}"
        )

        print(
            f"  baseline:  "
            f"{primary['baseline_p95_ms']:.2f} "
            f"ms p95"
        )

        print(
            f"  candidate: "
            f"{primary['candidate_p95_ms']:.2f} "
            f"ms p95"
        )

        print(
            f"  delta:     "
            f"+{primary['delta_ms']:.2f} ms"
        )

        print(
            f"  change:    "
            f"+{primary['delta_pct']:.1f}%"
        )

    cp_primary = critical_path[
        "primary_critical_path_regression"
    ]

    print()
    print("CRITICAL-PATH ANALYSIS")

    print(
        f"  baseline end-to-end p95:  "
        f"{critical_path['baseline_end_to_end_p95_ms']:.2f} ms"
    )

    print(
        f"  candidate end-to-end p95: "
        f"{critical_path['candidate_end_to_end_p95_ms']:.2f} ms"
    )

    print(
        f"  end-to-end delta:          "
        f"+{critical_path['end_to_end_delta_ms']:.2f} ms"
    )

    if cp_primary:
        print()
        print(
            "PRIMARY CRITICAL-PATH CONTRIBUTOR"
        )

        print(
            f"  service:   "
            f"{cp_primary['service']}"
        )

        print(
            f"  span:      "
            f"{cp_primary['span']}"
        )

        print(
            f"  parent:    "
            f"{cp_primary['parent']}"
        )

        print(
            f"  baseline contribution: "
            f"{cp_primary['baseline_p95_contribution_ms']:.2f} ms"
        )

        print(
            f"  candidate contribution: "
            f"{cp_primary['candidate_p95_contribution_ms']:.2f} ms"
        )

        print(
            f"  contribution delta:    "
            f"+{cp_primary['delta_ms']:.2f} ms"
        )

    new_path_spans = [
        item
        for item in critical_path[
            "contributors"
        ]
        if item["is_new_on_path"]
    ]

    if new_path_spans:
        print()
        print(
            "NEW CRITICAL-PATH CONTRIBUTORS"
        )

        for item in new_path_spans:
            print(
                f"  {item['parent']} "
                f"-> {item['span']} "
                f"[service={item['service']}] "
                f"+{item['delta_ms']:.2f} ms"
            )

    print()
    print(
        f"CI DECISION: "
        f"{report['decision']}"
    )

    print(
        f"report: {output}"
    )

    return (
        1
        if report["decision"] == "FAIL"
        else 0
    )


if __name__ == "__main__":
    sys.exit(main())
