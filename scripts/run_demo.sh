#!/usr/bin/env bash

set -e

echo "=== DetTrace Demo: Deterministic Replay ==="

# build C++ core
mkdir -p build
cd build
cmake ..
make -j
cd ..

# run simulation
./build/dettrace

echo ""
echo "Artifacts generated:"
ls -lh artifacts || true

echo ""
echo "Sample divergence:"
cat artifacts/divergence_report.json || true
