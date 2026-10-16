from trace_regression.github_summary import render_summary


def test_summary_explains_inconclusive_bootstrap_crossing():
    report = {
        "decision": "INCONCLUSIVE", "latency_evidence_mode": "bootstrap",
        "baseline_trace_count": 40, "candidate_trace_count": 40,
        "matched_shape_count": 1,
        "cohorts": [{
            "shape": {"method": "POST", "route": "/checkout"},
            "baseline_trace_count": 40, "candidate_trace_count": 40,
            "decision": "INCONCLUSIVE", "latency_evidence": {
                "confirmed_regressions": 0, "inconclusive_regressions": 1,
                "assessments": [{"semantic_key": ["checkout", "checkout.request", "ROOT"],
                                 "status": "INCONCLUSIVE", "lower_bound_delta_pct": 0.0,
                                 "reason": "threshold_crossing_not_statistically_resolved"}],
            },
        }],
    }
    summary = render_summary(report)
    assert "Opt-in bootstrap latency evidence" in summary
    assert "checkout.request" in summary
    assert "not PASS" in summary
    assert "threshold_crossing_not_statistically_resolved" in summary


def test_non_bootstrap_summary_unchanged():
    assert "Opt-in bootstrap" not in render_summary({"decision": "PASS", "cohorts": []})
