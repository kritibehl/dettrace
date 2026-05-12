# Simulated macOS-Style Crash Trace Ingestion

This is a simulated debugging workflow, not a real Apple crash-report integration.

## Input

A symbolized stack trace or crash-like event sequence.

## DetTrace analysis

DetTrace compares expected vs actual execution paths and identifies:

- first mismatched stack frame
- likely affected subsystem
- replay divergence index
- probable defect class
