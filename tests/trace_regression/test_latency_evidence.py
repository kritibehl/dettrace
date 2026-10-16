import copy

import pytest

from trace_regression.analyzer import analyze_cohort
from trace_regression.cli import analyze_shapes
from trace_regression.latency_evidence import (
    assess_latency_thresholds,
    validate_options,
)
from trace_regression.normalize import normalize_trace


def _trace(i, duration, route="/checkout", add_child=False):
    root = {
        "trace_id": f"trace-{i}", "span_id": f"span-{i}",
        "parent_span_id": None, "name": "checkout.request", "duration_ms": duration,
        "start_time_unix_nano": 0, "end_time_unix_nano": int(duration * 1_000_000),
        "status": "OK", "attributes": {"service.name": "checkout", "http.request.method": "POST", "http.route": route},
        "resource": {},
    }
    result = [root]
    if add_child:
        child = copy.deepcopy(root)
        child.update(span_id=f"child-{i}", parent_span_id=root["span_id"], name="redis.lookup", duration_ms=20)
        result.append(child)
    return result


def _shapes(baseline, candidate, **kwargs):
    return analyze_shapes(baseline, candidate, 50, 5, latency_evidence="bootstrap", bootstrap_iterations=400, **kwargs)


def test_strong_separation_is_confirmed():
    base = [_trace(i, 100) for i in range(40)]
    cand = [_trace(i + 100, 200) for i in range(40)]
    report = _shapes(base, cand)
    cohort = report["cohorts"][0]
    assert cohort["decision"] == "FAIL"
    evidence = cohort["latency_evidence"]
    assert evidence["confirmed_regressions"] == 1
    assert evidence["assessments"][0]["lower_bound_delta_pct"] == pytest.approx(100)


def test_sparse_tail_causes_inconclusive_not_false_positive():
    base = [_trace(i, 100) for i in range(50)]
    cand = [_trace(i + 100, 400 if i >= 46 else 100) for i in range(50)]
    report = _shapes(base, cand)
    cohort = report["cohorts"][0]
    assert cohort["point_estimate_decision"] == "FAIL"
    assert cohort["decision"] == "INCONCLUSIVE"
    assert cohort["latency_evidence"]["inconclusive_regressions"] == 1
    assert report["decision"] == "INCONCLUSIVE"


def test_identical_samples_pass_statistical_mode():
    base = [_trace(i, 100) for i in range(40)]
    cand = [_trace(i + 100, 100) for i in range(40)]
    report = _shapes(base, cand)
    assert report["decision"] == "PASS"
    assert report["cohorts"][0]["latency_evidence"]["assessments"] == []


def test_reproducibility_fixed_seed():
    base = [_trace(i, 100 + i) for i in range(50)]
    cand = [_trace(i + 100, 140 + i * 2) for i in range(50)]
    first = _shapes(base, cand, bootstrap_seed=911)
    second = _shapes(base, cand, bootstrap_seed=911)
    assert first == second


def test_under_sampled_matched_cohort_is_inconclusive_even_when_no_regression():
    base = [_trace(i, 100) for i in range(10)]
    cand = [_trace(i + 100, 100) for i in range(10)]
    assert _shapes(base, cand)["decision"] == "INCONCLUSIVE"


def test_missing_cohort_is_inconclusive():
    base = [_trace(i, 100) for i in range(40)]
    cand = [_trace(i + 100, 100) for i in range(40)]
    cand.extend(_trace(i + 200, 80, "/new") for i in range(40))
    report = _shapes(base, cand)
    assert report["decision"] == "INCONCLUSIVE"
    assert len(report["candidate_only_shapes"]) == 1


def test_structural_regression_remains_fail_when_latency_uncertain():
    base = [_trace(i, 100) for i in range(40)]
    cand = [_trace(i + 100, 400 if i >= 36 else 100, add_child=True) for i in range(40)]
    report = _shapes(base, cand)
    assert report["cohorts"][0]["decision"] == "FAIL"
    assert report["decision"] == "FAIL"


def test_not_enough_trace_presence_for_span():
    base = [_trace(i, 100, add_child=i < 5) for i in range(40)]
    cand = [_trace(i + 100, 100, add_child=i < 5) for i in range(40)]
    for t in cand[:5]:
        t[1]["duration_ms"] = 100
    report = _shapes(base, cand)
    assessment = next(x for x in report["cohorts"][0]["latency_evidence"]["assessments"] if x["semantic_key"][1] == "redis.lookup")
    assert assessment["reason"] == "insufficient_span_trace_coverage"
    assert report["decision"] == "INCONCLUSIVE"


def test_bonferroni_family_counts_all_comparable_keys():
    baseline = [normalize_trace(_trace(i, 100, add_child=True)) for i in range(40)]
    candidate = [normalize_trace(_trace(i+100, 200, add_child=True)) for i in range(40)]
    # Root crosses threshold, child stays unchanged.
    from trace_regression.compare import compare_traces
    regs = compare_traces(baseline, candidate)["regressions"]
    evidence = assess_latency_thresholds(baseline, candidate, regs, threshold_pct=50, iterations=200, confidence=0.95)
    assert evidence["comparable_semantic_keys"] == 2
    assert evidence["assessments"][0]["adjusted_one_sided_alpha"] == pytest.approx(0.025)


@pytest.mark.parametrize("options", [
    (100, 0.95, 30), (6000, 0.95, 30), (300, 0.1, 30),
    (300, 1.0, 30), (300, float("nan"), 30), (300, 0.95, 1),
])
def test_invalid_bootstrap_settings(options):
    with pytest.raises(ValueError):
        validate_options(*options)


def test_zero_baseline_returns_inconclusive_not_infinity():
    base = [_trace(i, 0) for i in range(40)]
    cand = [_trace(i + 100, 100) for i in range(40)]
    report = _shapes(base, cand)
    assert report["decision"] == "INCONCLUSIVE"
    assert report["cohorts"][0]["latency_evidence"]["assessments"][0]["reason"] == "nonpositive_baseline_p95"


def test_original_point_estimate_behavior_preserved():
    base = [_trace(i, 100) for i in range(50)]
    cand = [_trace(i + 100, 400 if i >= 46 else 100) for i in range(50)]
    report = analyze_shapes(base, cand, 50, 5)
    assert report["decision"] == "FAIL"
    assert "latency_evidence" not in report["cohorts"][0]
