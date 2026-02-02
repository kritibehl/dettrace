# DetTrace — Deterministic Execution Replay & Invariant Verification (C++)

DetTrace is a lightweight engine for **recording execution events**, **replaying them deterministically**, and **verifying correctness invariants** across runs. It is designed to make nondeterministic behavior reproducible, catch subtle ordering bugs, and provide minimal diffs when behavior diverges.

> Core idea: **Even when invariants pass, behavior can still diverge.** DetTrace detects the **first divergence** deterministically and explains it.

---

## Why DetTrace

Real systems fail in ways that are hard to reproduce:
- flaky tests caused by nondeterminism
- heisenbugs due to scheduling differences
- “passed invariants” but different outcomes (behavioral drift)

DetTrace provides three strong guarantees:
1. **Deterministic traces**: record a stable event sequence
2. **Invariant verification**: assert correctness constraints over events
3. **Replay enforcement**: validate a live run against an expected trace and fail on the first mismatch

---

## What it does (tight scope, high signal)

- Records execution events: `TASK_ENQUEUED`, `TASK_DEQUEUED`, `TASK_STARTED`, `TASK_FINISHED`
- Persists traces in **JSONL** (one JSON per line)
- Replays traces deterministically (trace-driven replay)
- Verifies invariants (ordering, state-machine validity, no duplicates)
- Detects divergence and prints the **first mismatch**
- Enforces replay correctness with **ReplayGuard** (fail-fast)

---

## Architecture (high level)

**Recorder → Trace (JSONL) → (Verifier / Diff / Replayer / ReplayGuard)**

- **Recorder**: assigns monotonic seq ids and stores events
- **Trace I/O**: writes/reads JSONL traces
- **Invariant Verifier**: checks ordering + valid state transitions
- **Diff**: finds first semantic mismatch between traces
- **Replayer**: trace-driven reconstruction
- **ReplayGuard**: validates a live event stream against expected trace (fail-fast)

---

## Quickstart

### Build
```bash
cmake -S . -B build
cmake --build build -j
