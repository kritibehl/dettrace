# Process Timeline Replay

## Expected

    process_start -> open -> read -> write -> close -> process_exit

## Actual

    process_start -> open -> read_error -> retry_read -> degraded_exit

## First divergence

    expected_event: write
    actual_event: read_error

## Safe claim

This models process/syscall timeline replay for diagnostics. It does not claim kernel, eBPF, or OS tracing implementation.
