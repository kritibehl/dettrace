# Runtime Diagnostics: First Divergence Report

## Expected

    request_send -> ack_received -> transaction_complete

## Observed

    request_send -> timeout -> retry_send -> timeout -> retry_send -> ack_received -> transaction_complete

## First divergence

- index: `1`
- expected: `ack_received`
- observed: `timeout`
- likely root cause: `timeout_chain`

## Debugging value

The trace eventually completes, but replay diagnostics identify the earlier reliability break: the first acknowledgement was missed.
