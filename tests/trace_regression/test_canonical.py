from trace_regression.canonical import (
    canonical_span_key,
    canonicalize_traces,
)
from trace_regression.quality import (
    assess_comparison_quality,
)


def span(
    trace_id,
    span_id,
    parent_id,
    service,
    name,
    *,
    attrs=None,
):
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_id,
        "name": name,
        "duration_ms": 10.0,
        "status": "UNSET",
        "attributes": attrs or {},
        "resource": {
            "service.name": service,
            "service.instance.id": f"{service}-volatile-id",
            "container.id": f"{service}-container",
        },
    }


def test_trace_and_span_ids_do_not_change_topology():
    left = [
        span(
            "trace-a",
            "root-a",
            "",
            "frontend",
            "GET /cart",
            attrs={
                "http.request.method": "GET",
                "http.route": "/cart",
            },
        ),
        span(
            "trace-a",
            "child-a",
            "root-a",
            "cart",
            "GetCart",
            attrs={
                "rpc.system": "grpc",
                "rpc.service": "oteldemo.CartService",
                "rpc.method": "GetCart",
                "server.address": "cart",
            },
        ),
    ]

    right = [
        span(
            "completely-different-trace",
            "different-root",
            "",
            "frontend",
            "GET /cart",
            attrs={
                "http.request.method": "GET",
                "http.route": "/cart",
            },
        ),
        span(
            "completely-different-trace",
            "different-child",
            "different-root",
            "cart",
            "GetCart",
            attrs={
                "rpc.system": "grpc",
                "rpc.service": "oteldemo.CartService",
                "rpc.method": "GetCart",
                "server.address": "cart",
            },
        ),
    ]

    assert (
        canonicalize_traces(left)[0].topology_signature()
        == canonicalize_traces(right)[0].topology_signature()
    )


def test_parallel_child_order_is_irrelevant():
    root = span(
        "trace",
        "root",
        "",
        "checkout",
        "PlaceOrder",
    )

    payment = span(
        "trace",
        "payment",
        "root",
        "payment",
        "Charge",
    )

    shipping = span(
        "trace",
        "shipping",
        "root",
        "shipping",
        "ShipOrder",
    )

    a = canonicalize_traces(
        [root, payment, shipping]
    )[0]

    b = canonicalize_traces(
        [shipping, root, payment]
    )[0]

    assert (
        a.topology_signature()
        == b.topology_signature()
    )


def test_repeated_call_changes_edge_multiplicity():
    baseline = [
        span(
            "trace",
            "root",
            "",
            "checkout",
            "PlaceOrder",
        ),
        span(
            "trace",
            "cart-1",
            "root",
            "cart",
            "GetCart",
        ),
    ]

    candidate = baseline + [
        span(
            "trace",
            "cart-2",
            "root",
            "cart",
            "GetCart",
        )
    ]

    left = canonicalize_traces(
        baseline
    )[0]

    right = canonicalize_traces(
        candidate
    )[0]

    assert (
        left.topology_signature()
        != right.topology_signature()
    )

    assert any(
        count == 2
        for _, _, count in right.edges
    )


def test_old_and_new_rpc_semconv_match():
    old = span(
        "trace-a",
        "a",
        "",
        "frontend",
        "rpc",
        attrs={
            "rpc.system": "grpc",
            "rpc.service": "oteldemo.ProductCatalogService",
            "rpc.method": "GetProduct",
        },
    )

    new = span(
        "trace-b",
        "b",
        "",
        "frontend",
        "rpc",
        attrs={
            "rpc.system.name": "grpc",
            "rpc.method": (
                "oteldemo.ProductCatalogService/"
                "GetProduct"
            ),
        },
    )

    assert (
        canonical_span_key(old).operation
        == canonical_span_key(new).operation
    )


def test_ephemeral_ip_is_not_structural_identity():
    item = span(
        "trace",
        "span",
        "",
        "frontend",
        "GetProduct",
        attrs={
            "rpc.system.name": "grpc",
            "rpc.method": (
                "oteldemo.ProductCatalogService/"
                "GetProduct"
            ),
            "server.address": "172.21.0.16",
        },
    )

    assert (
        canonical_span_key(item).target
        == ""
    )


def test_http_route_is_semantic_operation():
    item = span(
        "trace",
        "span",
        "",
        "frontend",
        "random raw name",
        attrs={
            "http.request.method": "POST",
            "http.route": "/api/checkout",
        },
    )

    assert (
        canonical_span_key(item).operation
        == "POST /api/checkout"
    )


def test_900_vs_6_is_inconclusive():
    result = assess_comparison_quality(
        900,
        6,
    )

    assert result.decision == "INCONCLUSIVE"
    assert (
        result.reason
        == "insufficient_candidate_samples"
    )


def test_500_vs_470_is_ready():
    result = assess_comparison_quality(
        500,
        470,
    )

    assert result.decision == "READY"
    assert (
        result.reason
        == "sufficient_samples"
    )
