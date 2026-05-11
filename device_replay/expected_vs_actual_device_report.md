# Expected vs Actual Device Replay Report

## Scenario

`device-interrupt-state-divergence`

## Expected sequence

```text
button_press -> sensor_read -> firmware_timer_tick -> interrupt_asserted -> interrupt_cleared -> network_packet_received
Actual sequence
button_press -> sensor_read -> firmware_timer_tick -> interrupt_asserted -> sensor_read -> network_packet_received
First divergence

Index: 4

Expected state

READY

Actual state

WAITING

Probable defect type

missing_interrupt_clear

Interpretation

The device should clear the interrupt after interrupt_asserted, then enter READY.

Instead, the actual trace performs another sensor_read and remains in WAITING, causing the later network packet to arrive while the device is still degraded.
