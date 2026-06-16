# UNIX-Style Debugging Workflow

## Local validation commands

    git status
    cmake -S . -B build
    cmake --build build
    ctest --test-dir build --output-on-failure

## Trace inspection

    cat io_transport_validation/timeout_retry_chain.json
    python3 tui/replay_explorer.py protocol_diag/spi_transfer_timeout.json
    python3 failure_similarity/search_similar_failures.py io_transport_validation/timeout_retry_chain.json

## Report inspection

    cat regression_intelligence/build_scorecard.md
    cat failure_similarity/failure_similarity_report.md
    open reports/sample_replay_timeline_report.html

## Safe scope

UNIX-style local debugging workflow for replay diagnostics. Not production on-call, kernel debugging, or hardware-lab validation.
