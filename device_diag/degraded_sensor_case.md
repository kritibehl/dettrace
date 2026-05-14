# Degraded Sensor Diagnostic Case

## Symptom

Sensor read timed out during device probe.

## Unhealthy subsystem

    sensor_probe_path

## Actual sequence

    probe_start -> sensor_read_timeout -> degraded_state

## Diagnostic interpretation

The device should not be marked ready until the sensor probe path either succeeds or recovery validates a refreshed state.

## Safe claim

This is a device-health diagnostic simulation for validation tooling, not embedded firmware.
