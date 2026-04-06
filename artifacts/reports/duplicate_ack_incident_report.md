# Incident Report

- **Scenario:** duplicate_ack
- **Suspected cause:** duplicate event
- **Confidence:** 0.9
- **First divergence event:** 3
- **Affected components:** coordinator
- **Likely user symptom:** duplicate completion or user-visible duplicate side effect
- **Alternative hypotheses:** retry bookkeeping bug; idempotency guard missing

## Key Evidence
- {seq=3, component=coordinator, action=ack, state=degraded, detail=job-1_duplicate_ack}
- {seq=3, component=coordinator, action=ack, state=degraded, detail=job-1_duplicate_ack}

## Invariant Breaks
- no duplicate completion without retry at event 3 (confidence=0.96): {seq=3, component=coordinator, action=ack, state=degraded, detail=job-1_duplicate_ack}
