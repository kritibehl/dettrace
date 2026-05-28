# I/O Transport Validation

This folder contains replay-based I/O transport validation artifacts for Apple Core I/O-style QA positioning.

## Scope

These are trace replay and diagnostics workflows. They do not claim USB/PCIe/DisplayPort driver development, kernel engineering, or firmware ownership.

## Scenarios

- USB reconnect recovery
- PCIe-style enumeration failure isolation
- DisplayPort-style link training recovery
- accessory disconnect/reconnect validation
- timeout/retry chain validation

## Run

    python3 io_transport_validation/run_transport_replay.py

## Expected proof

The workflow reports:

- first divergence index
- expected event
- actual event
- recovery observed
- final state
- PASS/FAIL diagnostic status with reason
