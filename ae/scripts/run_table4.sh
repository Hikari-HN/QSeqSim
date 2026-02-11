#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

python ae/tools/table4.py "$@"
echo
echo "[Table4] Preview:"
head -n 20 ae/results/table4.csv || true
