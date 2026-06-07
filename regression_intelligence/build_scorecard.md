# Build Regression Radar Scorecard

## Safe claim

heuristic replay-based build regression radar; not production release automation

## Candidate build

- build: `candidate_42`
- risk score: `100`
- risk level: `high`
- matched regressions: `2`
- historical occurrences: `4`
- release recommendation: `hold`

## Matched failures

- `reg_retry_storm_001` family=`retry_storm` risk=`high` confidence=`0.91` signals=`['duplicate_retry_window', 'retry_storm', 'timeout_chain']` action=block release until retry backoff and ACK ordering are reviewed
- `reg_enum_timeout_002` family=`enumeration_failure` risk=`high` confidence=`0.89` signals=`['config_read_timeout']` action=rerun enumeration replay and verify device_ready is not falsely reported
