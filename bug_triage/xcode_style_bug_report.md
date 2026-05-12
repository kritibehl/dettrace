# Xcode-Style Bug Report

## Title

Replay divergence when gRPC lifecycle times out before server handler completion.

## Component

DetTrace++ / protocol replay / gRPC lifecycle validation

## Build / Environment

- Local FastAPI replay service
- Simulated protocol replay pack
- JSON trace artifact: `grpc_timeout_lifecycle.json`

## Severity

Medium

## Reproducibility

Always reproducible with the included replay pack.

## Expected Result

```text
channel_ready -> rpc_start -> handler_start -> rpc_complete -> response_received
Actual Result
channel_ready -> rpc_start -> handler_start -> deadline_exceeded -> handler_cancelled
First Divergence
expected_event: rpc_complete
actual_event: deadline_exceeded
Root-Cause Hypothesis

The client-side deadline expires before the server handler can complete, causing cancellation to propagate through the RPC lifecycle.

Suggested Investigation
Inspect client timeout/deadline configuration
Compare server handler latency against deadline budget
Confirm cancellation propagation behavior
Validate retry behavior after deadline exceeded
