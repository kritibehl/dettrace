# Regression Reproduction Steps

## Regression

gRPC lifecycle replay diverges from successful completion path and enters `deadline_exceeded`.

## Input artifact

```text
dettrace_platform/case_studies/protocol_replay/grpc_timeout_lifecycle.json
Steps
Start the DetTrace++ API.
Ingest grpc_timeout_lifecycle.json.
Inspect the returned analysis.divergence object.
Confirm expected event is rpc_complete.
Confirm actual event is deadline_exceeded.
Generate /report/{incident_id} for triage output.
Expected behavior
rpc_complete -> response_received
Actual behavior
deadline_exceeded -> handler_cancelled
Validation target

The replay system should preserve:

first-divergence evidence
timeout-chain reasoning
root-cause summary
affected service lifecycle path
