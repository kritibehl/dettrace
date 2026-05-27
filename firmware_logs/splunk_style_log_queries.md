# Splunk-Style Firmware Log Queries

This is a structured JSONL telemetry workflow inspired by searchable diagnostics logs.

It does not claim Splunk deployment or production firmware telemetry ownership.

## Query by device

    python3 firmware_logs/query_firmware_logs.py --device-id dev-001

## Query by severity

    python3 firmware_logs/query_firmware_logs.py --severity ERROR

## Query by boot phase

    python3 firmware_logs/query_firmware_logs.py --boot-phase calibration

## Generate summary

    python3 firmware_logs/query_firmware_logs.py --summary

## Diagnostics supported

- calibration failure detection
- retry storm classification
- timeout-chain summary
- failure-family grouping
- boot-phase filtering
