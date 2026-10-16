"""Opt-in conservative bootstrap evidence for p95 latency threshold crossings.

Unit of resampling is a *trace* (not an individual span). This respects
within-trace duplicate spans and avoids weighting repeated span calls as
independent observations. Baseline and candidate samples are independent.

This is an exploratory percentile-bootstrap evidence gate, NOT a claim of
formal statistical power under nonstationarity or sampling bias.
"""

from __future__ import annotations

import hashlib
import math
import random

from trace_regression.statistics import percentile


def validate_options(iterations: int, confidence: float, minimum_traces: int) -> None:
    if not 200 <= iterations <= 5000:
        raise ValueError("bootstrap iterations must be between 200 and 5000")
    if not math.isfinite(confidence) or not 0.80 <= confidence <= 0.99:
        raise ValueError("bootstrap confidence must be in [0.80, 0.99]")
    if not 2 <= minimum_traces <= 100000:
        raise ValueError("minimum span traces must be between 2 and 100000")


def _durations_per_trace(traces: list[list[dict]], key: tuple) -> list[list[float]]:
    return [
        [float(span["duration_ms"]) for span in trace if tuple(span["semantic_key"]) == key]
        for trace in traces
    ]


def _sample_p95(samples: list[list[float]], rng: random.Random) -> float | None:
    durations: list[float] = []
    for _ in range(len(samples)):
        durations.extend(samples[rng.randrange(len(samples))])
    if not durations:
        return None
    return percentile(durations, 0.95)


def assess_latency_thresholds(
    baseline_traces: list[list[dict]],
    candidate_traces: list[list[dict]],
    regressions: list[dict],
    *,
    threshold_pct: float,
    iterations: int = 1000,
    confidence: float = 0.95,
    seed: int = 0,
    minimum_traces: int = 30,
) -> dict:
    """Use multiplicity-adjusted, one-sided percentile bootstrap lower bounds.

    Only regressions identified by the existing point-estimate comparator are
    reassessed. Absence of a crossing is NOT evidence that performance is equal.
    """
    validate_options(iterations, confidence, minimum_traces)
    if not math.isfinite(threshold_pct) or threshold_pct < 0:
        raise ValueError("latency threshold must be finite and nonnegative")

    base_keys = {tuple(s["semantic_key"]) for t in baseline_traces for s in t}
    cand_keys = {tuple(s["semantic_key"]) for t in candidate_traces for s in t}
    comparisons = len(base_keys & cand_keys)
    # Bonferroni: account for the entire family of comparable keys in a cohort,
    # not just keys that happened to cross the threshold in observed data.
    alpha = (1.0 - confidence) / max(1, comparisons)
    assessments: list[dict] = []

    for regression in regressions:
        key = tuple(regression["semantic_key"])
        base = _durations_per_trace(baseline_traces, key)
        cand = _durations_per_trace(candidate_traces, key)
        b_count = sum(bool(t) for t in base)
        c_count = sum(bool(t) for t in cand)

        item = {
            "semantic_key": list(key),
            "baseline_span_traces": b_count,
            "candidate_span_traces": c_count,
            "baseline_p95_ms": regression["baseline_p95_ms"],
            "candidate_p95_ms": regression["candidate_p95_ms"],
            "observed_delta_pct": regression["delta_pct"],
            "threshold_pct": threshold_pct,
            "adjusted_one_sided_alpha": alpha,
            "lower_bound_delta_pct": None,
            "status": "INCONCLUSIVE",
            "reason": "",
        }
        if b_count < minimum_traces or c_count < minimum_traces:
            item["reason"] = "insufficient_span_trace_coverage"
        elif regression["baseline_p95_ms"] <= 0:
            item["reason"] = "nonpositive_baseline_p95"
        elif not all(math.isfinite(v) and v >= 0 for t in base + cand for v in t):
            item["reason"] = "invalid_span_duration"
        else:
            digest = hashlib.sha256(repr(key).encode("utf-8")).digest()
            rng = random.Random(seed ^ int.from_bytes(digest[:8], "big"))
            deltas = []
            for _ in range(iterations):
                before = _sample_p95(base, rng)
                after = _sample_p95(cand, rng)
                if before is None or after is None or before <= 0:
                    break
                deltas.append((after / before - 1) * 100)
            if len(deltas) != iterations:
                item["reason"] = "unusable_bootstrap_draw"
            else:
                lower = percentile(deltas, alpha)
                item["lower_bound_delta_pct"] = round(lower, 6)
                if lower > threshold_pct:
                    item["status"] = "CONFIRMED"
                    item["reason"] = "bootstrap_lower_bound_exceeds_threshold"
                else:
                    item["reason"] = "threshold_crossing_not_statistically_resolved"
        assessments.append(item)

    return {
        "mode": "bootstrap",
        "method": "independent_trace_resampling_percentile_bootstrap",
        "correction": "bonferroni_per_cohort_comparable_semantic_keys",
        "comparable_semantic_keys": comparisons,
        "iterations": iterations,
        "confidence_level": confidence,
        "seed": seed,
        "minimum_span_traces": minimum_traces,
        "point_estimate_regressions": len(regressions),
        "confirmed_regressions": sum(x["status"] == "CONFIRMED" for x in assessments),
        "inconclusive_regressions": sum(x["status"] == "INCONCLUSIVE" for x in assessments),
        "assessments": assessments,
    }
