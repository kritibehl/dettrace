# Trace → Divergence → Replay

```text
Raw Trace / Events
        |
        v
Expected vs Actual Sequence
        |
        v
First Divergence Detection
        |
        v
Replay Diff + Root-Cause Panel
        |
        v
Visual Report / CLI Output / Regression Evidence
Example
Expected: cs_assert -> spi_write -> spi_read -> cs_deassert
Actual:   cs_assert -> spi_write -> timeout  -> retry_transfer

First divergence:
index=2
expected=spi_read
actual=timeout

