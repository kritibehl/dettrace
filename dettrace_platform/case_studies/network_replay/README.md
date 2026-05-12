# Serial / RPC / Network Failure Replay Pack

These replay packs model trace-driven failure scenarios for device-cloud and distributed debugging workflows.

They are simulated traces, not production Apple infrastructure.

## Scenarios

- `serial_disconnect.json`
- `rpc_timeout_chain.json`
- `dns_retry_storm.json`
- `network_partition_case.json`

## Failure modes

- serial disconnect
- RPC timeout chain
- DNS retry storm
- network partition / heartbeat timeout

## DetTrace output

These packs can be ingested through:

```bash
curl -X POST http://127.0.0.1:8010/ingest \
  -H "Content-Type: application/json" \
  --data @dettrace_platform/case_studies/network_replay/dns_retry_storm.json
DetTrace can produce:

incident fingerprint
retry-storm detection
timeout-chain detection
first-divergence evidence when baseline/candidate traces are present
root-cause explanation
timeline export
report output
