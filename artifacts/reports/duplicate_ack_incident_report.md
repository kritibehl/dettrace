# Incident Report

- **Scenario:** duplicate_ack
- **Suspected cause:** duplicate event
- **Confidence:** 0.9
- **First divergence event:** 3
- **Affected components:** coordinator, worker
- **Likely user symptom:** duplicate completion or user-visible duplicate side effect
- **Alternative hypotheses:** retry bookkeeping bug; missing idempotency guard

## Key Evidence
- {seq=3, component=coordinator, action=ack, state=degraded, detail=job-1_duplicate_ack, ts_ms=35}
- {seq=3, component=coordinator, action=ack, state=degraded, detail=job-1_duplicate_ack, ts_ms=35}

## Invariant Breaks
- no duplicate completion without retry at event 3 (confidence=0.97): {seq=3, component=coordinator, action=ack, state=degraded, detail=job-1_duplicate_ack, ts_ms=35}
