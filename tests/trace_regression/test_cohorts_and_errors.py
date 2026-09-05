import pytest

from trace_regression.analyzer import (
    analyze_cohort,
)
from trace_regression.cohorts import (
    group_traces_by_shape,
)
from trace_regression.errors import (
    compare_error_rates,
)
from trace_regression.normalize import (
    normalize_trace,
)


def raw_span(
    trace_id,
    span_id,
    parent_id,
    name,
    service,
    start_ms,
    end_ms,
    status="OK",
    method=None,
    route=None,
    shape=None,
):
    attributes = {
        "service.name":
            service,
    }

    if method is not None:
        attributes[
            "http.request.method"
        ] = method

    if route is not None:
        attributes[
            "http.route"
        ] = route

    if shape is not None:
        attributes[
            "dettrace.request_shape"
        ] = shape

    return {
        "trace_id":
            trace_id,
        "span_id":
            span_id,
        "parent_span_id":
            parent_id,
        "name":
            name,
        "start_time_unix_nano":
            int(
                start_ms
                * 1_000_000
            ),
        "end_time_unix_nano":
            int(
                end_ms
                * 1_000_000
            ),
        "duration_ms":
            end_ms
            - start_ms,
        "status":
            status,
        "attributes":
            attributes,
        "resource":
            {},
    }


def checkout_trace(
    trace_id,
    duration=20,
    error=False,
):
    return [
        raw_span(
            trace_id,
            f"{trace_id}-root",
            None,
            "checkout.request",
            "checkout",
            0,
            duration,
            status=(
                "ERROR"
                if error
                else "OK"
            ),
            method="POST",
            route="/checkout",
            shape="checkout",
        )
    ]


def health_trace(
    trace_id,
    duration=5,
):
    return [
        raw_span(
            trace_id,
            f"{trace_id}-root",
            None,
            "health.request",
            "checkout",
            0,
            duration,
            status="OK",
            method="GET",
            route="/health",
            shape="health",
        )
    ]


def test_request_shapes_are_separated():
    grouped = (
        group_traces_by_shape(
            [
                checkout_trace(
                    "c1"
                ),
                health_trace(
                    "h1"
                ),
            ]
        )
    )

    assert len(
        grouped
    ) == 2

    routes = {
        value[
            "shape"
        ]["route"]
        for value in grouped.values()
    }

    assert routes == {
        "/checkout",
        "/health",
    }


def test_error_rate_regression_is_percentage_point_based():
    baseline = [
        normalize_trace(
            checkout_trace(
                f"b{i}",
                error=False,
            )
        )
        for i in range(10)
    ]

    candidate = [
        normalize_trace(
            checkout_trace(
                f"c{i}",
                error=(
                    i < 2
                ),
            )
        )
        for i in range(10)
    ]

    result = (
        compare_error_rates(
            baseline,
            candidate,
            threshold_percentage_points=5,
        )
    )

    assert len(
        result[
            "regressions"
        ]
    ) == 1

    regression = result[
        "regressions"
    ][0]

    assert regression[
        "baseline_error_rate"
    ] == pytest.approx(
        0.0
    )

    assert regression[
        "candidate_error_rate"
    ] == pytest.approx(
        0.2
    )

    assert regression[
        "delta_percentage_points"
    ] == pytest.approx(
        20.0
    )


def test_cohort_analysis_detects_error_regression():
    baseline = [
        checkout_trace(
            f"b{i}",
            duration=20,
            error=False,
        )
        for i in range(10)
    ]

    candidate = [
        checkout_trace(
            f"c{i}",
            duration=20,
            error=(
                i < 2
            ),
        )
        for i in range(10)
    ]

    result = analyze_cohort(
        baseline,
        candidate,
        regression_threshold_pct=50,
        error_threshold_pp=5,
    )

    assert result[
        "decision"
    ] == "FAIL"

    assert len(
        result[
            "error_regressions"
        ]
    ) == 1


def test_health_and_checkout_can_be_analyzed_independently():
    checkout_baseline = [
        checkout_trace(
            f"cb{i}",
            duration=20,
        )
        for i in range(10)
    ]

    checkout_candidate = [
        checkout_trace(
            f"cc{i}",
            duration=50,
        )
        for i in range(10)
    ]

    health_baseline = [
        health_trace(
            f"hb{i}",
            duration=5,
        )
        for i in range(10)
    ]

    health_candidate = [
        health_trace(
            f"hc{i}",
            duration=5,
        )
        for i in range(10)
    ]

    checkout_result = (
        analyze_cohort(
            checkout_baseline,
            checkout_candidate,
            regression_threshold_pct=50,
            error_threshold_pp=5,
        )
    )

    health_result = (
        analyze_cohort(
            health_baseline,
            health_candidate,
            regression_threshold_pct=50,
            error_threshold_pp=5,
        )
    )

    assert checkout_result[
        "decision"
    ] == "FAIL"

    assert health_result[
        "decision"
    ] == "PASS"
