# Bring-Up Comparison Report

## Safe claim

firmware-style trace validation; not silicon ownership or hardware lab bring-up

## Summary

- diagnostic status: `FAIL`
- expected event count: `7`
- observed event count: `8`
- first divergence index: `3`
- timeout events: `1`
- retry events: `1`
- calibration issues: `2`
- blocked/degraded events: `2`

## First divergence

- expected: `{'phase': 'register_init', 'event': 'clock_enable', 'register': 'CLK_CTRL', 'value': '0x1', 'calibration_status': 'not_started', 'status': 'ok'}`
- observed: `{'phase': 'register_init', 'event': 'clock_enable_timeout', 'register': 'CLK_CTRL', 'value': '0x0', 'calibration_status': 'not_started', 'status': 'timeout'}`

## Root-cause summary

Observed boot trace diverged during register initialization: expected clock_enable but observed clock_enable_timeout, followed by retry behavior, calibration drift warning, and blocked ready state.
