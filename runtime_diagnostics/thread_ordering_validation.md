# Thread Ordering Validation

## Scope

Simulated ordering validation for replay traces.

## Ordering rule

    timeout_handler must not trigger before ack_deadline expires

## Observed sequence

    request_send -> timeout_handler -> retry_send -> ack_received

## Validation result

- ordering status: `WARN`
- reason: timeout handler ran before the expected ACK path completed
- likely family: `timeout_chain`

Safe scope: replay-order validation only. Not kernel scheduler, thread library, or runtime implementation.
