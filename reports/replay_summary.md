# Replay Summary

- Trace file: `artifacts/expected.jsonl`
- Replay status: guarded replay passed for expected schedule
- Divergence status: injected divergence detected successfully
- First divergence event: `5`
- Expected event: `TASK_DEQUEUED task=1 worker=0 queue=0`
- Actual event: `TASK_DEQUEUED task=2 worker=0 queue=0`
- Invariant status: expected trace invariants passed
- Notes: divergence was injected by flipping the first two dequeued tasks
