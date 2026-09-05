#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from trace_regression.compare import compare_traces
from trace_regression.normalize import group_by_trace, normalize_trace


def load_normalized(path):
    spans = json.loads(Path(path).read_text())
    traces = group_by_trace(spans)

    return [
        normalize_trace(trace_spans)
        for trace_spans in traces.values()
    ]


def tuple_to_dict(value):
    return {
        "service": value[0],
        "span": value[1],
        "parent": value[2],
    }


def choose_primary_localized_regression(regressions):
    """
    Select the strongest non-root regression.

    This is intentionally NOT called a causal first divergence yet.
    Proper causal ordering requires explicit span-DAG and critical-path
    analysis, which is a later DetTrace milestone.
    """

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


def find_end_to_end_regression(regressions):
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
        description="DetTrace OpenTelemetry trace regression gate"
    )

    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)

    parser.add_argument(
        "--regression-threshold-pct",
        type=float,
        default=50.0,
    )

    parser.add_argument(
        "--output",
        default="reports/trace_regression_report.json",
    )

    args = parser.parse_args()

    baseline = load_normalized(args.baseline)
    candidate = load_normalized(args.candidate)

    comparison = compare_traces(
        baseline,
        candidate,
        regression_threshold_pct=args.regression_threshold_pct,
    )

    regressions = comparison["regressions"]

    primary = choose_primary_localized_regression(regressions)
    end_to_end = find_end_to_end_regression(regressions)

    report = {
        "baseline_trace_count": len(baseline),
        "candidate_trace_count": len(candidate),
        "threshold_pct": args.regression_threshold_pct,
        "added_spans": [
            tuple_to_dict(item)
            for item in comparison["added_spans"]
        ],
        "removed_spans": [
            tuple_to_dict(item)
            for item in comparison["removed_spans"]
        ],
        "regressions": regressions,
        "primary_localized_regression": primary,
        "end_to_end_regression": end_to_end,
        "decision": (
            "FAIL"
            if regressions or comparison["added_spans"]
            else "PASS"
        ),
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))

    print()
    print("DETTRACE TRACE REGRESSION GATE")
    print("=" * 40)

    print(f"baseline traces:  {len(baseline)}")
    print(f"candidate traces: {len(candidate)}")

    if report["added_spans"]:
        print()
        print("STRUCTURAL CHANGES")

        for item in report["added_spans"]:
            print(
                f"  {item['parent']} -> {item['span']} "
                f"[service={item['service']}]"
            )

    if end_to_end:
        print()
        print("END-TO-END REGRESSION")
        print(
            f"  span:      {end_to_end['span']}"
        )
        print(
            f"  baseline:  {end_to_end['baseline_p95_ms']:.2f} ms p95"
        )
        print(
            f"  candidate: {end_to_end['candidate_p95_ms']:.2f} ms p95"
        )
        print(
            f"  delta:     +{end_to_end['delta_ms']:.2f} ms"
        )
        print(
            f"  change:    +{end_to_end['delta_pct']:.1f}%"
        )

    if primary:
        print()
        print("PRIMARY LOCALIZED REGRESSION")
        print(
            f"  service:   {primary['service']}"
        )
        print(
            f"  span:      {primary['span']}"
        )
        print(
            f"  parent:    {primary['parent']}"
        )
        print(
            f"  baseline:  {primary['baseline_p95_ms']:.2f} ms p95"
        )
        print(
            f"  candidate: {primary['candidate_p95_ms']:.2f} ms p95"
        )
        print(
            f"  delta:     +{primary['delta_ms']:.2f} ms"
        )
        print(
            f"  change:    +{primary['delta_pct']:.1f}%"
        )

    print()
    print(f"CI DECISION: {report['decision']}")
    print(f"report: {output}")

    return 1 if report["decision"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
