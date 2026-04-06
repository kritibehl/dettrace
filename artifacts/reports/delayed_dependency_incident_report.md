# Incident Report

- **Scenario:** delayed_dependency
- **Suspected cause:** timing divergence
- **Confidence:** 0.84
- **First divergence event:** 1
- **Affected components:** orchestrator
- **Likely user symptom:** deadline miss after dependency delay
- **Alternative hypotheses:** incorrect readiness gating; dependency probe lag

## Key Evidence
- {seq=1, component=orchestrator, action=dispatch, state=degraded, detail=action_before_ready}
- {seq=1, component=orchestrator, action=dispatch, state=degraded, detail=action_before_ready}

## Invariant Breaks
- no action before dependency-ready at event 1 (confidence=0.91): {seq=1, component=orchestrator, action=dispatch, state=degraded, detail=action_before_ready}
