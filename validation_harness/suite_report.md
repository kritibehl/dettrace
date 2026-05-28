# I/O Transport Suite Report

## Safe claim

repeatable simulated I/O transport replay validation; not hardware lab, driver, firmware, or kernel ownership

## Summary

- runs: `500`
- scenario count: `20`
- total validations: `10000`
- pass: `10000`
- validation failures: `0`
- family counts: `{'usb': 2000, 'pcie': 2000, 'displayport': 2000, 'accessory': 2000, 'transport': 2000}`
- expected status counts: `{'FAIL': 7500, 'PASS': 2500}`

## Interpretation

The validation harness repeatedly executes a 20-scenario I/O transport failure corpus and confirms that expected recovery and expected failure outcomes are classified consistently.
