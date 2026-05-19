# SystemVerilog FIFO Verification Lab

This project is a directed FIFO verification lab built using SystemVerilog RTL and testbench workflows.

## Scope

The lab validates:

- reset behavior
- enqueue/dequeue correctness
- full and empty flag transitions
- overflow and underflow handling
- FIFO ordering correctness

## Verification Artifacts

Docs:

- docs/verification_plan.md
- docs/testbench_matrix.md
- docs/assertion_list.md
- docs/corner_case_report.md

## Methodology

The verification flow uses:

- directed testbench scenarios
- assertion checks
- expected-vs-actual validation
- corner-case analysis
- simulation review

## Safe claim

This is a directed verification lab for learning and validation workflows. It is not production ASIC verification infrastructure.
