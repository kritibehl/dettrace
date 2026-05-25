# C++ Testing and Replay Validation

DetTrace includes C++17 replay-oriented validation artifacts for device-event debugging.

## Build device replay

    make -C device_replay run

## What it validates

- expected vs actual device-event replay
- first-divergence detection
- interrupt-clear ordering
- missing interrupt-clear defect reproduction
- failing-to-passing replay behavior
- C-compatible replay-result interface

## Example output

    first_divergence_index: 4
    expected_event: interrupt_cleared
    actual_event: sensor_read
    expected_state: READY
    actual_state: WAITING
    probable_defect_type: missing_interrupt_clear

## Safe claim

This demonstrates C/C++ replay validation and debugging workflows. It does not claim production firmware, driver, or kernel development.
