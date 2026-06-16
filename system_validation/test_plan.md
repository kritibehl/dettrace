# Systems Validation Test Plan

## Goal

Validate DetTrace replay workflows as systems test infrastructure.

## Scope

- reproduce failure traces
- isolate first-divergence behavior
- validate runtime-state invariants
- classify failure modes
- generate regression reports
- document UNIX-style debugging workflows

## Validation commands

    cmake -S . -B build
    cmake --build build
    ctest --test-dir build --output-on-failure

    python3 validation_harness/run_transport_suite.py --runs 500
    python3 regression_intelligence/build_regression_radar.py --build candidate_42 --signals retry_storm,timeout_chain,duplicate_retry_window,config_read_timeout
    python3 failure_similarity/search_similar_failures.py io_transport_validation/timeout_retry_chain.json

## Safe scope

Replay-based systems validation and diagnostics tooling. Not kernel, driver, firmware, hardware-lab, or production CI ownership.
