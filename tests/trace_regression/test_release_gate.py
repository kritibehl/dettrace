from trace_regression.canonical_compare import (
    compare_canonical_multiplicity,
)
from trace_regression.quality import (
    assess_comparison_quality,
)


def make_trace(
    trace_id,
    copies,
):
    spans = [
        {
            "trace_id": trace_id,
            "span_id": "root",
            "parent_span_id": "",
            "service_name": "checkout",
            "name": "POST /checkout",
            "kind": "SERVER",
            "duration_ms": 10,
        }
    ]

    for index in range(copies):
        spans.append(
            {
                "trace_id":
                    trace_id,
                "span_id":
                    f"cart-{index}",
                "parent_span_id":
                    "root",
                "service_name":
                    "checkout",
                "name":
                    "oteldemo.CartService/GetCart",
                "kind":
                    "CLIENT",
                "duration_ms":
                    1,
            }
        )

    return spans


def test_quality_rejects_tiny_cohort():
    quality = assess_comparison_quality(
        3,
        2,
    )

    assert (
        quality.decision
        == "INCONCLUSIVE"
    )


def test_quality_accepts_balanced_cohort():
    quality = assess_comparison_quality(
        40,
        40,
    )

    assert (
        quality.decision
        == "READY"
    )


def test_canonical_edge_multiplicity_regression():
    baseline = []
    candidate = []

    for index in range(40):
        baseline.extend(
            make_trace(
                f"b-{index}",
                1,
            )
        )

        candidate.extend(
            make_trace(
                f"c-{index}",
                2,
            )
        )

    result = (
        compare_canonical_multiplicity(
            baseline,
            candidate,
        )
    )

    assert result[
        "multiplicity_regressions"
    ]

    item = result[
        "multiplicity_regressions"
    ][0]

    assert (
        item[
            "baseline_p95_count"
        ]
        == 1
    )

    assert (
        item[
            "candidate_p95_count"
        ]
        == 2
    )
