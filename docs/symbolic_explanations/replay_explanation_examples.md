# Symbolic Replay Explanation Examples

DetTrace attaches symbolic explanations to replay failures so the output reads like internal debugging tooling.

## Example: Timer missed tick

- probable root cause: timer event skipped before ISR service
- likely affected subsystem: firmware timer / ISR scheduling path
- confidence score: 0.86
- evidence: expected `irq_assert`, actual `tick_miss`

## Example: GPIO interrupt race

- probable root cause: second GPIO edge arrived before ack/clear completed
- likely affected subsystem: GPIO interrupt handling path
- confidence score: 0.88
- evidence: expected `gpio_ack`, actual `gpio_edge`

## Example: serial disconnect

- probable root cause: device disconnected before heartbeat read
- likely affected subsystem: serial lifecycle / device-agent connection path
- confidence score: 0.82
- evidence: expected `serial_read`, actual `serial_disconnect`

## Example: DNS retry storm

- probable root cause: retry amplification against DNS resolver
- likely affected subsystem: network dependency resolution path
- confidence score: 0.9
- evidence: 4 retry events and timeout-chain fingerprint
