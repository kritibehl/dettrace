# Incident Report

- **Scenario:** stale_state
- **Suspected cause:** stale-state transition
- **Confidence:** 0.9
- **First divergence event:** 1
- **Affected components:** controller, planner
- **Likely user symptom:** control drift or stale state actuation
- **Alternative hypotheses:** delayed sensor update; ordering instability in state pipeline

## Key Evidence
- {seq=1, component=planner, action=state_update, state=ok, detail=est=v2}
- {seq=3, component=controller, action=actuate, state=degraded, detail=cmd_from_stale_state}

## Invariant Breaks
- ack ordering must preserve causality at event 3 (confidence=0.73): {seq=3, component=controller, action=actuate, state=degraded, detail=cmd_from_stale_state}
