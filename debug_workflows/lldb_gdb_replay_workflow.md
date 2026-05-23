# LLDB/GDB-Style Replay Debugging Workflow

This is a simulated debugger workflow for replay-based failure analysis.

## Workflow

1. Reproduce failure with replay trace.
2. Inspect first-divergence event.
3. Compare expected vs actual stack/frame/event state.
4. Map divergence to probable subsystem.
5. Generate triage report.

## Example

    expected: SerialTransport::readHeartbeat
    actual:   SerialTransport::disconnect

## Safe claim

This demonstrates debugger-style triage methodology. It does not claim production LLDB/GDB plugin development.
