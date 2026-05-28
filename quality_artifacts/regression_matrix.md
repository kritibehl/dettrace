# I/O Transport Regression Matrix

| Scenario | Expected Outcome | Validation |
|---|---|---|
| USB reconnect | PASS | reconnect reaches device_ready |
| PCIe-style enumeration | FAIL | config_read_timeout isolated |
| DisplayPort-style link training | PASS | retry reaches display_active |
| Accessory disconnect | PASS | reconnect reaches session_ready |
| Timeout/retry chain | PASS | retries reach transaction_complete |
