# DetTrace

DetTrace is a deterministic replay and divergence-analysis system for turning flaky concurrent failures into reproducible root-cause artifacts.

It is positioned as:
- serious systems tooling
- C++ debugging maturity
- flaky-test stabilization platform
- trace-driven root-cause analysis

## What it demonstrates

- capture execution traces from concurrent runs
- replay executions deterministically
- detect the first point of divergence
- explain violated invariants
- generate reproducible debugging artifacts

## Core story

A small concurrent demo exhibits a flaky failure.

DetTrace:
1. captures the trace
2. replays the failure deterministically
3. pinpoints the first divergence event
4. explains the violated invariant
5. emits replay and divergence reports

## Planned repo layout

- `trace/` — trace capture and serialization
- `replay/` — replay engine
- `analysis/` — divergence and invariant analysis
- `examples/flaky_case_1/` — end-to-end flaky case walkthrough
- `reports/` — replay summary and divergence reports
- `viewer/` — timeline and divergence visualization
- `tests/` — unit, integration, and regression coverage
- `bench/` — overhead and consistency measurements

## Definition of done

DetTrace is done when someone can:
- run one flaky example
- capture a trace
- replay it deterministically
- see the first divergence
- inspect one clean report
- see measured overhead
