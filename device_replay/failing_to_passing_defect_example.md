# Failing-to-Passing Device Defect Example

## Bug

Missing interrupt clear after a device interrupt assertion.

## Before: failing trace

Input:

`device_replay/sample_device_trace.json`

At divergence index 4:

```text
expected_event: interrupt_cleared
actual_event: sensor_read
expected_state: READY
actual_state: WAITING
probable_defect_type: missing_interrupt_clear
Fix hypothesis

The firmware/device event flow should clear DEVICE_IRQ before allowing another sensor read or network packet processing path.

Corrected sequence:

interrupt_asserted -> interrupt_cleared -> network_packet_received
After: corrected trace

Input:

device_replay/sample_device_trace_fixed.json

The corrected trace matches the expected path and the replay tool reports:

status: PASS
first_divergence_index: none
Reproduction
make -C device_replay run
python3 device_replay/run_replay_suite.py

