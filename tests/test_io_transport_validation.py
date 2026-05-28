import json
import subprocess
from pathlib import Path


def test_io_transport_replay_workflow_runs():
    result = subprocess.run(
        ["python3", "io_transport_validation/run_transport_replay.py"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    report = json.loads(Path("io_transport_validation/transport_validation_report.json").read_text())

    assert report["trace_count"] == 5
    assert report["validation_pass_count"] == 5
    assert report["validation_fail_count"] == 0

    scenarios = {r["scenario"]: r for r in report["results"]}

    assert scenarios["usb-reconnect-recovery"]["computed_status"] == "PASS"
    assert scenarios["pcie-style-enumeration-failure"]["computed_status"] == "FAIL"
    assert scenarios["displayport-style-link-training-recovery"]["computed_status"] == "PASS"
    assert scenarios["accessory-disconnect-recovery"]["computed_status"] == "PASS"
    assert scenarios["transport-timeout-retry-chain"]["computed_status"] == "PASS"

    assert scenarios["pcie-style-enumeration-failure"]["first_divergence_index"] == 1
    assert scenarios["displayport-style-link-training-recovery"]["first_divergence_index"] == 2
