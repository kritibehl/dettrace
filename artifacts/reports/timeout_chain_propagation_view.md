# Propagation View

```text
healthy path
  edge -> ... -> api

degraded path
  divergence@4 -> timeout_chain -> gateway timeout visible to operator

step-by-step propagation
  profile:timeout -> db_wait_exceeded
  user:timeout -> downstream_timeout
  api:cancel -> propagate_cancel
  edge:reply -> 504_gateway_timeout
```
