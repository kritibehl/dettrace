# Device Event Replay Schema

This pack models trace-driven device-level events for deterministic replay and defect reproduction.

It is not hardware emulation. It is expected-vs-actual replay of device-facing event sequences.

## Event types

- button_press
- sensor_read
- network_packet_received
- device_state_change
- firmware_timer_tick
- interrupt_asserted
- interrupt_cleared

## Required fields

```json
{
  "index": 0,
  "event_type": "sensor_read",
  "expected_state": "IDLE",
  "actual_state": "IDLE",
  "value": "temperature=42",
  "notes": "nominal sensor poll"
}
Replay output

The replay tool reports:

first divergence index
expected state
actual state
probable defect type
reproduction steps
