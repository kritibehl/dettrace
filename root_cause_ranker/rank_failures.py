#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

SIGNATURES = Path("root_cause_ranker/failure_signatures.json")
REPORT_JSON = Path("root_cause_ranker/root_cause_reports/root_cause_report.json")
REPORT_MD = Path("root_cause_ranker/root_cause_reports/root_cause_report.md")


def tokenize(obj):
    text = json.dumps(obj).lower()
    for ch in '{}[]":,/_-':
        text = text.replace(ch, " ")
    return set(t for t in text.split() if len(t) > 2)


def main():
    parser = argparse.ArgumentParser(description="Rank likely root causes for replay artifacts")
    parser.add_argument("artifact", help="Path to JSON replay artifact")
    args = parser.parse_args()

    artifact_path = Path(args.artifact)
    artifact = json.loads(artifact_path.read_text())
    tokens = tokenize(artifact)

    signatures = json.loads(SIGNATURES.read_text())["signatures"]

    ranked = []
    for sig in signatures:
        hits = [kw for kw in sig["keywords"] if kw.lower() in tokens or kw.lower() in json.dumps(artifact).lower()]
        if hits:
            ranked.append({
                "likely_cause": sig["cause"],
                "confidence": sig["confidence"],
                "evidence": hits
            })

    ranked.sort(key=lambda x: (x["confidence"], len(x["evidence"])), reverse=True)

    best = ranked[0] if ranked else {
        "likely_cause": "unknown",
        "confidence": 0.0,
        "evidence": []
    }

    report = {
        "incident": artifact_path.stem,
        "artifact": str(artifact_path),
        "safe_claim": "heuristic root-cause ranking for replay diagnostics; not trained ML or production incident ranking",
        "likely_cause": best["likely_cause"],
        "confidence": best["confidence"],
        "evidence": best["evidence"],
        "ranked_candidates": ranked[:5]
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))
    REPORT_MD.write_text(
        "# Root-Cause Ranking Report\n\n"
        "## Safe claim\n\n"
        f"{report['safe_claim']}\n\n"
        "## Result\n\n"
        f"- incident: `{report['incident']}`\n"
        f"- artifact: `{report['artifact']}`\n"
        f"- likely cause: `{report['likely_cause']}`\n"
        f"- confidence: `{report['confidence']}`\n"
        f"- evidence: `{report['evidence']}`\n\n"
        "## Ranked candidates\n\n"
        + "\n".join(
            f"- `{item['likely_cause']}` confidence=`{item['confidence']}` evidence=`{item['evidence']}`"
            for item in report["ranked_candidates"]
        )
        + "\n"
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
