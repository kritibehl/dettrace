# DetTrace++ Defect Reproduction Guide

This guide documents how DetTrace++ reproduces and explains device-level replay defects using expected-vs-actual event traces.

## Defect type

`missing_interrupt_clear`

## Input trace

`device_replay/sample_device_trace.json`

## Expected behavior

```text
button_press -> sensor_read -> firmware_timer_tick -> interrupt_asserted -> interrupt_cleared -> network_packet_received
Expected state at divergence:

READY
Actual behavior
button_press -> sensor_read -> firmware_timer_tick -> interrupt_asserted -> sensor_read -> network_packet_received

Actual state at divergence:

WAITING
First divergence
index: 4
expected_event: interrupt_cleared
actual_event: sensor_read
expected_state: READY
actual_state: WAITING
probable_defect_type: missing_interrupt_clear
Reproduction command

Compile and run the C++17 replay tool:

c++ -std=c++17 device_replay/replay_device_trace.cpp -o device_replay/replay_device_trace
./device_replay/replay_device_trace

Compile and run the C-compatible interface demo:

cc -std=c11 device_replay/replay_result.c device_replay/replay_c_api_demo.c -o device_replay/replay_c_api_demo
./device_replay/replay_c_api_demo
Fix hypothesis

The device interrupt path likely needs to clear DEVICE_IRQ before the firmware performs another sensor read or processes network input.

A plausible fix would enforce:

interrupt_asserted -> interrupt_cleared -> device_state_change(READY)

before allowing downstream packet handling.
