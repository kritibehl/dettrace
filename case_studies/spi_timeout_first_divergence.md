# Case Study: SPI Timeout First Divergence

## Summary

This case study shows how DetTrace identifies the first divergence in a SPI-style protocol replay.

This is a diagnostic simulation, not SPI driver or firmware development.

## Expected flow

    cs_assert -> spi_write -> spi_read -> cs_deassert -> transfer_complete

## Actual flow

    cs_assert -> spi_write -> timeout -> retry_transfer -> stale_device_state

## First divergence

    index: 2
    expected_event: spi_read
    actual_event: timeout

## Probable defect type

    spi_read_timeout

## Why logs are not enough

A normal log stream may show only the later retry or stale device state.

DetTrace shows the earlier correctness break: the transfer failed when `spi_read` did not occur and the replay entered `timeout`.

## Replay evidence

Source artifact:

    protocol_diag/spi_transfer_timeout.json

Visual report:

    reports/trace_timeline.html

CLI inspection:

    python3 tui/replay_explorer.py protocol_diag/spi_transfer_timeout.json

## Safe claim

This demonstrates protocol-state replay and first-divergence debugging for embedded-adjacent diagnostics. It does not claim driver, firmware, or hardware bus implementation.
