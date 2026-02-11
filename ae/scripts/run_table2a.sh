#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

python ae/tools/table2a.py "$@"
