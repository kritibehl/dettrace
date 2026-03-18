#!/usr/bin/env bash
set -euo pipefail
PORT="${1:-8000}"
echo "Serving DetTrace repo at http://localhost:${PORT}/viewer/index.html"
python3 -m http.server "${PORT}"
