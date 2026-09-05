from __future__ import annotations

from trace_regression.normalize import service_name


def find_root_span(trace: list[dict]):
    if not trace:
        return None

    span_ids = {
        span["span_id"]
        for span in trace
    }

    roots = [
        span
        for span in trace
        if (
            not span.get("parent_span_id")
            or span.get("parent_span_id")
            not in span_ids
        )
    ]

    if not roots:
        return None

    def duration_ns(span):
        start = int(
            span.get(
                "start_time_unix_nano",
                0,
            )
            or 0
        )

        end = int(
            span.get(
                "end_time_unix_nano",
                0,
            )
            or 0
        )

        return max(
            0,
            end - start,
        )

    return max(
        roots,
        key=lambda span: (
            duration_ns(span),
            -int(
                span.get(
                    "start_time_unix_nano",
                    0,
                )
                or 0
            ),
        ),
    )


def describe_request_shape(
    trace: list[dict],
):
    root = find_root_span(trace)

    if root is None:
        return {
            "fingerprint": "unknown",
            "service": "unknown",
            "root_span": "unknown",
            "method": None,
            "route": None,
            "explicit_shape": None,
        }

    attributes = dict(
        root.get("attributes")
        or {}
    )

    method = (
        attributes.get(
            "http.request.method"
        )
        or attributes.get(
            "http.method"
        )
    )

    route = (
        attributes.get(
            "http.route"
        )
        or attributes.get(
            "url.path"
        )
    )

    explicit_shape = attributes.get(
        "dettrace.request_shape"
    )

    service = service_name(root)
    root_name = root["name"]

    fingerprint_parts = [
        str(service),
        str(root_name),
        str(method or "-"),
        str(route or "-"),
        str(explicit_shape or "-"),
    ]

    return {
        "fingerprint":
            "|".join(
                fingerprint_parts
            ),
        "service":
            service,
        "root_span":
            root_name,
        "method":
            method,
        "route":
            route,
        "explicit_shape":
            explicit_shape,
    }


def group_traces_by_shape(
    traces: list[list[dict]],
):
    grouped = {}

    for trace in traces:
        descriptor = (
            describe_request_shape(
                trace
            )
        )

        fingerprint = descriptor[
            "fingerprint"
        ]

        if fingerprint not in grouped:
            grouped[fingerprint] = {
                "shape":
                    descriptor,
                "traces":
                    [],
            }

        grouped[
            fingerprint
        ]["traces"].append(
            trace
        )

    return grouped
