from trace_regression.github_summary import (
    render_summary,
)


def test_summary_renders_cohort_decisions():
    report = {
        "decision": "FAIL",
        "baseline_trace_count": 40,
        "candidate_trace_count": 40,
        "matched_shape_count": 2,
        "cohorts": [
            {
                "shape": {
                    "method": "POST",
                    "route": "/checkout",
                    "root": "checkout.request",
                },
                "baseline_trace_count": 30,
                "candidate_trace_count": 30,
                "decision": "FAIL",
                "regressions": [{}],
                "error_regressions": [],
                "added_spans": [],
            },
            {
                "shape": {
                    "method": "GET",
                    "route": "/health",
                    "root": "health.request",
                },
                "baseline_trace_count": 10,
                "candidate_trace_count": 10,
                "decision": "PASS",
                "regressions": [],
                "error_regressions": [],
                "added_spans": [],
            },
        ],
    }

    summary = render_summary(
        report
    )

    assert (
        "**Decision:** `FAIL`"
        in summary
    )

    assert (
        "POST /checkout"
        in summary
    )

    assert (
        "GET /health"
        in summary
    )

    assert (
        "Failed request shapes"
        in summary
    )


def test_summary_renders_errors_and_new_spans():
    report = {
        "decision": "FAIL",
        "baseline_trace_count": 30,
        "candidate_trace_count": 30,
        "matched_shape_count": 1,
        "cohorts": [
            {
                "shape": {
                    "method": "POST",
                    "route": "/checkout",
                },
                "baseline_trace_count": 30,
                "candidate_trace_count": 30,
                "decision": "FAIL",
                "regressions": [],
                "error_regressions": [
                    {
                        "service": "inventory",
                        "span": "inventory.reserve",
                        "baseline_error_rate": 0.0,
                        "candidate_error_rate": 0.2,
                    }
                ],
                "added_spans": [
                    {
                        "service": "redis",
                        "span": "redis.lookup",
                        "parent": "inventory.reserve",
                    }
                ],
            }
        ],
    }

    summary = render_summary(
        report
    )

    assert (
        "0.0% -> 20.0%"
        in summary
    )

    assert (
        "inventory.reserve -> redis.lookup"
        in summary
    )

    assert (
        "service=redis"
        in summary
    )
