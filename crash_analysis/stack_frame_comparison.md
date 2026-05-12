# Stack Frame Comparison

## Scenario

Simulated symbolicated crash comparison for DetTrace device-session workflow.

This is not a real Apple crash report. It is a simulated crash-symbolication proof artifact.

## Expected frame

```text
SerialTransport::readHeartbeat
Actual frame
SerialTransport::disconnect
First mismatched frame
index: 0
Mismatched subsystem
SerialTransport / DeviceSession lifecycle
Probable defect class
disconnect-before-heartbeat
Triage summary

The expected path reads a heartbeat before device state transition.

The actual crash path disconnects first, suggesting the device lifecycle moved into disconnect handling before the heartbeat path completed.
