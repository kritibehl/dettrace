# Systems Regression Report

## Candidate

`candidate_42`

## Signals

- retry_storm
- timeout_chain
- duplicate_retry_window
- config_read_timeout

## Result

- risk score: `100`
- risk level: `high`
- matched regressions: `2`
- release recommendation: `hold`

## Interpretation

The candidate build matches historical retry-storm and enumeration-timeout regression patterns. Replay diagnostics recommend holding release until retry backoff, ACK ordering, and enumeration state transitions are reviewed.
