from trace_regression.compare import compare_traces


def span(
    service,
    name,
    parent,
    duration,
):
    return {
        "service": service,
        "name": name,
        "parent_name": parent,
        "duration_ms": duration,
        "status": "OK",
        "semantic_key": (
            service,
            name,
            parent or "ROOT",
        ),
    }


def test_detects_latency_regression():
    baseline = [
        [
            span(
                "inventory",
                "inventory.reserve",
                "checkout.request",
                20,
            )
        ]
        for _ in range(10)
    ]

    candidate = [
        [
            span(
                "inventory",
                "inventory.reserve",
                "checkout.request",
                100,
            )
        ]
        for _ in range(10)
    ]

    result = compare_traces(
        baseline,
        candidate,
        regression_threshold_pct=50,
    )

    assert len(result["regressions"]) == 1

    regression = result["regressions"][0]

    assert regression["service"] == "inventory"
    assert regression["span"] == "inventory.reserve"
    assert regression["delta_pct"] == 400.0


def test_detects_new_span():
    baseline = [
        [
            span(
                "inventory",
                "inventory.reserve",
                "checkout.request",
                20,
            )
        ]
    ]

    candidate = [
        [
            span(
                "inventory",
                "inventory.reserve",
                "checkout.request",
                20,
            ),
            span(
                "redis",
                "redis.lookup",
                "inventory.reserve",
                10,
            ),
        ]
    ]

    result = compare_traces(
        baseline,
        candidate,
    )

    assert (
        "redis",
        "redis.lookup",
        "inventory.reserve",
    ) in result["added_spans"]


def test_root_regression_is_not_treated_as_localized_root_cause():
    from trace_regression.cli import (
        choose_primary_localized_regression,
    )

    regressions = [
        {
            "service": "checkout",
            "span": "checkout.request",
            "parent": "ROOT",
            "baseline_p95_ms": 50.0,
            "candidate_p95_ms": 160.0,
            "delta_ms": 110.0,
            "delta_pct": 220.0,
        },
        {
            "service": "inventory",
            "span": "inventory.reserve",
            "parent": "checkout.request",
            "baseline_p95_ms": 28.0,
            "candidate_p95_ms": 135.0,
            "delta_ms": 107.0,
            "delta_pct": 382.1,
        },
    ]

    primary = choose_primary_localized_regression(regressions)

    assert primary["service"] == "inventory"
    assert primary["span"] == "inventory.reserve"
