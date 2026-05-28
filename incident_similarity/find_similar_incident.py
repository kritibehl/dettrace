#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

CORPUS = Path("failure_library/io_failure_corpus.json")
REPORT_JSON = Path("incident_similarity/similarity_report.json")
REPORT_MD = Path("incident_similarity/similarity_report.md")


def tokens_from_obj(obj):
    text = json.dumps(obj).lower()
    for ch in '",:{}[]()->_/':
        text = text.replace(ch, " ")
    return {t for t in text.split() if len(t) > 2}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    parser = argparse.ArgumentParser(description="Find similar replay incident")
    parser.add_argument("incident", help="Path to JSON incident artifact")
    args = parser.parse_args()

    incident_path = Path(args.incident)
    incident = json.loads(incident_path.read_text())
    incident_tokens = tokens_from_obj(incident)

    corpus = json.loads(CORPUS.read_text())["scenarios"]

    scored = []
    for item in corpus:
        score = jaccard(incident_tokens, tokens_from_obj(item))
        scored.append({
            "scenario_id": item["id"],
            "family": item["family"],
            "expected_event": item["expected_event"],
            "actual_event": item["actual_event"],
            "expected_status": item["expected_status"],
            "similarity": round(score, 2)
        })

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    best = scored[0]

    report = {
        "new_incident": str(incident_path),
        "safe_claim": "token-based replay incident similarity for diagnostics; not ML ranking",
        "most_similar_replay": best,
        "top_5": scored[:5]
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))
    REPORT_MD.write_text(
        "# Incident Similarity Report\n\n"
        "## Safe claim\n\n"
        f"{report['safe_claim']}\n\n"
        "## Most similar replay\n\n"
        f"- scenario id: `{best['scenario_id']}`\n"
        f"- family: `{best['family']}`\n"
        f"- expected event: `{best['expected_event']}`\n"
        f"- actual event: `{best['actual_event']}`\n"
        f"- similarity: `{best['similarity']}`\n\n"
        "## Top 5\n\n"
        + "\n".join(
            f"- `{x['scenario_id']}` family=`{x['family']}` similarity=`{x['similarity']}`"
            for x in scored[:5]
        )
        + "\n"
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
