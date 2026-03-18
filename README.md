# DetTrace

**Deterministic replay and divergence analysis for concurrent C++ systems.**

DetTrace turns flaky concurrent failures into reproducible debugging artifacts. Given an execution that may behave differently across runs, DetTrace records an expected trace, validates execution against it under guarded replay, and identifies the exact first point where observed behavior diverges from expectation.

---

## What it does

- Generates an expected concurrent execution trace and validates invariants against it
- Validates execution against an expected ordering during guarded replay
- Detects the **first point of divergence** deterministically
- Saves divergent trace artifacts even when replay throws, preserving failure context
- Produces a structured divergence report identifying the mismatched events

---

## Quick start

```bash
./scripts/run_demo.sh
```

This builds the project, runs the demo, generates a divergence report, and prints a preview of the resulting traces.

---

## Concrete example

The project includes a real flaky-case walkthrough in [`examples/flaky_case_1/`](examples/flaky_case_1/).

Observed first divergence at event index `5`:

- Expected: `TASK_DEQUEUED task=1 worker=0 queue=0`
- Actual: `TASK_DEQUEUED task=2 worker=0 queue=0`

A different task was dequeued than the expected schedule required. DetTrace catches this deterministically and reports exactly where the traces split.

---

## Artifacts

Each run produces the following under `artifacts/`:

- `expected.jsonl` — reference trace with validated invariants
- `actual.jsonl` — observed trace from the divergent run
- `replayed.jsonl` — replayed reference trace
- `guarded_ok.jsonl` — guarded execution that matches the expected schedule

Divergence analysis is written to `reports/divergence_report.json`.

---

## Repo structure

```text
analysis/          # Divergence detection and invariant checking
trace/             # Trace recording and serialization
replay/            # Replay engine
examples/          # Flaky case walkthroughs
  flaky_case_1/    # Concrete documented ordering-divergence case
artifacts/         # Generated trace files
reports/           # Generated divergence reports
scripts/           # Demo runner and report generator
tests/
  unit/
  integration/     # test_flaky_case_1: verifies divergence at index 5
  regression/
bench/             # Overhead benchmarks
docs/
viewer/            # Trace viewer (WIP)
```

---

## Running tests

```bash
cmake -B build && cmake --build build
cd build && ctest --output-on-failure
```

The integration test `test_flaky_case_1` verifies end-to-end behavior:

- the demo binary runs successfully
- expected and actual traces are created
- first divergence exists and is exactly at index 5
- expected event is `TASK_DEQUEUED task=1`
- actual event is `TASK_DEQUEUED task=2`

---

## Generating a divergence report manually

```bash
python scripts/generate_divergence_report.py
```

This reads `artifacts/expected.jsonl` and `artifacts/actual.jsonl`, finds the first mismatch, and writes `reports/divergence_report.json`.

---
---

## Swift companion analyzer

DetTrace includes a **Swift CLI companion** in `dettrace-swift/` that reads C++-generated trace artifacts concurrently using `async/await`, isolates analysis state with an `actor`, and generates structured JSON/Markdown divergence reports.

It includes **3 passing tests** covering:
- identical traces
- known divergence at index 5
- different length traces

```bash
cd dettrace-swift
swift run DetTraceAnalyzer ../artifacts/expected.jsonl ../artifacts/actual.jsonl
---

## Diagnostics viewer

DetTrace includes a lightweight developer-facing diagnostics UI in `viewer/` that makes execution differences easier to inspect for both systems and general SWE audiences.

It provides:
- a side-by-side diff view for passing vs failing executions
- first-divergence highlighting
- rule-based root-cause hints
- invariant status exploration
- a "what changed between runs" summary
- a reproducible scenarios / benchmark page

Run it from the repo root:

```bash
./scripts/serve_viewer.sh
Then open:

http://localhost:8000/viewer/index.html

http://localhost:8000/viewer/benchmarks.html
