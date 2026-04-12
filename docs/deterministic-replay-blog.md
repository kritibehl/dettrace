# How I built a deterministic replay system in C++17 — and what it taught me about concurrency bugs

## Why deterministic replay matters

Concurrency bugs are not just hard — they are nondeterministic. The same program, same input, different execution.

Traditional debugging fails because:
- Logs are incomplete
- Timing changes behavior
- Bugs disappear under observation

DetTrace was built to make these failures reproducible.

---

## Core idea

Record execution as an ordered sequence of events:

- TASK_ENQUEUED
- TASK_DEQUEUED
- WORKER_ASSIGNED
- STATE_TRANSITION

Then replay and compare.

---

## First divergence principle

The *first mismatch* is the root cause.

Everything after that is noise.

DetTrace isolates:
Event 5:
Expected: TASK_DEQUEUED task=1
Actual:   TASK_DEQUEUED task=2

This is where the system diverged.

---

## Artifact preservation

Each run produces:

- expected.jsonl
- actual.jsonl
- replayed.jsonl
- divergence_report.json

This allows post-mortem debugging without rerunning the system.

---

## Real bug DetTrace caught

Scenario: duplicate dequeue under race condition

Two workers read the queue simultaneously.

Result:
- Task 1 processed twice
- Task 2 skipped

DetTrace detected divergence at event index 5.

---

## What this taught me

1. The root cause is earlier than failure
2. Reproducibility > logging
3. Determinism is a design choice

---

## Why this matters

As systems scale, concurrency bugs dominate failure modes.

Deterministic replay turns debugging from guesswork into analysis.

