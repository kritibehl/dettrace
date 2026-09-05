import pytest

from trace_regression.critical_path import (
    analyze_trace,
    compare_critical_paths,
)


def span(
    trace_id,
    span_id,
    parent_id,
    name,
    service,
    start_ms,
    end_ms,
):
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_id,
        "name": name,
        "start_time_unix_nano": int(start_ms * 1_000_000),
        "end_time_unix_nano": int(end_ms * 1_000_000),
        "duration_ms": end_ms - start_ms,
        "status": "OK",
        "attributes": {
            "service.name": service,
        },
        "resource": {},
    }


def test_sequential_children_cover_root_duration():
    trace = [
        span(
            "t1",
            "root",
            None,
            "checkout.request",
            "checkout",
            0,
            100,
        ),
        span(
            "t1",
            "auth",
            "root",
            "auth.validate",
            "auth",
            10,
            40,
        ),
        span(
            "t1",
            "inventory",
            "root",
            "inventory.reserve",
            "inventory",
            50,
            90,
        ),
    ]

    result = analyze_trace(trace)

    assert result[
        "critical_path_duration_ms"
    ] == pytest.approx(100.0)

    contributions = result["contributions"]

    assert contributions[
        (
            "auth",
            "auth.validate",
            "checkout.request",
        )
    ] == pytest.approx(30.0)

    assert contributions[
        (
            "inventory",
            "inventory.reserve",
            "checkout.request",
        )
    ] == pytest.approx(40.0)


def test_overlapping_sibling_is_not_double_counted():
    trace = [
        span(
            "t1",
            "root",
            None,
            "request",
            "api",
            0,
            100,
        ),
        span(
            "t1",
            "slow",
            "root",
            "slow.branch",
            "slow-service",
            10,
            90,
        ),
        span(
            "t1",
            "parallel",
            "root",
            "parallel.branch",
            "parallel-service",
            20,
            60,
        ),
    ]

    result = analyze_trace(trace)

    assert result[
        "critical_path_duration_ms"
    ] == pytest.approx(100.0)

    keys = set(result["contributions"])

    assert (
        "slow-service",
        "slow.branch",
        "request",
    ) in keys

    assert (
        "parallel-service",
        "parallel.branch",
        "request",
    ) not in keys


def test_detects_new_critical_path_contributor():
    baseline = [[
        span(
            "b1",
            "root",
            None,
            "checkout.request",
            "checkout",
            0,
            100,
        ),
        span(
            "b1",
            "inventory",
            "root",
            "inventory.reserve",
            "inventory",
            10,
            80,
        ),
        span(
            "b1",
            "db",
            "inventory",
            "inventory.database",
            "inventory-db",
            20,
            40,
        ),
    ]]

    candidate = [[
        span(
            "c1",
            "root",
            None,
            "checkout.request",
            "checkout",
            0,
            200,
        ),
        span(
            "c1",
            "inventory",
            "root",
            "inventory.reserve",
            "inventory",
            10,
            180,
        ),
        span(
            "c1",
            "db",
            "inventory",
            "inventory.database",
            "inventory-db",
            20,
            40,
        ),
        span(
            "c1",
            "redis",
            "inventory",
            "redis.lookup",
            "redis",
            50,
            100,
        ),
    ]]

    result = compare_critical_paths(
        baseline,
        candidate,
    )

    redis = [
        item
        for item in result["contributors"]
        if (
            item["service"] == "redis"
            and item["span"] == "redis.lookup"
        )
    ]

    assert len(redis) == 1
    assert redis[0]["is_new_on_path"] is True
    assert redis[0]["delta_ms"] == pytest.approx(50.0)


def test_per_trace_segments_form_exact_root_duration():
    trace = [
        span(
            "t1",
            "root",
            None,
            "request",
            "checkout",
            0,
            200,
        ),
        span(
            "t1",
            "a",
            "root",
            "service.a",
            "a",
            10,
            80,
        ),
        span(
            "t1",
            "b",
            "root",
            "service.b",
            "b",
            90,
            170,
        ),
        span(
            "t1",
            "nested",
            "b",
            "db.query",
            "db",
            110,
            150,
        ),
    ]

    result = analyze_trace(trace)

    segment_sum = sum(
        segment["duration_ms"]
        for segment in result["segments"]
    )

    assert segment_sum == pytest.approx(
        result["root_duration_ms"]
    )

    assert result[
        "critical_path_duration_ms"
    ] == pytest.approx(
        result["root_duration_ms"]
    )
