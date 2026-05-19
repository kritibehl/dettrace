# FIFO Verification Plan

## Goal

Validate FIFO correctness across reset, enqueue, dequeue, full, empty, overflow, and underflow behavior.

## Verification Scope

The directed verification workflow checks:

- FIFO reset behavior
- enqueue/dequeue correctness
- full flag assertion
- empty flag assertion
- overflow protection
- underflow protection
- data ordering preservation

## Test Strategy

The lab uses:

- directed testbench scenarios
- assertion checks
- waveform review
- corner-case validation

## Pass Criteria

The FIFO passes validation if:

- reset clears state correctly
- enqueue/dequeue ordering remains valid
- full and empty flags transition correctly
- overflow writes are rejected
- underflow reads are rejected
- assertions do not fail

## Safe claim

This is a directed SystemVerilog verification lab, not production ASIC verification infrastructure.
