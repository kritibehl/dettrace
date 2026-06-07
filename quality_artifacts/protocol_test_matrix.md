# Protocol Test Matrix

| Protocol | Failure | Detection | Recovery Validated | Status |
|-----------|-----------|-----------|-----------|-----------|
| USB | reconnect | PASS | PASS | PASS |
| USB | timeout | PASS | PASS | PASS |
| PCIe | enumeration failure | PASS | N/A | PASS |
| DisplayPort | link recovery | PASS | PASS | PASS |
| SPI | transfer timeout | PASS | PASS | PASS |
| BLE | reconnect | PASS | PASS | PASS |
| UART | checksum error | PASS | N/A | PASS |
| I2C | missing ACK | PASS | N/A | PASS |
| TCP | retransmit | PASS | PASS | PASS |

Coverage goal:

- protocol sequencing
- timeout handling
- reconnect behavior
- recovery validation
- first-divergence isolation
