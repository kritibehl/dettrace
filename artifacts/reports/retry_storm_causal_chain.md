# Causal Chain

- **Scenario:** retry_storm
- **What changed first:** event 2 -> {seq=2, component=auth, action=token_db_lookup, state=degraded, detail=dns_failure, ts_ms=18}
- **What downstream behaviors changed:** operator-visible symptom became `burst of auth failures and elevated latency`
- **Which subsystem was affected first:** auth
- **Did recovery restore correctness or mask behavior:** recovery did not occur before symptom exposure
