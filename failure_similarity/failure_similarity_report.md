# Failure Similarity Search Report

## Safe claim

heuristic replay failure-similarity search; not ML or production incident ranking

## Most similar failure

- family: `timeout`
- similarity: `0.25`
- confidence: `0.69`
- likely root cause: `timeout_chain`
- evidence: `['timeout']`

## Top matches

- `timeout` similarity=`0.25` confidence=`0.69` evidence=`['timeout']` root_cause=`timeout_chain`
- `retry_storm` similarity=`0.25` confidence=`0.69` evidence=`['retry_send']` root_cause=`unbounded_or_duplicate_retry`
