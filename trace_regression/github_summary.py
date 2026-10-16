from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _shape_label(cohort: dict[str, Any]) -> str:
    shape = cohort.get("shape", {})

    method = shape.get("method") or "-"
    route = shape.get("route") or "-"
    root = shape.get("root") or "-"

    if route != "-":
        return f"{method} {route}"

    return str(root)


def render_summary(
    report: dict[str, Any],
) -> str:
    decision = report.get(
        "decision",
        "UNKNOWN",
    )

    lines = [
        "## DetTrace Trace Regression Gate",
        "",
        f"**Decision:** `{decision}`",
        "",
        (
            f"Baseline traces: "
            f"**{report.get('baseline_trace_count', 0)}**  "
        ),
        (
            f"Candidate traces: "
            f"**{report.get('candidate_trace_count', 0)}**  "
        ),
        (
            f"Matched request shapes: "
            f"**{report.get('matched_shape_count', 0)}**"
        ),
        "",
        "| Request shape | Baseline | Candidate | Decision |",
        "|---|---:|---:|:---:|",
    ]

    cohorts = report.get(
        "cohorts",
        [],
    )

    for cohort in cohorts:
        label = _shape_label(
            cohort
        )

        lines.append(
            "| "
            f"{label} | "
            f"{cohort.get('baseline_trace_count', 0)} | "
            f"{cohort.get('candidate_trace_count', 0)} | "
            f"**{cohort.get('decision', 'UNKNOWN')}** |"
        )

    if report.get("latency_evidence_mode") == "bootstrap":
        lines.extend([
            "",
            "### Opt-in bootstrap latency evidence",
            "",
            "Observed crossings require an adjusted one-sided bootstrap lower "
            "bound above the latency threshold. `INCONCLUSIVE` is not PASS.",
        ])
        for cohort in cohorts:
            evidence = cohort.get("latency_evidence")
            if not evidence:
                continue
            label = _shape_label(cohort)
            lines.append(
                f"- **{label}**: {evidence.get('confirmed_regressions', 0)} "
                "confirmed, "
                f"{evidence.get('inconclusive_regressions', 0)} inconclusive "
                "point-estimate crossings"
            )
            for item in evidence.get("assessments", []):
                key = item.get("semantic_key", ["-", "-"])
                lower = item.get("lower_bound_delta_pct")
                lower_label = "unavailable" if lower is None else f"{lower:.2f}%"
                lines.append(
                    f"  - `{key[1] if len(key) > 1 else key[0]}`: "
                    f"{item.get('status', 'UNKNOWN')} "
                    f"(lower bound {lower_label}; {item.get('reason', '-')})"
                )

    failed = [
        cohort
        for cohort in cohorts
        if cohort.get("decision") == "FAIL"
    ]

    if failed:
        lines.extend(
            [
                "",
                "### Failed request shapes",
            ]
        )

    for cohort in failed:
        label = _shape_label(
            cohort
        )

        regressions = cohort.get(
            "regressions",
            [],
        )

        errors = cohort.get(
            "error_regressions",
            [],
        )

        additions = cohort.get(
            "added_spans",
            [],
        )

        lines.extend(
            [
                "",
                f"#### `{label}`",
                "",
                (
                    f"- latency regressions: "
                    f"**{len(regressions)}**"
                ),
                (
                    f"- error-rate regressions: "
                    f"**{len(errors)}**"
                ),
                (
                    f"- structural additions: "
                    f"**{len(additions)}**"
                ),
            ]
        )

        if additions:
            lines.append(
                "- new spans:"
            )

            for item in additions:
                service = item.get(
                    "service",
                    "-",
                )
                span = item.get(
                    "span",
                    "-",
                )
                parent = item.get(
                    "parent",
                    "-",
                )

                lines.append(
                    "  - "
                    f"`{parent} -> {span}` "
                    f"(`service={service}`)"
                )

        if errors:
            lines.append(
                "- error regressions:"
            )

            for item in errors:
                service = item.get(
                    "service",
                    "-",
                )
                span = item.get(
                    "span",
                    "-",
                )
                baseline_rate = (
                    100
                    * item.get(
                        "baseline_error_rate",
                        0.0,
                    )
                )
                candidate_rate = (
                    100
                    * item.get(
                        "candidate_error_rate",
                        0.0,
                    )
                )

                lines.append(
                    "  - "
                    f"`{service}.{span}`: "
                    f"{baseline_rate:.1f}% "
                    f"-> {candidate_rate:.1f}%"
                )

    lines.extend(
        [
            "",
            "---",
            "",
            (
                "Generated by DetTrace from the "
                "trace-regression JSON report."
            ),
        ]
    )

    return "\n".join(
        lines
    )


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--report",
        required=True,
    )

    args = parser.parse_args()

    report = json.loads(
        Path(
            args.report
        ).read_text()
    )

    print(
        render_summary(
            report
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
