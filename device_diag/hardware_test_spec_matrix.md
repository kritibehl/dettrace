# Hardware Diagnostic Test-Spec Matrix

This matrix maps simulated device-diagnostic scenarios to expected behavior, observable failure signals, replay evidence, validation commands, and pass/fail criteria.

It is intended as a diagnostics review artifact. It does not claim manufacturing systems, embedded firmware ownership, driver development, or hardware lab engineering.

| Diagnostic Case | Expected Behavior | Observable Failure | Replay Signal | Validation Command | Pass / Fail Criteria |
|---|---|---|---|---|---|
| I2C timeout | Device ACK arrives after register read, then device reaches READY | Timeout during register read | `actual_event=timeout`, `probable_defect_type=i2c_ack_timeout` | `python3 tools/replay_inspect_cli.py show-timeouts hardware_diag/i2c_timeout_trace.json` | Pass if timeout is detected and recovery path is documented; fail if timeout is hidden or stale state is not surfaced |
| USB reconnect | Device reconnects, descriptor is re-read, stale state is cleared | Disconnect before configuration | `actual_event=disconnect`, `probable_defect_type=transient_device_reconnect` | `python3 tools/replay_inspect_cli.py show-divergence hardware_diag/usb_device_reconnect.json` | Pass if reconnect sequence validates descriptor re-read and final READY state; fail if stale state persists |
| PCIe-style enumeration | Probe flow reaches config read, BAR assignment, interrupt route, and READY | Config-read timeout or missing enumeration step | `timeout -> retry_config_read -> stale_device_state` | Review `hardware_diag/pcie_device_enumeration.md` | Pass if ordered probe sequence is preserved; fail if retry path leaves device state stale |
| Device probe sequence | Capabilities read succeeds and health check passes before READY | Capability read timeout | `actual_event=read_capabilities_timeout` | Review `hardware_diag/device_probe_sequence.md` | Pass if health check gates READY state; fail if degraded state is not surfaced |
| Degraded sensor | Sensor timeout marks subsystem unhealthy and blocks false READY state | Sensor read timeout | `unhealthy_subsystem=sensor_probe_path` | Review `device_diag/device_health_report.json` | Pass if degraded state is reported and recovery path is explicit; fail if device is marked healthy without recovery |
| Reconnect recovery | Reconnect clears stale state before health passes | Reconnect occurs but stale state remains | `device_reconnect -> state_refresh -> health_check_pass` | Review `device_diag/reconnect_recovery.md` | Pass if state refresh occurs before health pass; fail if reconnect alone is treated as recovery |
| Heartbeat timing | Worker ACK arrives before timeout deadline | ACK missed timeout window | `expected_event=heartbeat_ack`, `actual_event=heartbeat_timeout` | Review `protocol_timing/heartbeat_timeout_window.md` | Pass if missed window is surfaced as first divergence; fail if only late downstream unavailability is reported |

## Review Notes

This matrix is designed to make DetTrace diagnostics easy to review like a hardware/software validation checklist.

The focus is:

- expected behavior
- observed failure signal
- replay evidence
- validation command
- pass/fail criterion
- safe diagnostic interpretation

## Safe Claim

DetTrace demonstrates hardware-diagnostic test-spec review workflows using simulated, replayable device and protocol traces.
