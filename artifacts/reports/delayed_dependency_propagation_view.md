# Propagation View

```text
healthy path
  orchestrator -> ... -> worker

degraded path
  divergence@1 -> timing divergence -> deadline miss after dependency delay

step-by-step propagation
  orchestrator:dispatch -> action_before_ready
  cache:ready -> cache_ready_late
  worker:complete -> deadline_miss
```
