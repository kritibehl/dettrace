# Propagation View

```text
healthy path
  edge -> ... -> gateway

degraded path
  divergence@2 -> retry_amplification -> burst of auth failures and elevated latency

step-by-step propagation
  auth:token_db_lookup -> dns_failure
  gateway:retry -> attempt=1
  auth:token_db_lookup -> transport_reset
  gateway:retry -> attempt=2
  auth:token_db_lookup -> timeout_chain
  gateway:reply -> 503_auth_unavailable
```
