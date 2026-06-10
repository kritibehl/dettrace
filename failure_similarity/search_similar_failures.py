#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

PATTERNS = Path("failure_similarity/failure_patterns.json")
REPORT_JSON = Path("failure_similarity/failure_similarity_report.json")
REPORT_MD = Path("failure_similarity/failure_similarity_report.md")


def text_for(path):
    return Path(path).read_text().lower()


def score_pattern(trace_text, pattern):
    hits = [signal for signal in pattern["signals"] if signal.lower() in trace_text]
    score = round(len(hits) / len(pattern["signals"]), 2)
    confidence = round(min(0.99, 0.60 + score * 0.35), 2) if hits else 0.0
    return {
        "pattern_id": pattern["id"],
        "failure_family": pattern["family"],
        "similarity": score,
        "confidence": confidence,
        "matched_evidence": hits,
        "likely_root_cause": pattern["likely_root_cause"]
    }


def main():
    parser = argparse.ArgumentParser(description="Search similar DetTrace replay failure patterns")
    parser.add_argument("trace", help="Path to trace or replay artifact")
    args = parser.parse_args()

    trace_text = text_for(args.trace)
    patterns = json.loads(PATTERNS.read_text())["patterns"]

    matches = [score_pattern(trace_text, p) for p in patterns]
    matches = [m for m in matches if m["similarity"] > 0]
    matches.sort(key=lambda m: (m["confidence"], m["similarity"], len(m["matched_evidence"])), reverse=True)

    best = matches[0] if matches else {
        "pattern_id": "none",
        "failure_family": "unknown",
        "similarity": 0.0,
        "confidence": 0.0,
        "matched_evidence": [],
        "likely_root_cause": "unknown"
    }

    report = {
        "input_trace": args.trace,
        "safe_claim": "heuristic replay failure-similarity search; not ML or production incident ranking",
        "most_similar_failure": best,
        "top_matches": matches[:5]
    }

    REPORT_JSON.write_text(json.dumps(report, indent=2))
    REPORT_MD.write_text(
        "# Failure Similarity Search Report\n\n"
        "## Safe claim\n\n"
        f"{report['safe_claim']}\n\n"
        "## Most similar failure\n\n"
        f"- family: `{best['failure_family']}`\n"
        f"- similarity: `{best['similarity']}`\n"
        f"- confidence: `{best['confidence']}`\n"
        f"- likely root cause: `{best['likely_root_cause']}`\n"
        f"- evidence: `{best['matched_evidence']}`\n\n"
        "## Top matches\n\n"
        + "\n".join(
            f"- `{m['failure_family']}` similarity=`{m['similarity']}` confidence=`{m['confidence']}` evidence=`{m['matched_evidence']}` root_cause=`{m['likely_root_cause']}`"
            for m in report["top_matches"]
        )
        + "\n"
    )

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
