# Flaky Case 1 — Ordering-sensitive concurrent failure

## Summary

This example shows how DetTrace turns a concurrent ordering drift into a reproducible debugging artifact.

The baseline run dequeues task `1` first.  
The divergent run dequeues task `2` first.

DetTrace catches the first divergence at event index `5`:

- **Expected:** `TASK_DEQUEUED task=1 worker=0 queue=0`
- **Actual:** `TASK_DEQUEUED task=2 worker=0 queue=0`

## Why this matters

The system does not merely log events. It detects the first point where execution deviates from the expected schedule, making flaky behavior inspectable and reproducible.

## Walkthrough

1. Generate the expected trace from a stable concurrent execution.
2. Validate invariants on the expected trace.
3. Run guarded execution against the expected schedule.
4. Inject divergence by flipping the first two dequeued tasks.
5. Catch the first mismatch deterministically.
6. Inspect the trace artifacts.

## Artifacts

- Baseline trace: `artifacts/expected.jsonl`
- Divergent trace: `artifacts/actual.jsonl`
- Replayed trace: `artifacts/replayed.jsonl`
- Guarded passing trace: `artifacts/guarded_ok.jsonl`

## Observed first divergence

At event index `5`:

- Expected event: `TASK_DEQUEUED task=1 worker=0 queue=0`
- Actual event: `TASK_DEQUEUED task=2 worker=0 queue=0`

This turns a flaky ordering bug into a concrete root-cause artifact.

## Intended outcome

DetTrace should let someone:

- capture a flaky concurrent run
- replay it deterministically
- identify the first divergence point
- inspect a reproducible debugging artifact instead of a nondeterministic failure
