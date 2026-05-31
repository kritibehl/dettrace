# Failure Knowledge Base Report

## Safe claim

heuristic diagnostics knowledge base for replay review; not AI, not production incident automation

## Lookup result

- failure family: `calibration_drift`
- found: `True`

## Similar failures

- `bringup_clock_enable_timeout`
- `calibration_drift_warning`
- `ready_blocked`

## Likely root causes

- `calibration_drift_warning`
- `blocked_ready_state`
- `clock_enable_timeout`

## Recommended actions

- inspect calibration status transition
- compare pre/post bring-up trace
- check clock-enable timeout before calibration
- verify ready state was blocked intentionally
