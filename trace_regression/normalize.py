from __future__ import annotations

from collections import defaultdict


def service_name(span):
    attrs = span.get("attributes", {})

    return (
        attrs.get("service.name")
        or span.get("resource", {}).get("service.name")
        or "unknown"
    )


def group_by_trace(spans):
    grouped = defaultdict(list)

    for span in spans:
        grouped[span["trace_id"]].append(span)

    return dict(grouped)


def semantic_key(span, parent_name=None):
    return (
        service_name(span),
        span["name"],
        parent_name or "ROOT",
    )


def normalize_trace(spans):
    by_id = {
        span["span_id"]: span
        for span in spans
    }

    normalized = []

    for span in spans:
        parent = by_id.get(span.get("parent_span_id"))

        parent_name = (
            parent["name"]
            if parent is not None
            else None
        )

        normalized.append(
            {
                "service": service_name(span),
                "name": span["name"],
                "parent_name": parent_name,
                "duration_ms": float(span["duration_ms"] or 0),
                "status": span.get("status", "UNSET"),
                "semantic_key": semantic_key(span, parent_name),
            }
        )

    return normalized
