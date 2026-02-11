#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

python ae/tools/table5.py "$@"
echo
echo "[Table5] Preview:"
head -n 20 ae/results/table5.csv || true
