# Bug Triage Report

## Title

Missing interrupt clear causes device replay divergence before network packet handling.

## Component

DetTrace++ / device replay / interrupt-state transition path

## Severity

Medium

## Reproducibility

Always reproducible with `device_replay/sample_device_trace.json`

## Regression

Yes — failing-to-passing replay example isolates a regression at divergence index 4.

## Steps to reproduce

1. Run `make -C device_replay run`
2. Run `python3 device_replay/run_replay_suite.py`
3. Inspect `device_replay/reports/device_replay_summary.md`

## Expected result

```text
interrupt_cleared -> READY
Actual result
sensor_read -> WAITING
First divergence
index: 4
expected_event: interrupt_cleared
actual_event: sensor_read
expected_state: READY
actual_state: WAITING
probable_defect_type: missing_interrupt_clear
Root-cause hypothesis

The device interrupt path does not clear DEVICE_IRQ before another sensor read or network packet handling path continues.

Suggested fix

Enforce:

interrupt_asserted -> interrupt_cleared -> device_state_change(READY)

before allowing downstream packet processing.
