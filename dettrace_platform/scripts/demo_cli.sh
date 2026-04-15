#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate

python -m app.cli.main replay case_studies/race_condition_bug.json
echo ""
python -m app.cli.main fingerprint case_studies/retry_storm_meltdown.json
echo ""
