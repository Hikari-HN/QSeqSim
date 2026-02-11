#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

echo "[Smoke] Starting smoke test: Table1 + Table2a + Table2b + Table3 + Table4 + Table5"
echo "[Smoke] Using run_all_tables.sh to ensure a single shared timestamped log directory"
echo

bash "${SCRIPT_DIR}/run_all_tables.sh" \
  --only table1,table2a,table2b,table3,table4,table5 \
  -- --smoke