# Bug Reproduction Matrix

| Bug Class | Input Trace | First Divergence | Expected | Observed | Reproduction Command |
|---|---|---:|---|---|---|
| timeout chain | `io_transport_validation/timeout_retry_chain.json` | 1 | `ack_received` | `timeout` | `python3 failure_similarity/search_similar_failures.py io_transport_validation/timeout_retry_chain.json` |
| enumeration failure | `io_transport_validation/pcie_enumeration_trace.json` | 1 | `config_read` | `config_read_timeout` | `python3 io_transport_validation/run_transport_replay.py` |
| display recovery | `io_transport_validation/displayport_link_training_trace.json` | 2 | `lane_align` | `lane_align_timeout` | `python3 io_transport_validation/run_transport_replay.py` |
| interrupt ordering | `device_replay/sample_device_trace.json` | 4 | `interrupt_cleared` | `sensor_read` | `make -C device_replay run` |
| retry storm | `failure_library/io_failure_corpus.json` | varies | bounded retry | retry storm | `python3 regression_intelligence/build_regression_radar.py --build candidate_42 --signals retry_storm,timeout_chain,duplicate_retry_window` |
