# FIFO Testbench Matrix

| Scenario | Description | Expected Result |
|---|---|---|
| reset_sequence | apply reset before traffic | FIFO becomes empty |
| enqueue_sequence | push values into FIFO | values stored in order |
| dequeue_sequence | pop stored values | values returned in order |
| full_condition | fill FIFO completely | full flag asserted |
| empty_condition | read empty FIFO | empty flag asserted |
| overflow_case | write when full | write rejected |
| underflow_case | read when empty | read rejected |
| alternating_rw | alternating enqueue/dequeue | stable pointer movement |

## Verification Method

Each scenario is validated through:

- simulation output
- assertion checks
- waveform review
- expected-vs-actual state comparison
