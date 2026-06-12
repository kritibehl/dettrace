# First-Divergence Debugging Walkthrough

## Scenario

A timeout/retry transport trace reaches a later successful transaction, but the replay should still explain where behavior first diverged from the expected path.

## Expected flow

    request_send -> ack_received -> transaction_complete

## Observed flow

    request_send -> timeout -> retry_send -> timeout -> retry_send -> ack_received -> transaction_complete

## First divergence

    index: 1
    expected_event: ack_received
    observed_event: timeout

## Why this matters

Later logs may show that the transaction eventually completed.

Replay diagnostics show the earlier reliability break: the first acknowledgement was missed, triggering timeout and retry behavior.

## Debugging path

1. Compare expected vs observed event sequence.
2. Identify the first divergent event.
3. Map the divergent event to a failure family.
4. Search for similar historical failures.
5. Run build regression radar if the signal appears in a candidate build.
6. Generate a reviewer-readable report.

## Safe scope

This walkthrough demonstrates replay-based debugging methodology. It does not claim production incident automation or hardware validation ownership.
