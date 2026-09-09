from __future__ import annotations

from collections import defaultdict
from math import ceil

from trace_regression.canonical import (
    CanonicalSpanKey,
    canonicalize_traces,
)
from trace_regression.quality import (
    assess_comparison_quality,
)


def _percentile_count(
    values,
    percentile=0.95,
):
    values = sorted(values)

    if not values:
        return 0

    index = max(
        0,
        min(
            len(values) - 1,
            ceil(
                percentile
                * len(values)
            )
            - 1,
        ),
    )

    return values[index]


def _key_dict(
    key: CanonicalSpanKey,
):
    return {
        "service": key.service,
        "operation": key.operation,
        "kind": key.kind,
        "protocol": key.protocol,
        "target": key.target,
    }


def compare_canonical_multiplicity(
    baseline_spans,
    candidate_spans,
):
    baseline = canonicalize_traces(
        baseline_spans
    )

    candidate = canonicalize_traces(
        candidate_spans
    )

    baseline_groups = defaultdict(
        list
    )

    candidate_groups = defaultdict(
        list
    )

    for trace in baseline:
        baseline_groups[
            trace.request_shape
        ].append(trace)

    for trace in candidate:
        candidate_groups[
            trace.request_shape
        ].append(trace)

    regressions = []
    cohorts = []

    for shape in sorted(
        set(baseline_groups)
        & set(candidate_groups)
    ):
        baseline_traces = (
            baseline_groups[shape]
        )

        candidate_traces = (
            candidate_groups[shape]
        )

        quality = (
            assess_comparison_quality(
                len(baseline_traces),
                len(candidate_traces),
            )
        )

        cohort = {
            "request_shape":
                shape,
            "quality":
                quality.to_dict(),
            "multiplicity_regressions":
                [],
        }

        if (
            quality.decision
            != "READY"
        ):
            cohorts.append(cohort)
            continue

        edge_keys = set()

        for trace in (
            baseline_traces
            + candidate_traces
        ):
            edge_keys.update(
                (
                    parent,
                    child,
                )
                for (
                    parent,
                    child,
                    count,
                )
                in trace.edges
            )

        for parent, child in sorted(
            edge_keys
        ):
            baseline_values = []

            candidate_values = []

            for trace in baseline_traces:
                edge_map = {
                    (
                        edge_parent,
                        edge_child,
                    ): count
                    for (
                        edge_parent,
                        edge_child,
                        count,
                    )
                    in trace.edges
                }

                baseline_values.append(
                    edge_map.get(
                        (
                            parent,
                            child,
                        ),
                        0,
                    )
                )

            for trace in candidate_traces:
                edge_map = {
                    (
                        edge_parent,
                        edge_child,
                    ): count
                    for (
                        edge_parent,
                        edge_child,
                        count,
                    )
                    in trace.edges
                }

                candidate_values.append(
                    edge_map.get(
                        (
                            parent,
                            child,
                        ),
                        0,
                    )
                )

            before = _percentile_count(
                baseline_values
            )

            after = _percentile_count(
                candidate_values
            )

            if (
                before >= 1
                and after > before
            ):
                item = {
                    "request_shape":
                        shape,
                    "parent":
                        _key_dict(parent),
                    "child":
                        _key_dict(child),
                    "baseline_p95_count":
                        before,
                    "candidate_p95_count":
                        after,
                    "delta":
                        after - before,
                }

                regressions.append(
                    item
                )

                cohort[
                    "multiplicity_regressions"
                ].append(item)

        cohorts.append(cohort)

    return {
        "baseline_canonical_traces":
            len(baseline),
        "candidate_canonical_traces":
            len(candidate),
        "baseline_orphan_parent_traces":
            sum(
                1
                for trace in baseline
                if trace.orphan_parent_count
            ),
        "candidate_orphan_parent_traces":
            sum(
                1
                for trace in candidate
                if trace.orphan_parent_count
            ),
        "cohorts":
            cohorts,
        "multiplicity_regressions":
            regressions,
    }
