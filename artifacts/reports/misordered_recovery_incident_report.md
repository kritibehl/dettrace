# Incident Report

- **Scenario:** misordered_recovery
- **Suspected cause:** recovery misordering
- **Confidence:** 0.9
- **First divergence event:** 1
- **Affected components:** checkout-a, lb, payment
- **Likely user symptom:** recovery appears healthy before correctness is restored
- **Alternative hypotheses:** masked failover; premature health signal

## Key Evidence
- {seq=1, component=checkout-a, action=healthy, state=degraded, detail=marked_healthy_early, ts_ms=12}
- {seq=1, component=checkout-a, action=healthy, state=degraded, detail=marked_healthy_early, ts_ms=12}

## Invariant Breaks
- recovery must follow failure within N steps at event 1 (confidence=0.89): {seq=1, component=checkout-a, action=healthy, state=degraded, detail=marked_healthy_early, ts_ms=12}
