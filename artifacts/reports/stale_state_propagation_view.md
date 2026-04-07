# Propagation View

```text
healthy path
  planner -> ... -> plant

degraded path
  divergence@1 -> stale-state transition -> control drift or stale state actuation

step-by-step propagation
  controller:consume_state -> est=v1_stale
  controller:actuate -> cmd_from_stale_state
  plant:state_commit -> drift_detected
```
