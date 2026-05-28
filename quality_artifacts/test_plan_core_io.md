# Core I/O-Style Replay Test Plan

## Goal

Validate I/O transport recovery and failure isolation through replayable diagnostic traces.

## Scope

- USB reconnect recovery
- PCIe-style enumeration failure
- DisplayPort-style link training recovery
- accessory disconnect/reconnect
- timeout/retry chains

## Pass criteria

- first divergence is identified
- recovery path is validated when expected
- failed enumeration remains marked FAIL
- diagnostic reason is produced
- replay report is generated
