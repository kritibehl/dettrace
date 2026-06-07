# Regression Intelligence Report

- build: `candidate_42`
- known regression risk: `high`
- release recommendation: `hold`

## Matched failures

- `reg_retry_storm_001` family=`retry_storm` risk=`high` confidence=`0.91` signals=`['duplicate_retry_window', 'retry_storm', 'timeout_chain']` action=block release until retry backoff and ACK ordering are reviewed
