# Runtime Replay Consistency Report

## Summary

DetTrace includes a C++ multithreaded replay-ordering validation test.

## Scenario

Two worker threads record replay events with logical timestamps.

The replay normalizes events by logical time and compares observed ordering against the expected runtime trace.

## Expected trace

    request_send -> ack_received -> transaction_complete

## Observed trace

    request_send -> timeout -> retry_send -> ack_received

## First divergence

- index: `1`
- expected event: `ack_received`
- observed event: `timeout`

## Validation

The test confirms that nondeterministic producer ordering can be normalized and checked against deterministic replay expectations.

## Command

    cmake -S . -B build
    cmake --build build
    ctest --test-dir build --output-on-failure

## Safe scope

This validates replay ordering and first-divergence detection for simulated runtime traces.

It does not claim production runtime implementation, kernel scheduler work, or OS thread-library ownership.
