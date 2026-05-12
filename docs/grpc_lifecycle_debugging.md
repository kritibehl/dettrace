# gRPC Lifecycle Debugging with DetTrace++

This document describes a simulated gRPC lifecycle replay case.

It is a trace-driven debugging artifact, not a production gRPC capture.

## Scenario

A baseline RPC completes successfully before deadline.

The candidate execution diverges when the client reaches `deadline_exceeded` before the server completes the handler path.

## Expected lifecycle

```text
channel_ready -> rpc_start -> handler_start -> rpc_complete -> response_received
Actual lifecycle
channel_ready -> rpc_start -> handler_start -> deadline_exceeded -> handler_cancelled
First divergence
expected_event: rpc_complete
actual_event: deadline_exceeded
Probable root cause

The RPC deadline expired before the server completed request handling.

Likely affected subsystem
grpc-client deadline handling / grpc-server handler lifecycle
Debugging value

This replay pack demonstrates:

RPC lifecycle debugging
service communication failure analysis
timeout/deadline propagation
backend infrastructure debugging
expected-vs-actual service flow comparison
Reproduction

Start DetTrace++:

cd dettrace_platform
uvicorn app.main:app --host 127.0.0.1 --port 8010

Ingest the replay pack:

curl -X POST http://127.0.0.1:8010/ingest \
  -H "Content-Type: application/json" \
  --data @case_studies/protocol_replay/grpc_timeout_lifecycle.json

