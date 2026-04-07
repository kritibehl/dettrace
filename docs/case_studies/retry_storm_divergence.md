# Retry Storm Case Study

This case study compares healthy vs degraded auth lookup behavior and shows how retry amplification becomes an operator-visible failure.

## Healthy Trace Excerpt
- {seq=0, component=edge, action=request_start, state=ok, detail=trace-200, ts_ms=0}
- {seq=1, component=gateway, action=auth_lookup, state=ok, detail=attempt=0, ts_ms=8}
- {seq=2, component=auth, action=token_db_lookup, state=ok, detail=attempt=0, ts_ms=18}
- {seq=3, component=token-db, action=reply, state=ok, detail=token_ok, ts_ms=35}

## Degraded Trace Excerpt
- {seq=0, component=edge, action=request_start, state=ok, detail=trace-200, ts_ms=0}
- {seq=1, component=gateway, action=auth_lookup, state=ok, detail=attempt=0, ts_ms=8}
- {seq=2, component=auth, action=token_db_lookup, state=degraded, detail=dns_failure, ts_ms=18}
- {seq=3, component=gateway, action=retry, state=degraded, detail=attempt=1, ts_ms=32}
- {seq=4, component=auth, action=token_db_lookup, state=degraded, detail=transport_reset, ts_ms=55}
- {seq=5, component=gateway, action=retry, state=degraded, detail=attempt=2, ts_ms=70}

## Why replay matters
- logs often show aftermath
- replay reveals drift onset
- first divergence is more actionable than terminal symptom
- causal reconstruction beats symptom-only debugging
