# From Traces to Replay: Reconstructing Retry Storms with OpenTelemetry

## Scenario

DetTrace ingests OpenTelemetry-style spans from a retry storm involving:

- frontend
- checkout-service
- payment-service

## Detected Pattern

- failure fingerprint: `retry_storm_timeout_chain`
- retry count: 4
- timeout-chain events: 5
- root cause: checkout-service repeatedly retried payment-service after timeout responses

## Why Logs Alone Are Not Enough

Logs show the retries after they happen.

DetTrace converts span data into replayable event timelines so the incident can be reconstructed, tagged, searched, and compared against historical failures.

## Output

DetTrace generated:

- replayable timeline
- failure tags
- retry-storm fingerprint
- timeout-chain detection
- root-cause explanation

## Incident Summary

```json
{
  "fingerprint": "retry_storm_timeout_chain",
  "retry_count": 4,
  "timeout_chain_events": 5,
  "root_cause": "checkout-service entered a retry storm against payment-service"
}
