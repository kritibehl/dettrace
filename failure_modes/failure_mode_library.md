# DetTrace Failure-Mode Library

This library summarizes replayable failure modes covered by DetTrace.

| Failure Mode | Example Artifact | First-Divergence Signal | Safe Scope |
|---|---|---|---|
| Missing interrupt clear | `device_replay/sample_device_trace.json` | `interrupt_cleared` vs `sensor_read` | device-event replay |
| SPI timeout | `protocol_diag/spi_transfer_timeout.json` | `spi_read` vs `timeout` | protocol-style diagnostics |
| I2C ACK timeout | `hardware_diag/i2c_timeout_trace.json` | `ack_received` vs `timeout` | hardware-interface simulation |
| USB reconnect | `hardware_diag/usb_device_reconnect.json` | `configuration_set` vs `disconnect` | device lifecycle replay |
| Runtime cache fallback | `runtime_replay_cases/cache_fallback_trace.json` | `shape_A` vs `shape_B` | runtime trace replay |
| Invalid branch target | `runtime_replay_cases/invalid_branch_target_trace.json` | validated vs unchecked branch target | runtime trace replay |
| TLS handshake timeout | `traffic_replay/http_capture_replay_example.json` | `tls_handshake` vs `tls_handshake_timeout` | mock traffic replay |
| Crash-frame mismatch | `crash_analysis/crash_diff_report.json` | `readHeartbeat` vs `disconnect` | crash/stack comparison |

## Safe Claim

This is a replay-debugging failure-mode library for diagnostics and developer-tooling workflows. It does not claim production driver, kernel, packet-capture, firmware, or VM implementation work.
