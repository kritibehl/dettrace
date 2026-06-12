# Test Infrastructure Mode

DetTrace can be read as a test-infrastructure workflow for replay diagnostics.

## What it validates

- replay traces execute consistently
- first divergence is isolated
- expected failure outcomes are classified correctly
- known regression signals produce release-risk scores
- protocol failures map to root-cause families
- generated reports are reviewer-readable

## Core commands

    cmake -S . -B build
    cmake --build build
    ctest --test-dir build --output-on-failure

    python3 validation_harness/run_transport_suite.py --runs 500

    python3 regression_intelligence/build_regression_radar.py \
      --build candidate_42 \
      --signals retry_storm,timeout_chain,duplicate_retry_window,config_read_timeout

    python3 failure_similarity/search_similar_failures.py \
      io_transport_validation/timeout_retry_chain.json

## Safe scope

This is replay-based test infrastructure and diagnostics tooling.

It does not claim production CI ownership, hardware-lab testing, drivers, firmware, kernel engineering, or real hardware emulation.
