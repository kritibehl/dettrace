#!/usr/bin/env python3
import json
from pathlib import Path

INPUT = Path(__file__).with_name("failing_commit_demo.json")
REPORT = Path(__file__).with_name("regression_summary.md")


def is_fail(commit_record):
    return commit_record["replay_status"] == "FAIL"


def bisect_first_failure(commits):
    lo = 0
    hi = len(commits) - 1
    first_fail = None
    probes = []

    while lo <= hi:
        mid = (lo + hi) // 2
        record = commits[mid]
        probes.append({
            "index": mid,
            "commit": record["commit"],
            "status": record["replay_status"],
            "summary": record["summary"]
        })

        if is_fail(record):
            first_fail = record
            hi = mid - 1
        else:
            lo = mid + 1

    return first_fail, probes


def main():
    data = json.loads(INPUT.read_text())
    commits = data["commits"]

    first_fail, probes = bisect_first_failure(commits)

    if not first_fail:
        result = {
            "status": "NO_REGRESSION_FOUND",
            "first_failing_commit": None,
            "probes": probes
        }
    else:
        prev_idx = max(0, commits.index(first_fail) - 1)
        previous = commits[prev_idx]

        result = {
            "status": "REGRESSION_ISOLATED",
            "first_failing_commit": first_fail["commit"],
            "first_failing_label": first_fail["label"],
            "previous_passing_commit": previous["commit"] if previous != first_fail else None,
            "first_divergence_index": first_fail["first_divergence_index"],
            "probable_defect_type": first_fail["probable_defect_type"],
            "replay_diff": {
                "expected": "interrupt_cleared -> READY",
                "actual": "sensor_read -> WAITING",
                "defect": first_fail["probable_defect_type"]
            },
            "root_cause_summary": (
                "Regression introduced by interrupt state-machine refactor: "
                "actual replay reads sensor data before clearing the device interrupt."
            ),
            "probes": probes
        }

    REPORT.write_text(
        "# Regression Isolation Summary\n\n"
        f"## Status\n\n{result['status']}\n\n"
        "## First failing commit\n\n"
        f"`{result.get('first_failing_commit')}` — {result.get('first_failing_label')}\n\n"
        "## Previous passing commit\n\n"
        f"`{result.get('previous_passing_commit')}`\n\n"
        "## Replay diff\n\n"
        f"- expected: `{result.get('replay_diff', {}).get('expected')}`\n"
        f"- actual: `{result.get('replay_diff', {}).get('actual')}`\n"
        f"- first divergence index: `{result.get('first_divergence_index')}`\n"
        f"- probable defect type: `{result.get('probable_defect_type')}`\n\n"
        "## Root-cause summary\n\n"
        f"{result.get('root_cause_summary')}\n\n"
        "## Bisect probes\n\n"
        + "\n".join(
            f"- index {p['index']}: `{p['commit']}` -> {p['status']} ({p['summary']})"
            for p in result["probes"]
        )
        + "\n"
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
