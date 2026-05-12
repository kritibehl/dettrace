# Heartbeat Timeout Window Analysis

This note documents a software-level protocol timing scenario for DetTrace++.

It is not electrical signal-integrity analysis. It is trace-driven timing validation for protocol sequencing.

## Scenario

A controller expects a worker heartbeat acknowledgement within a bounded timeout window.

## Expected sequence

    heartbeat_send -> heartbeat_ack

## Candidate failure sequence

    heartbeat_send -> heartbeat_timeout

## Timing window

    heartbeat_send_time: 0 ms
    expected_ack_deadline: 250 ms
    observed_ack_time: none
    timeout_fired_at: 251 ms

## First divergence

    expected_event: heartbeat_ack
    actual_event: heartbeat_timeout
    first_divergence_index: 1

## Why this matters

Late logs usually show only that a node was unavailable.

Replay timing analysis shows that the first correctness break happened when the heartbeat acknowledgement missed the protocol timeout window.

## Safe claim

DetTrace models protocol timing and sequencing failures using replayable software traces. It does not model physical-layer signal integrity.
