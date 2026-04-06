# Retry Storm Case Study

This case study compares healthy vs degraded auth lookup behavior and shows how retry amplification becomes operator-visible failure.

## Healthy Trace Excerpt
- {seq=0, component=edge, action=request_start, state=ok, detail=trace-200}
- {seq=1, component=gateway, action=auth_lookup, state=ok, detail=attempt=0}
- {seq=2, component=auth, action=token_db_lookup, state=ok, detail=attempt=0}
- {seq=3, component=token-db, action=reply, state=ok, detail=token_ok}

## Degraded Trace Excerpt
- {seq=0, component=edge, action=request_start, state=ok, detail=trace-200}
- {seq=1, component=gateway, action=auth_lookup, state=ok, detail=attempt=0}
- {seq=2, component=auth, action=token_db_lookup, state=degraded, detail=dns_failure}
- {seq=3, component=gateway, action=retry, state=degraded, detail=attempt=1}
- {seq=4, component=auth, action=token_db_lookup, state=degraded, detail=transport_reset}
- {seq=5, component=gateway, action=retry, state=degraded, detail=attempt=2}

## Why replay matters
- logs often show aftermath
- replay reveals drift onset
- first divergence is more actionable than terminal symptom
- causal reconstruction beats symptom-only debugging
