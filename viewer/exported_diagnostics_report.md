# Exported Diagnostics Report

## Summary

- workflow: `io-transport-replay-validation`
- trace count: `5`
- validation pass count: `5`
- validation fail count: `0`

## Replay results

### usb-reconnect-recovery

- first divergence index: `2`
- expected event: `configuration_set`
- actual event: `disconnect`
- computed status: `PASS`
- validation passed: `True`
- reason: disconnect was recovered through reconnect, descriptor re-read, configuration_set, and device_ready

### pcie-style-enumeration-failure

- first divergence index: `1`
- expected event: `config_read`
- actual event: `config_read_timeout`
- computed status: `FAIL`
- validation passed: `True`
- reason: enumeration did not reach BAR assignment or ready state after config-read timeout

### displayport-style-link-training-recovery

- first divergence index: `2`
- expected event: `lane_align`
- actual event: `lane_align_timeout`
- computed status: `PASS`
- validation passed: `True`
- reason: link-training timeout recovered after retry and reached display_active

### accessory-disconnect-recovery

- first divergence index: `2`
- expected event: `session_ready`
- actual event: `disconnect`
- computed status: `PASS`
- validation passed: `True`
- reason: accessory disconnect recovered through reconnect and capability re-read

### transport-timeout-retry-chain

- first divergence index: `1`
- expected event: `ack_received`
- actual event: `timeout`
- computed status: `PASS`
- validation passed: `True`
- reason: timeout chain recovered after retry_send and final ack_received
