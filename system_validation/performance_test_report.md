# Replay Performance Test Report

## Scope

Lightweight performance summary for replay/test-infrastructure workflows.

## Workloads

| Workload | Runs | Scenario Count | Total Validations | Result |
|---|---:|---:|---:|---|
| transport validation suite | 500 | 20 | 10,000 | PASS |
| C++ replay regression | 1 | 3 | 3 | PASS |
| build regression radar | 1 | 3 known regressions | 2 matched | HOLD |

## Notes

The validation harness is intentionally deterministic and lightweight so it can run as repeatable test infrastructure.

Safe scope: local replay validation performance, not production benchmarking.
