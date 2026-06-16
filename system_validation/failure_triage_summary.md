# Failure Triage Summary

## Triage flow

1. Load replay trace.
2. Compare expected vs observed event sequence.
3. Identify first divergence.
4. Classify failure family.
5. Search similar historical failures.
6. Run build regression radar.
7. Generate reviewer-readable report.

## Example

- family: `timeout`
- first divergence: `ack_received` vs `timeout`
- likely root cause: `timeout_chain`
- recommended action: inspect retry backoff, ACK ordering, and timeout thresholds.
