# Measurement Validation Report

## Capture

`mock_capture_001` from `mock-position-sensor`

## Safe claim

mock instrument-data parsing and validation; not lab hardware control

## Summary

- diagnostic status: `FAIL`
- sample count: `6` / expected `8`
- missing sample count: `2`
- out-of-range samples: `1`
- calibration issues: `2`
- degraded states: `3`
- retry events: `3`

## Diagnostic interpretation

The capture is marked `FAIL` because it contains an out-of-range measurement, calibration drift warnings, degraded device states, retry events, and incomplete capture windows.

This demonstrates mock instrument-data parsing and validation for hardware-adjacent diagnostics review.
