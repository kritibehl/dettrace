# DetTrace Case Study

## Problem
Distributed failures are hard to explain because logs often show late symptoms instead of first cause.

## Design
DetTrace replays expected and observed traces, isolates first divergence, and classifies root-cause patterns.

## Validation
Validated with deterministic replay scenarios run in CI (C++ Replay Regression workflow).

## Tradeoffs
Requires structured trace input, but produces clearer debugging evidence.
