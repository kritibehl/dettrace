from __future__ import annotations

from collections import Counter
from collections import defaultdict
from dataclasses import dataclass
from ipaddress import ip_address
from typing import Any
from typing import Iterable


_KIND_NAMES = {
    0: "UNSPECIFIED",
    1: "INTERNAL",
    2: "SERVER",
    3: "CLIENT",
    4: "PRODUCER",
    5: "CONSUMER",
}


@dataclass(
    frozen=True,
    order=True,
)
class CanonicalSpanKey:
    service: str
    operation: str
    kind: str
    protocol: str
    target: str


@dataclass(
    frozen=True,
)
class CanonicalTrace:
    trace_id: str
    request_shape: str
    nodes: tuple[
        tuple[
            CanonicalSpanKey,
            int,
        ],
        ...,
    ]
    edges: tuple[
        tuple[
            CanonicalSpanKey,
            CanonicalSpanKey,
            int,
        ],
        ...,
    ]
    roots: tuple[
        CanonicalSpanKey,
        ...,
    ]
    duration_ms: float
    error_count: int
    orphan_parent_count: int

    def topology_signature(
        self,
    ):
        return (
            self.request_shape,
            self.nodes,
            self.edges,
            self.roots,
        )


def _decode_any(
    value: Any,
):
    if not isinstance(
        value,
        dict,
    ):
        return value

    for key in (
        "stringValue",
        "boolValue",
        "intValue",
        "doubleValue",
        "bytesValue",
    ):
        if key in value:
            return value[key]

    if "arrayValue" in value:
        return [
            _decode_any(item)
            for item in value[
                "arrayValue"
            ].get(
                "values",
                [],
            )
        ]

    return value


def _attribute_list_to_dict(
    items,
):
    result = {}

    if not isinstance(
        items,
        list,
    ):
        return result

    for item in items:
        if not isinstance(
            item,
            dict,
        ):
            continue

        key = item.get(
            "key"
        )

        if not key:
            continue

        result[key] = _decode_any(
            item.get(
                "value",
                {},
            )
        )

    return result


def span_attributes(
    span: dict,
) -> dict:
    value = span.get(
        "attributes",
        {},
    )

    if isinstance(
        value,
        dict,
    ):
        return value

    return _attribute_list_to_dict(
        value
    )


def resource_attributes(
    span: dict,
) -> dict:
    for field in (
        "resource_attributes",
        "resource_attrs",
        "resource",
    ):
        value = span.get(
            field
        )

        if not isinstance(
            value,
            dict,
        ):
            continue

        nested = value.get(
            "attributes"
        )

        if isinstance(
            nested,
            dict,
        ):
            return nested

        if isinstance(
            nested,
            list,
        ):
            return (
                _attribute_list_to_dict(
                    nested
                )
            )

        return value

    return {}


def service_name(
    span: dict,
) -> str:
    for field in (
        "service_name",
        "service",
    ):
        value = span.get(
            field
        )

        if value:
            return str(
                value
            )

    resource = resource_attributes(
        span
    )

    value = resource.get(
        "service.name"
    )

    if value:
        return str(
            value
        )

    attrs = span_attributes(
        span
    )

    value = attrs.get(
        "service.name"
    )

    if value:
        return str(
            value
        )

    return "unknown"


def _kind(
    span: dict,
) -> str:
    value = span.get(
        "kind",
        "UNSPECIFIED",
    )

    if isinstance(
        value,
        int,
    ):
        return _KIND_NAMES.get(
            value,
            str(value),
        )

    result = str(
        value
    ).upper()

    if result.startswith(
        "SPAN_KIND_"
    ):
        result = result[
            len(
                "SPAN_KIND_"
            ):
        ]

    return result


def _first(
    attrs: dict,
    *keys: str,
):
    for key in keys:
        value = attrs.get(
            key
        )

        if value not in (
            None,
            "",
        ):
            return value

    return None


def semantic_protocol(
    span: dict,
) -> str:
    attrs = span_attributes(
        span
    )

    if _first(
        attrs,
        "rpc.system.name",
        "rpc.system",
    ):
        return "rpc"

    if _first(
        attrs,
        "http.route",
        "http.request.method",
        "http.method",
    ):
        return "http"

    if _first(
        attrs,
        "messaging.system",
    ):
        return "messaging"

    if _first(
        attrs,
        "db.system.name",
        "db.system",
    ):
        return "db"

    return "internal"


def semantic_operation(
    span: dict,
) -> str:
    attrs = span_attributes(
        span
    )

    route = _first(
        attrs,
        "http.route",
    )

    method = _first(
        attrs,
        "http.request.method",
        "http.method",
    )

    if route:
        if method:
            return (
                f"{str(method).upper()} "
                f"{route}"
            )

        return str(
            route
        )

    rpc_method = _first(
        attrs,
        "rpc.method",
        "grpc.method",
    )

    rpc_service = _first(
        attrs,
        "rpc.service",
    )

    if rpc_method:
        rpc_method = str(
            rpc_method
        )

        if "/" in rpc_method:
            return rpc_method

        if rpc_service:
            return (
                f"{rpc_service}/"
                f"{rpc_method}"
            )

        return rpc_method

    messaging_op = _first(
        attrs,
        "messaging.operation.name",
    )

    destination = _first(
        attrs,
        "messaging.destination.name",
    )

    if messaging_op:
        if destination:
            return (
                f"{messaging_op} "
                f"{destination}"
            )

        return str(
            messaging_op
        )

    return str(
        span.get(
            "name",
            "unknown",
        )
    )


def _stable_host(
    value,
) -> str:
    if not value:
        return ""

    value = str(
        value
    )

    if value in (
        "localhost",
        "127.0.0.1",
        "::1",
    ):
        return ""

    try:
        ip_address(
            value
        )

        return ""
    except ValueError:
        return value


