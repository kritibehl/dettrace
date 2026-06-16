# Memory/State Validation

## Scope

This is state validation for replay traces, not memory allocator, kernel memory, or VM implementation work.

## Example state checks

| State | Expected | Observed | Status |
|---|---|---|---|
| session_state | READY | READY | PASS |
| retry_window | CLOSED | CLOSED | PASS |
| ack_state | RECEIVED | MISSED_THEN_RECEIVED | WARN |
| stale_state | false | false | PASS |

## Debugging value

Replay state validation surfaces transient state violations that may be hidden by eventual recovery.
