#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

REPORT = Path("git_bisect_tools/git_bisect_summary.json")


def run(cmd):
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.returncode, p.stdout.strip()


def main():
    code, log = run(["git", "log", "--oneline", "-n", "12"])
    commits = []
    for line in log.splitlines():
        if not line.strip():
            continue
        sha, *msg = line.split(" ", 1)
        commits.append({
            "commit": sha,
            "message": msg[0] if msg else "",
            "simulated_replay_status": "FAIL" if "device" in line.lower() or "replay" in line.lower() else "PASS"
        })

    first_fail = next((c for c in commits if c["simulated_replay_status"] == "FAIL"), None)

    result = {
        "mode": "actual_git_history_scan",
        "commit_count_scanned": len(commits),
        "first_matching_replay_failure_commit": first_fail,
        "note": "This scans real Git commits and marks replay/device commits as simulated failure candidates for bisection workflow demonstration."
    }

    REPORT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
