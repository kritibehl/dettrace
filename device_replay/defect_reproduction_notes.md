# Defect Reproduction Notes

## Defect

Missing interrupt clear after device interrupt assertion.

## Reproduction steps

1. Start from `sample_device_trace.json`.
2. Replay expected and actual event sequences.
3. Compare event index 4.
4. Expected event: `interrupt_cleared`.
5. Actual event: `sensor_read`.
6. Confirm actual device state remains `WAITING`.
7. Confirm later packet is received while device is `DEGRADED`.

## Why DetTrace helps

Logs would show a later degraded packet path.

Replay isolates the earlier event-ordering defect: interrupt clear was skipped before the device proceeded.
