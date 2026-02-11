#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

python ae/tools/table3.py "$@" --repeats 50 --timeout 600
echo
echo "[Full] table3.csv saved at ae/results/table3.csv"