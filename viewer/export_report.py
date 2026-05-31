#!/usr/bin/env python3
from pathlib import Path
import json

SOURCE = Path("io_transport_validation/transport_validation_report.json")
OUT = Path("viewer/exported_diagnostics_report.md")

data = json.loads(SOURCE.read_text())

lines = [
    "# Exported Diagnostics Report",
    "",
    "## Summary",
    "",
    f"- workflow: `{data['workflow']}`",
    f"- trace count: `{data['trace_count']}`",
    f"- validation pass count: `{data['validation_pass_count']}`",
    f"- validation fail count: `{data['validation_fail_count']}`",
    "",
    "## Replay results",
    ""
]

for r in data["results"]:
    lines.extend([
        f"### {r['scenario']}",
        "",
        f"- first divergence index: `{r['first_divergence_index']}`",
        f"- expected event: `{r['expected_event']}`",
        f"- actual event: `{r['actual_event']}`",
        f"- computed status: `{r['computed_status']}`",
        f"- validation passed: `{r['validation_passed']}`",
        f"- reason: {r['reason']}",
        ""
    ])

OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
