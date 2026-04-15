#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt

python3 scripts/seed_case_studies.py

uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
