# Protocol Validation Matrix

| Protocol | Failure Scenario | First Divergence | Detected Root Cause | Result |
|-----------|-----------|-----------|-----------|-----------|
| SPI-style | read timeout | spi_read -> timeout | missing response | PASS |
| USB-style | reconnect recovery | reconnect ordering | stale device state | PASS |
| PCIe-style | enumeration failure | config read timeout | enumeration failure | PASS |
| DisplayPort-style | link training retry | lane timeout | link recovery required | PASS |
| BLE-style | reconnect lifecycle | disconnect before ready | stale session | PASS |
| UART-style | checksum failure | checksum_error | frame corruption | PASS |
| I2C-style | ack timeout | data_ack -> timeout | missing_ack | PASS |
| TCP-style | retransmit sequence | ack_received -> timeout | timeout chain | PASS |

Safe scope: protocol-state replay simulation for diagnostics and validation review.
