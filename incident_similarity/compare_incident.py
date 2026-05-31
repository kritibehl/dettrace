#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

CORPUS = Path("failure_library/io_failure_corpus.json")
INDEX = Path("incident_similarity/similarity_index.json")
REPORT_JSON = Path("incident_similarity/enhanced_similarity_report.json")
REPORT_MD = Path("incident_similarity/enhanced_similarity_report.md")


def tokens(obj):
    text = json.dumps(obj).lower()
    for ch in '{}[]":,/_-':
        text = text.replace(ch, " ")
    return set(t for t in text.split() if len(t) > 2)


def jaccard(a, b):
    return round(len(a & b) / len(a | b), 2) if a and b else 0.0


def main():
    parser = argparse.ArgumentParser(description="Compare new incident against replay corpus")
    parser.add_argument("incident")
    args = parser.parse_args()

    incident_path = Path(args.incident)
    incident = json.loads(incident_path.read_text())
    incident_tokens = tokens(incident)

    corpus = json.loads(CORPUS.read_text())["scenarios"]

    index = []
    for item in corpus:
        score = jaccard(incident_tokens, tokens(item))
        shared = sorted(list(incident_tokens & tokens(item)))[:10]
        index.append({
            "scenario_id": item["id"],
            "family": item["family"],
            "expected_event": item["expected_event"],
            "actual_event": item["actual_event"],
            "expected_status": item["expected_status"],
            "similarity": score,
            "shared_evidence": shared
        })

    index.sort(key=lambda x: x["similarity"], reverse=True)
    INDEX.write_text(json.dumps(index, indent=2))

    best = index[0]
    report = {
        "incident": str(incident_path),
        "safe_claim": "token-based incident similarity for replay diagnostics; not ML ranking",
        "most_similar_replay": best,
        "top_5": index[:5]
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))
    REPORT_MD.write_text(
        "# Enhanced Incident Similarity Report\n\n"
        "## Safe claim\n\n"
        f"{report['safe_claim']}\n\n"
        "## Most similar replay\n\n"
        f"- scenario id: `{best['scenario_id']}`\n"
        f"- family: `{best['family']}`\n"
        f"- similarity: `{best['similarity']}`\n"
        f"- shared evidence: `{best['shared_evidence']}`\n\n"
        "## Top 5\n\n"
        + "\n".join(
            f"- `{x['scenario_id']}` family=`{x['family']}` similarity=`{x['similarity']}` evidence=`{x['shared_evidence']}`"
            for x in report["top_5"]
        )
        + "\n"
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
