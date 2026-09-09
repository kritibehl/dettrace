from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass


@dataclass(frozen=True)
class ComparisonQuality:
    decision: str
    reason: str
    baseline_samples: int
    candidate_samples: int
    required_samples: int
    sample_ratio: float
    baseline_invalid_fraction: float
    candidate_invalid_fraction: float

    def to_dict(self):
        return asdict(self)


def assess_comparison_quality(
    baseline_samples: int,
    candidate_samples: int,
    *,
    minimum_samples: int = 30,
    minimum_sample_ratio: float = 0.25,
    baseline_invalid_fraction: float = 0.0,
    candidate_invalid_fraction: float = 0.0,
    maximum_invalid_fraction: float = 0.10,
) -> ComparisonQuality:
    largest = max(
        baseline_samples,
        candidate_samples,
    )

    smallest = min(
        baseline_samples,
        candidate_samples,
    )

    ratio = (
        smallest / largest
        if largest
        else 0.0
    )

    decision = "READY"
    reason = "sufficient_samples"

    if baseline_samples < minimum_samples:
        decision = "INCONCLUSIVE"
        reason = "insufficient_baseline_samples"

    elif candidate_samples < minimum_samples:
        decision = "INCONCLUSIVE"
        reason = "insufficient_candidate_samples"

    elif ratio < minimum_sample_ratio:
        decision = "INCONCLUSIVE"
        reason = "severe_sample_imbalance"

    elif baseline_invalid_fraction > maximum_invalid_fraction:
        decision = "INCONCLUSIVE"
        reason = "excessive_baseline_invalid_traces"

    elif candidate_invalid_fraction > maximum_invalid_fraction:
        decision = "INCONCLUSIVE"
        reason = "excessive_candidate_invalid_traces"

    return ComparisonQuality(
        decision=decision,
        reason=reason,
        baseline_samples=baseline_samples,
        candidate_samples=candidate_samples,
        required_samples=minimum_samples,
        sample_ratio=ratio,
        baseline_invalid_fraction=baseline_invalid_fraction,
        candidate_invalid_fraction=candidate_invalid_fraction,
    )
