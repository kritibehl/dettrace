# Replay Performance Notes

This is a lightweight performance-analysis note for DetTrace replay workflows.

## Observed stages

    parse_trace -> compare_events -> detect_divergence -> generate_report

## Bottleneck candidate

    compare_events

## Safe scope

This documents replay latency and flamegraph-style analysis concepts. It does not claim production perf, kernel profiling, or real perf/eBPF integration.
