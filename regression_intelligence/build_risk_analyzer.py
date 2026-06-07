#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

KNOWN = Path("regression_intelligence/known_regressions.json")
REPORT_JSON = Path("regression_intelligence/risk_report.json")
REPORT_MD = Path("regression_intelligence/risk_report.md")


def main():
    parser = argparse.ArgumentParser(description="Analyze regression risk from replay/build signals")
    parser.add_argument("--build", default="candidate_build")
    parser.add_argument("--signals", required=True, help="Comma-separated signals")
    args = parser.parse_args()

    signals = {s.strip() for s in args.signals.split(",") if s.strip()}
    known = json.loads(KNOWN.read_text())["known_regressions"]

    matches = []
    for reg in known:
        overlap = sorted(signals & set(reg["signals"]))
        if overlap:
            matches.append({
                "regression_id": reg["id"],
                "family": reg["family"],
                "risk": reg["risk"],
                "confidence": reg["confidence"],
                "matched_signals": overlap,
                "recommended_action": reg["recommended_action"]
            })

    risk_rank = {"low": 1, "medium": 2, "high": 3}
    highest = "low"
    if matches:
        highest = max((m["risk"] for m in matches), key=lambda r: risk_rank[r])

    report = {
        "build": args.build,
        "safe_claim": "heuristic regression-risk analysis for replay diagnostics; not production release automation",
        "known_regression_risk": highest,
        "matched_failures": matches,
        "release_recommendation": "hold" if highest == "high" else "review" if highest == "medium" else "proceed"
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))
    REPORT_MD.write_text(
        "# Regression Intelligence Report\n\n"
        f"- build: `{report['build']}`\n"
        f"- known regression risk: `{report['known_regression_risk']}`\n"
        f"- release recommendation: `{report['release_recommendation']}`\n\n"
        "## Matched failures\n\n" +
        "\n".join(
            f"- `{m['regression_id']}` family=`{m['family']}` risk=`{m['risk']}` confidence=`{m['confidence']}` signals=`{m['matched_signals']}` action={m['recommended_action']}"
            for m in matches
        ) + "\n"
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
