# Incident Report

- **Scenario:** delayed_dependency
- **Suspected cause:** timing divergence
- **Confidence:** 0.84
- **First divergence event:** 1
- **Affected components:** cache, orchestrator
- **Likely user symptom:** deadline miss after dependency delay
- **Alternative hypotheses:** readiness gate bug; dependency probe lag

## Key Evidence
- {seq=1, component=orchestrator, action=dispatch, state=degraded, detail=action_before_ready, ts_ms=8}
- {seq=1, component=orchestrator, action=dispatch, state=degraded, detail=action_before_ready, ts_ms=8}

## Invariant Breaks
- no action before dependency-ready at event 1 (confidence=0.93): {seq=1, component=orchestrator, action=dispatch, state=degraded, detail=action_before_ready, ts_ms=8}
