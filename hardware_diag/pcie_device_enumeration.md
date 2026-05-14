# PCIe Device Enumeration Diagnostic Simulation

This is a protocol-state debugging note, not PCIe driver development or kernel engineering.

## Expected enumeration flow

    bus_scan -> config_read -> bar_assign -> interrupt_route -> device_ready

## Candidate failure flow

    bus_scan -> config_read -> timeout -> retry_config_read -> stale_device_state

## Diagnostic interpretation

The expected flow reaches `device_ready` after configuration and BAR assignment.

The candidate flow times out during config read and retries while the device state remains stale.

## Safe claim

DetTrace models device-enumeration timing and protocol-state failures through replayable diagnostic traces.
