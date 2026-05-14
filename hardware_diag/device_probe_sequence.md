# Device Probe Sequence Diagnostic Simulation

## Goal

Show expected-vs-actual device probe behavior for diagnostics and validation tooling.

## Expected

    probe_start -> identify_device -> read_capabilities -> health_check_pass -> device_ready

## Actual

    probe_start -> identify_device -> read_capabilities_timeout -> retry_probe -> degraded_state

## First divergence

    expected_event: health_check_pass
    actual_event: read_capabilities_timeout

## Debugging value

This models how a diagnostic tool can identify the earliest point where a device lifecycle path diverges from expected probe behavior.
