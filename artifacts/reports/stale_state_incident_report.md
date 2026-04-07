# Incident Report

- **Scenario:** stale_state
- **Suspected cause:** stale-state transition
- **Confidence:** 0.9
- **First divergence event:** 1
- **Affected components:** controller, planner
- **Likely user symptom:** control drift or stale state actuation
- **Alternative hypotheses:** delayed sensor update; state ordering instability

## Key Evidence
- {seq=1, component=controller, action=consume_state, state=degraded, detail=est=v1_stale, ts_ms=10}
- {seq=2, component=controller, action=actuate, state=degraded, detail=cmd_from_stale_state, ts_ms=20}

## Invariant Breaks
- no stale-state actuation after fresher estimate exists at event 2 (confidence=0.79): {seq=2, component=controller, action=actuate, state=degraded, detail=cmd_from_stale_state, ts_ms=20}