def semantic_target(
    span: dict,
) -> str:
    attrs = span_attributes(
        span
    )

    target = _first(
        attrs,
        "server.address",
        "peer.service",
        "net.peer.name",
    )

    stable = _stable_host(
        target
    )

    if stable:
        return stable

    rpc_service = _first(
        attrs,
        "rpc.service",
    )

    if rpc_service:
        return str(
            rpc_service
        )

    return ""


def canonical_span_key(
    span: dict,
) -> CanonicalSpanKey:
    return CanonicalSpanKey(
        service=service_name(
            span
        ),
        operation=semantic_operation(
            span
        ),
        kind=_kind(
            span
        ),
        protocol=semantic_protocol(
            span
        ),
        target=semantic_target(
            span
        ),
    )


def span_is_error(
    span: dict,
) -> bool:
    status = span.get(
        "status",
        "",
    )

    if isinstance(
        status,
        dict,
    ):
        status = (
            status.get(
                "code"
            )
            or status.get(
                "status_code"
            )
            or ""
        )

    if "ERROR" in str(
        status
    ).upper():
        return True

    attrs = span_attributes(
        span
    )

    if attrs.get(
        "error.type"
    ):
        return True

    error = attrs.get(
        "error"
    )

    if error not in (
        None,
        "",
        False,
        0,
        "false",
        "False",
    ):
        return True

    http_status = _first(
        attrs,
        "http.response.status_code",
        "http.status_code",
    )

    try:
        if (
            http_status is not None
            and int(
                http_status
            ) >= 500
        ):
            return True
    except (
        TypeError,
        ValueError,
    ):
        pass

    grpc_status = _first(
        attrs,
        "rpc.grpc.status_code",
        "grpc.status_code",
    )

    try:
        if (
            grpc_status is not None
            and int(
                grpc_status
            ) != 0
        ):
            return True
    except (
        TypeError,
        ValueError,
    ):
        pass

    return False


def _duration_ms(
    span: dict,
) -> float:
    value = span.get(
        "duration_ms"
    )

    if value is not None:
        try:
            return float(
                value
            )
        except (
            TypeError,
            ValueError,
        ):
            pass

    start = (
        span.get(
            "start_time_unix_nano"
        )
        or span.get(
            "startTimeUnixNano"
        )
    )

    end = (
        span.get(
            "end_time_unix_nano"
        )
        or span.get(
            "endTimeUnixNano"
        )
    )

    try:
        if (
            start is not None
            and end is not None
        ):
            return (
                int(end)
                - int(start)
            ) / 1_000_000
    except (
        TypeError,
        ValueError,
    ):
        pass

    return 0.0


def _request_shape(
    roots: list[
        dict
    ],
) -> str:
    if not roots:
        return "unknown"

    server_roots = [
        root
        for root in roots
        if _kind(
            root
        ) == "SERVER"
    ]

    candidates = (
        server_roots
        or roots
    )

    values = sorted(
        semantic_operation(
            root
        )
        for root in candidates
    )

    return values[0]


def canonicalize_trace(
    trace_id: str,
    spans: Iterable[
        dict
    ],
) -> CanonicalTrace:
    spans = list(
        spans
    )

    by_id = {}

    for span in spans:
        span_id = (
            span.get(
                "span_id"
            )
            or span.get(
                "spanId"
            )
            or ""
        )

        if span_id:
            by_id[
                str(span_id)
            ] = span

    nodes = Counter()
    edges = Counter()
    roots = []

    orphan_parent_count = 0

    for span in spans:
        key = canonical_span_key(
            span
        )

        nodes[
            key
        ] += 1

        parent_id = (
            span.get(
                "parent_span_id"
            )
            or span.get(
                "parentSpanId"
            )
            or ""
        )

        parent_id = str(
            parent_id
        )

        if (
            parent_id
            and parent_id in by_id
        ):
            parent_key = (
                canonical_span_key(
                    by_id[
                        parent_id
                    ]
                )
            )

            edges[
                (
                    parent_key,
                    key,
                )
            ] += 1
        else:
            roots.append(
                span
            )

            if parent_id:
                orphan_parent_count += 1

    root_keys = tuple(
        sorted(
            canonical_span_key(
                root
            )
            for root in roots
        )
    )

    if roots:
        duration_ms = max(
            _duration_ms(
                root
            )
            for root in roots
        )
    else:
        duration_ms = max(
            (
                _duration_ms(
                    span
                )
                for span in spans
            ),
            default=0.0,
        )

    return CanonicalTrace(
        trace_id=str(
            trace_id
        ),
        request_shape=_request_shape(
            roots
        ),
        nodes=tuple(
            sorted(
                (
                    key,
                    count,
                )
                for key, count
                in nodes.items()
            )
        ),
        edges=tuple(
            sorted(
                (
                    parent,
                    child,
                    count,
                )
                for (
                    parent,
                    child,
                ), count
                in edges.items()
            )
        ),
        roots=root_keys,
        duration_ms=duration_ms,
        error_count=sum(
            1
            for span in spans
            if span_is_error(
                span
            )
        ),
        orphan_parent_count=(
            orphan_parent_count
        ),
    )


def canonicalize_traces(
    spans: Iterable[
        dict
    ],
) -> list[
    CanonicalTrace
]:
    grouped = defaultdict(
        list
    )

    for span in spans:
        trace_id = (
            span.get(
                "trace_id"
            )
            or span.get(
                "traceId"
            )
        )

        if not trace_id:
            continue

        grouped[
            str(trace_id)
        ].append(
            span
        )

    return [
        canonicalize_trace(
            trace_id,
            grouped[
                trace_id
            ],
        )
        for trace_id in sorted(
            grouped
        )
    ]
