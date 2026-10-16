import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "artifacts/traces/baseline/checkout.json"
CANDIDATE = ROOT / "artifacts/traces/candidate/checkout.json"


def _run(tmp_path, *extra):
    dest = tmp_path / "report.json"
    proc = subprocess.run(
        [sys.executable, "-m", "trace_regression.cli",
         "--baseline", str(BASELINE), "--candidate", str(CANDIDATE),
         "--output", str(dest), *extra],
        cwd=ROOT, capture_output=True, text=True,
    )
    return proc, json.loads(dest.read_text()) if dest.exists() else None


def test_bootstrap_cli_on_checked_in_trace_fixture(tmp_path):
    result, report = _run(tmp_path, "--latency-evidence", "bootstrap", "--bootstrap-iterations", "200")
    assert result.returncode == 1, result.stderr
    assert report["decision"] == "FAIL"
    assert report["latency_evidence_mode"] == "bootstrap"
    checkout = next(c for c in report["cohorts"] if c["shape"]["route"] == "/checkout")
    assert checkout["latency_evidence"]["confirmed_regressions"] >= 1
    health = next(c for c in report["cohorts"] if c["shape"]["route"] == "/health")
    assert health["decision"] == "INCONCLUSIVE"


def test_legacy_cli_default_regression_unchanged(tmp_path):
    result, report = _run(tmp_path)
    assert result.returncode == 1, result.stderr
    assert report["latency_evidence_mode"] == "point-estimate"
    assert report["decision"] == "FAIL"
    assert all("latency_evidence" not in c for c in report["cohorts"])


def test_bootstrap_bad_settings_exit_without_report(tmp_path):
    result, report = _run(tmp_path, "--latency-evidence", "bootstrap", "--bootstrap-iterations", "10")
    assert result.returncode == 2
    assert "bootstrap iterations" in result.stderr
    assert report is None


def test_zero_baseline_report_has_no_nonstandard_infinity(tmp_path):
    from trace_regression.cli import _json_safe
    assert json.dumps(_json_safe({"delta_pct": float("inf")}), allow_nan=False) == '{"delta_pct": null}'
    assert _json_safe([float("nan"), {"x": float("-inf")}]) == [None, {"x": None}]


def test_bootstrap_cli_renders_evidence(tmp_path):
    result, report = _run(tmp_path, "--latency-evidence", "bootstrap", "--bootstrap-iterations", "200")
    assert result.returncode == 1
    assert "BOOTSTRAP LATENCY EVIDENCE" in result.stdout
    assert "confirmed:" in result.stdout
