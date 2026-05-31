# Failure Knowledge Base Recommended Actions

## Safe scope

This is a heuristic diagnostics knowledge base for replay review.

It is not AI, not an expert system, not production incident automation, and not hardware-lab ownership.

## Families

### retry_storm

Recommended investigation:

- inspect retry backoff and retry limits
- validate ACK ordering before retry
- check timeout thresholds
- compare retry window against known-good replay

### timeout

Recommended investigation:

- inspect first timeout event
- compare expected vs observed deadline
- check downstream recovery path
- verify whether retry reached a stable final state

### disconnect

Recommended investigation:

- verify reconnect sequence
- check stale state cleanup
- compare capability re-read behavior
- confirm final ready/session state

### enumeration_failure

Recommended investigation:

- inspect config-read step
- verify BAR assignment sequence
- compare interrupt routing against expected replay
- confirm device_ready was not falsely reported

### state_corruption

Recommended investigation:

- inspect state transition ordering
- compare expected vs observed lifecycle state
- verify stale state cleanup
- check for duplicate attach or stale session reuse

### calibration_drift

Recommended investigation:

- inspect calibration status transition
- compare pre/post bring-up trace
- check clock-enable timeout before calibration
- verify ready state was blocked intentionally
