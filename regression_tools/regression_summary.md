# Regression Isolation Summary

## Status

REGRESSION_ISOLATED

## First failing commit

`c3d4e5f` — refactor interrupt state machine

## Previous passing commit

`b2c3d4e`

## Replay diff

- expected: `interrupt_cleared -> READY`
- actual: `sensor_read -> WAITING`
- first divergence index: `4`
- probable defect type: `missing_interrupt_clear`

## Root-cause summary

Regression introduced by interrupt state-machine refactor: actual replay reads sensor data before clearing the device interrupt.

## Bisect probes

- index 2: `c3d4e5f` -> FAIL (sensor_read occurs before interrupt_cleared)
- index 0: `a1b2c3d` -> PASS (expected interrupt clear sequence preserved)
- index 1: `b2c3d4e` -> PASS (sensor read path still follows interrupt clear)
