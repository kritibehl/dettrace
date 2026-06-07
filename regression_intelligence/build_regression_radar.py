#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

KNOWN = Path("regression_intelligence/known_regressions.json")
HISTORY = Path("regression_intelligence/regression_history.json")
REPORT_JSON = Path("regression_intelligence/regression_radar_report.json")
SCORECARD_MD = Path("regression_intelligence/build_scorecard.md")

RISK_WEIGHTS = {
    "low": 25,
    "medium": 55,
    "high": 85
}


def load_json(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description="Build Regression Radar for DetTrace replay diagnostics")
    parser.add_argument("--build", default="candidate_42")
    parser.add_argument("--signals", required=True, help="Comma-separated replay/build signals")
    args = parser.parse_args()

    signals = {s.strip() for s in args.signals.split(",") if s.strip()}
    known = load_json(KNOWN)["known_regressions"]
    history = load_json(HISTORY)["build_history"]

    matched = []
    for reg in known:
        overlap = sorted(signals & set(reg["signals"]))
        if overlap:
            matched.append({
                "regression_id": reg["id"],
                "family": reg["family"],
                "risk": reg["risk"],
                "confidence": reg["confidence"],
                "matched_signals": overlap,
                "recommended_action": reg["recommended_action"]
            })

    historical_occurrences = sum(item["matched_failures"] for item in history)
    max_risk_score = max([RISK_WEIGHTS[m["risk"]] for m in matched], default=15)
    confidence_boost = int(max([m["confidence"] for m in matched], default=0.0) * 10)
    match_boost = min(len(matched) * 4, 12)

    risk_score = min(100, max_risk_score + confidence_boost + match_boost)

    if risk_score >= 80:
        risk_level = "high"
        release_recommendation = "hold"
    elif risk_score >= 50:
        risk_level = "medium"
        release_recommendation = "review"
    else:
        risk_level = "low"
        release_recommendation = "proceed"

    report = {
        "candidate_build": args.build,
        "safe_claim": "heuristic replay-based build regression radar; not production release automation",
        "input_signals": sorted(signals),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "matched_regressions": len(matched),
        "historical_occurrences": historical_occurrences,
        "release_recommendation": release_recommendation,
        "matched_failures": matched
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))

    SCORECARD_MD.write_text(
        "# Build Regression Radar Scorecard\n\n"
        "## Safe claim\n\n"
        f"{report['safe_claim']}\n\n"
        "## Candidate build\n\n"
        f"- build: `{report['candidate_build']}`\n"
        f"- risk score: `{report['risk_score']}`\n"
        f"- risk level: `{report['risk_level']}`\n"
        f"- matched regressions: `{report['matched_regressions']}`\n"
        f"- historical occurrences: `{report['historical_occurrences']}`\n"
        f"- release recommendation: `{report['release_recommendation']}`\n\n"
        "## Matched failures\n\n"
        + "\n".join(
            f"- `{m['regression_id']}` family=`{m['family']}` risk=`{m['risk']}` "
            f"confidence=`{m['confidence']}` signals=`{m['matched_signals']}` action={m['recommended_action']}"
            for m in matched
        )
        + "\n"
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
