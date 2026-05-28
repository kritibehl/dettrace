#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path("io_transport_validation")
REPORT_JSON = ROOT / "transport_validation_report.json"
REPORT_MD = ROOT / "transport_validation_report.md"

TRACE_FILES = [
    "usb_reconnect_trace.json",
    "pcie_enumeration_trace.json",
    "displayport_link_training_trace.json",
    "accessory_disconnect_recovery.json",
    "timeout_retry_chain.json",
]


def load_trace(filename):
    path = ROOT / filename
    data = json.loads(path.read_text())
    data["_file"] = str(path)
    return data


def validate_trace(trace):
    diag = trace["diagnosis"]
    actual_flow = trace["actual_flow"]
    expected_recovery = trace["expected_recovery"]

    first_divergence_valid = (
        diag["first_divergence_index"] < len(actual_flow)
        and actual_flow[diag["first_divergence_index"]] == diag["actual_event"]
    )

    recovery_valid = diag["recovery_observed"] == expected_recovery

    final_state_valid = actual_flow[-1] == diag["final_state"]

    expected_status = "PASS" if (
        first_divergence_valid and recovery_valid and final_state_valid
    ) else "FAIL"

    return {
        "scenario": trace["scenario"],
        "file": trace["_file"],
        "safe_claim": trace["safe_claim"],
        "first_divergence_index": diag["first_divergence_index"],
        "expected_event": diag["expected_event"],
        "actual_event": diag["actual_event"],
        "recovery_observed": diag["recovery_observed"],
        "final_state": diag["final_state"],
        "declared_status": diag["diagnostic_status"],
        "computed_status": expected_status,
        "reason": diag["reason"],
        "validation_passed": expected_status == diag["diagnostic_status"]
    }


def main():
    traces = [load_trace(f) for f in TRACE_FILES]
    results = [validate_trace(t) for t in traces]

    pass_count = sum(1 for r in results if r["validation_passed"])
    fail_count = len(results) - pass_count

    report = {
        "workflow": "io-transport-replay-validation",
        "safe_claim": "I/O transport trace replay and diagnostics; not driver, firmware, or kernel development",
        "trace_count": len(results),
        "validation_pass_count": pass_count,
        "validation_fail_count": fail_count,
        "results": results
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))

    lines = [
        "# I/O Transport Validation Report",
        "",
        "## Safe claim",
        "",
        report["safe_claim"],
        "",
        "## Summary",
        "",
        f"- trace count: `{report['trace_count']}`",
        f"- validation pass count: `{report['validation_pass_count']}`",
        f"- validation fail count: `{report['validation_fail_count']}`",
        "",
        "## Results",
        ""
    ]

    for r in results:
        lines.extend([
            f"### {r['scenario']}",
            "",
            f"- first divergence index: `{r['first_divergence_index']}`",
            f"- expected event: `{r['expected_event']}`",
            f"- actual event: `{r['actual_event']}`",
            f"- recovery observed: `{r['recovery_observed']}`",
            f"- final state: `{r['final_state']}`",
            f"- declared status: `{r['declared_status']}`",
            f"- computed status: `{r['computed_status']}`",
            f"- validation passed: `{r['validation_passed']}`",
            f"- reason: {r['reason']}",
            ""
        ])

    REPORT_MD.write_text("\n".join(lines))
    print(json.dumps(report, indent=2))

    if fail_count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
