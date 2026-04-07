# Incident Report

- **Scenario:** retry_storm
- **Suspected cause:** retry_amplification
- **Confidence:** 0.82
- **First divergence event:** 2
- **Affected components:** auth, gateway
- **Likely user symptom:** burst of auth failures and elevated latency
- **Alternative hypotheses:** dependency DNS flap; transport reset before timeout

## Key Evidence
- {seq=2, component=auth, action=token_db_lookup, state=degraded, detail=dns_failure, ts_ms=18}
