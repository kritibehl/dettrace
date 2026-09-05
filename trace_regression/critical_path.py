from __future__ import annotations

from collections import defaultdict

from trace_regression.graph import (
    TraceGraph,
    build_trace_graph,
    semantic_key,
)
from trace_regression.statistics import summarize


def _root_node(graph: TraceGraph):
    if not graph.roots:
        return None

    return max(
        (graph.nodes[root_id] for root_id in graph.roots),
        key=lambda node: (
            node.duration_ms,
            -node.start_ns,
        ),
    )


def _walk_critical_segments(
    graph: TraceGraph,
    node,
):
    """
    Build an interval-derived critical path.

    Starting at the end of a parent interval, select the direct child
    that finishes latest. Move backward through non-overlapping sibling
    intervals.

    Overlapping siblings are not double-counted.

    Time not owned by a selected child is attributed to the parent as
    self-time.
    """

    segments = []

    cursor = node.end_ns

    remaining = [
        graph.nodes[child_id]
        for child_id in node.children
    ]

    while True:
        eligible = [
            child
            for child in remaining
            if (
                child.start_ns < cursor
                and child.end_ns <= cursor
                and child.end_ns > node.start_ns
            )
        ]

        if not eligible:
            break

        child = max(
            eligible,
            key=lambda item: (
                item.end_ns,
                item.start_ns,
            ),
        )

        gap_start = max(
            child.end_ns,
            node.start_ns,
        )

        if cursor > gap_start:
            segments.append(
                {
                    "semantic_key": semantic_key(node, graph),
                    "service": node.service,
                    "span": node.name,
                    "start_ns": gap_start,
                    "end_ns": cursor,
                    "duration_ms": (
                        cursor - gap_start
                    ) / 1_000_000.0,
                    "kind": "self",
                }
            )

        segments.extend(
            _walk_critical_segments(
                graph,
                child,
            )
        )

        cursor = max(
            node.start_ns,
            child.start_ns,
        )

        remaining = [
            item
            for item in remaining
            if (
                item.span_id != child.span_id
                and item.end_ns <= cursor
            )
        ]

    if cursor > node.start_ns:
        segments.append(
            {
                "semantic_key": semantic_key(node, graph),
                "service": node.service,
                "span": node.name,
                "start_ns": node.start_ns,
                "end_ns": cursor,
                "duration_ms": (
                    cursor - node.start_ns
                ) / 1_000_000.0,
                "kind": "self",
            }
        )

    return segments


def analyze_trace(spans: list[dict]):
    graph = build_trace_graph(spans)

    root = _root_node(graph)

    if root is None:
        return {
            "trace_id": graph.trace_id,
            "root_duration_ms": 0.0,
            "critical_path_duration_ms": 0.0,
            "contributions": {},
            "segments": [],
        }

    segments = _walk_critical_segments(
        graph,
        root,
    )

    segments.sort(
        key=lambda item: (
            item["start_ns"],
            item["end_ns"],
        )
    )

    contributions = defaultdict(float)

    for segment in segments:
        contributions[
            segment["semantic_key"]
        ] += segment["duration_ms"]

    return {
        "trace_id": graph.trace_id,
        "root_duration_ms": root.duration_ms,
        "critical_path_duration_ms": sum(
            segment["duration_ms"]
            for segment in segments
        ),
        "contributions": dict(contributions),
        "segments": segments,
    }


def aggregate_critical_paths(
    traces: list[list[dict]],
):
    analyses = [
        analyze_trace(trace)
        for trace in traces
    ]

    all_keys = set()

    for analysis in analyses:
        all_keys.update(
            analysis["contributions"].keys()
        )

    contribution_stats = {}

    for key in all_keys:
        values = [
            analysis["contributions"].get(
                key,
                0.0,
            )
            for analysis in analyses
        ]

        contribution_stats[key] = summarize(values)

    root_stats = summarize(
        [
            analysis["root_duration_ms"]
            for analysis in analyses
        ]
    )

    path_stats = summarize(
        [
            analysis["critical_path_duration_ms"]
            for analysis in analyses
        ]
    )

    return {
        "trace_count": len(analyses),
        "root_duration": root_stats,
        "critical_path_duration": path_stats,
        "contributions": contribution_stats,
    }


def _pct_change(old: float, new: float):
    if old == 0:
        return None

    return ((new - old) / old) * 100.0


def compare_critical_paths(
    baseline_traces: list[list[dict]],
    candidate_traces: list[list[dict]],
    minimum_delta_ms: float = 1.0,
):
    baseline = aggregate_critical_paths(
        baseline_traces
    )

    candidate = aggregate_critical_paths(
        candidate_traces
    )

    all_keys = (
        set(baseline["contributions"])
        | set(candidate["contributions"])
    )

    contributors = []

    for key in all_keys:
        before = baseline[
            "contributions"
        ].get(
            key,
            {
                "count": 0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
            },
        )

        after = candidate[
            "contributions"
        ].get(
            key,
            {
                "count": 0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
            },
        )

        delta_ms = (
            after["p95_ms"]
            - before["p95_ms"]
        )

        if delta_ms < minimum_delta_ms:
            continue

        contributors.append(
            {
                "service": key[0],
                "span": key[1],
                "parent": key[2],
                "baseline_p95_contribution_ms":
                    before["p95_ms"],
                "candidate_p95_contribution_ms":
                    after["p95_ms"],
                "delta_ms": delta_ms,
                "delta_pct": _pct_change(
                    before["p95_ms"],
                    after["p95_ms"],
                ),
                "is_new_on_path":
                    before["p95_ms"] == 0
                    and after["p95_ms"] > 0,
            }
        )

    contributors.sort(
        key=lambda item: item["delta_ms"],
        reverse=True,
    )

    localized = [
        item
        for item in contributors
        if item["parent"] != "ROOT"
    ]

    primary = (
        localized[0]
        if localized
        else (
            contributors[0]
            if contributors
            else None
        )
    )

    baseline_root = baseline[
        "root_duration"
    ]["p95_ms"]

    candidate_root = candidate[
        "root_duration"
    ]["p95_ms"]

    return {
        "method":
            "interval-derived parent/child critical-path contribution analysis",
        "contribution_semantics": (
            "Per-span p95 contribution deltas are computed independently "
            "and are not additive decompositions of the end-to-end p95 delta."
        ),
        "baseline_end_to_end_p95_ms":
            baseline_root,
        "candidate_end_to_end_p95_ms":
            candidate_root,
        "end_to_end_delta_ms":
            candidate_root - baseline_root,
        "contributors": contributors,
        "primary_critical_path_regression":
            primary,
    }
