# Propagation View

```text
healthy path
  worker -> ... -> coordinator

degraded path
  divergence@3 -> duplicate event -> duplicate completion or user-visible duplicate side effect

step-by-step propagation
  coordinator:ack -> job-1_duplicate_ack
```
