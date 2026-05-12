#!/usr/bin/env python3
import json
from pathlib import Path

INPUT = Path("contract_validation/api_contract_break_case.json")
REPORT = Path("contract_validation/contract_validation_report.json")


def validate_required_fields(obj, required):
    missing = []
    for field in required:
        if field not in obj:
            missing.append(field)
    return missing


def main():
    case = json.loads(INPUT.read_text())
    expected = case["expected_schema"]
    actual = case["actual_response"]

    missing_top_level = validate_required_fields(actual, expected["required_fields"])

    analysis = actual.get("analysis", {})
    missing_analysis = validate_required_fields(
        analysis,
        expected["analysis_required_fields"]
    )

    status = "FAIL" if missing_top_level or missing_analysis else "PASS"

    report = {
        "scenario": case["scenario"],
        "status": status,
        "schema_mismatch": status == "FAIL",
        "missing_top_level_fields": missing_top_level,
        "missing_analysis_fields": missing_analysis,
        "expected_fields": expected,
        "regression_summary": (
            "API response contract changed: expected event_count and fingerprint fields are missing."
            if status == "FAIL"
            else "API response matches expected schema."
        )
    }

    REPORT.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))

    if status == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
