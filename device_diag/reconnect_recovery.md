# Reconnect Recovery Workflow

## Failure path

    sensor_read_timeout -> device_reconnect -> stale_device_state

## Recovery path

    device_reconnect -> state_refresh -> health_check_pass

## Validation goal

Confirm that reconnect clears stale state before the device is marked ready.

## Why this matters

Diagnostic workflows need to distinguish between a recovered device and a device that merely reconnected while retaining stale state.
