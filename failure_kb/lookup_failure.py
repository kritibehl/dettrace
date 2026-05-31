#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

CATALOG = Path("failure_kb/failure_catalog.json")
REPORT_JSON = Path("failure_kb/knowledge_base_report.json")
REPORT_MD = Path("failure_kb/knowledge_base_report.md")


ALIASES = {
    "retry": "retry_storm",
    "retry_storm": "retry_storm",
    "timeout": "timeout",
    "disconnect": "disconnect",
    "reconnect": "disconnect",
    "enumeration": "enumeration_failure",
    "enumeration_failure": "enumeration_failure",
    "state": "state_corruption",
    "state_corruption": "state_corruption",
    "calibration": "calibration_drift",
    "calibration_drift": "calibration_drift"
}


def resolve_family(raw):
    key = raw.strip().lower().replace("-", "_")
    return ALIASES.get(key, key)


def main():
    parser = argparse.ArgumentParser(description="Lookup DetTrace diagnostics knowledge base")
    parser.add_argument("--family", required=True, help="Failure family, e.g. retry_storm, timeout, disconnect")
    args = parser.parse_args()

    catalog = json.loads(CATALOG.read_text())
    family = resolve_family(args.family)
    entry = catalog["failure_families"].get(family)

    if not entry:
        result = {
            "failure_family": family,
            "found": False,
            "safe_claim": catalog["safe_claim"],
            "similar_failures": [],
            "likely_root_causes": [],
            "recommended_actions": []
        }
    else:
        result = {
            "failure_family": family,
            "found": True,
            "safe_claim": catalog["safe_claim"],
            **entry
        }

    REPORT_JSON.write_text(json.dumps(result, indent=2))
    REPORT_MD.write_text(
        "# Failure Knowledge Base Report\n\n"
        "## Safe claim\n\n"
        f"{result['safe_claim']}\n\n"
        "## Lookup result\n\n"
        f"- failure family: `{result['failure_family']}`\n"
        f"- found: `{result['found']}`\n\n"
        "## Similar failures\n\n"
        + "\n".join(f"- `{x}`" for x in result["similar_failures"])
        + "\n\n## Likely root causes\n\n"
        + "\n".join(f"- `{x}`" for x in result["likely_root_causes"])
        + "\n\n## Recommended actions\n\n"
        + "\n".join(f"- {x}" for x in result["recommended_actions"])
        + "\n"
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
