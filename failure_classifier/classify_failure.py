#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

REPORT_JSON = Path("failure_classifier/classification_report.json")
REPORT_MD = Path("failure_classifier/classification_report.md")


RULES = [
    ("retry_storm", ["retry_storm", "retry_send", "retry", "bounded_retry"], 0.92),
    ("timeout", ["timeout", "deadline_exceeded", "timed out"], 0.90),
    ("disconnect", ["disconnect", "reconnect"], 0.88),
    ("enumeration_failure", ["config_read_timeout", "missing_bar_assignment", "enumeration"], 0.91),
    ("state_corruption", ["stale_device_state", "stale_session", "state_corruption"], 0.87),
]


def load_json(path: Path):
    return json.loads(path.read_text())


def classify_text(text: str):
    lowered = text.lower()
    matches = []

    for family, keywords, confidence in RULES:
        hits = [kw for kw in keywords if kw in lowered]
        if hits:
            matches.append({
                "failure_family": family,
                "confidence": confidence,
                "matched_keywords": hits
            })

    if not matches:
        return {
            "failure_family": "unknown",
            "confidence": 0.0,
            "matched_keywords": []
        }

    matches.sort(key=lambda x: (x["confidence"], len(x["matched_keywords"])), reverse=True)
    return matches[0]


def main():
    parser = argparse.ArgumentParser(description="Classify DetTrace failure artifacts")
    parser.add_argument("artifact", help="Path to JSON replay artifact")
    args = parser.parse_args()

    path = Path(args.artifact)
    data = load_json(path)
    classification = classify_text(json.dumps(data))

    result = {
        "artifact": str(path),
        "safe_claim": "heuristic replay-failure classification for diagnostics; not trained ML",
        **classification
    }

    REPORT_JSON.write_text(json.dumps(result, indent=2))
    REPORT_MD.write_text(
        "# Failure Classification Report\n\n"
        "## Safe claim\n\n"
        f"{result['safe_claim']}\n\n"
        "## Result\n\n"
        f"- artifact: `{result['artifact']}`\n"
        f"- failure family: `{result['failure_family']}`\n"
        f"- confidence: `{result['confidence']}`\n"
        f"- matched keywords: `{result['matched_keywords']}`\n"
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
