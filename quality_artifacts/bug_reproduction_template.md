# Bug Reproduction Template

## Title

Transport replay divergence in `<scenario>`.

## Input trace

`io_transport_validation/<trace>.json`

## Steps

1. Run `python3 io_transport_validation/run_transport_replay.py`
2. Open `io_transport_validation/transport_validation_report.md`
3. Identify first divergence index.
4. Compare expected vs actual event.
5. Validate recovery or failure status.

## Expected behavior

Document expected event and final state.

## Actual behavior

Document actual event and final state.

## Diagnostic reason

Document replay-generated reason.
