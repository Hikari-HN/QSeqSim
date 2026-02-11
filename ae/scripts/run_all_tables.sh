#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

TABLE_SCRIPTS_DEFAULT=(
  "run_table1.sh"
  "run_table2a.sh"
  "run_table2b.sh"
  "run_table3.sh"
  "run_table4.sh"
  "run_table5.sh"
)

LOG_ROOT_DIR="${REPO_ROOT}/ae/results/logs"
LOG_DIR=""
CONTINUE_ON_FAIL=0
RETRY=0
ONLY=""
EXTRA_ARGS=()

usage() {
  cat <<'EOF'
Usage:
  ./ae/scripts/run_all_tables.sh [options] [-- extra_args_passed_to_subscripts]

Options:
  --log-root-dir PATH    Root directory to store logs (default: ae/results/logs)
  --log-dir PATH         Exact log directory to use (disables timestamp subdir)
  --continue-on-fail     Continue running remaining scripts after a failure
  --retry N              Retry a failed script N times (default: 0)
  --only LIST            Run only selected scripts (comma-separated).
                         Accepts: table1,table2a,... OR run_table1.sh,... (case-sensitive)
  -h, --help             Show this help message

Examples:
  ./ae/scripts/run_all_tables.sh
  ./ae/scripts/run_all_tables.sh --only table1,table3
  ./ae/scripts/run_all_tables.sh -- --smoke
EOF
}

ts() { date +"%Y-%m-%d %H:%M:%S"; }
run_id() { date +"%Y%m%d-%H%M%S"; }

normalize_only_item() {
  local x="${1// /}"
  if [[ "$x" =~ ^table ]]; then
    echo "run_${x}.sh"
  else
    echo "$x"
  fi
}

ensure_executable() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "[ERROR] Script not found: $path" >&2
    return 2
  fi
  if [[ ! -x "$path" ]]; then
    chmod +x "$path" 2>/dev/null || true
  fi
}

run_one() {
  local script_name="$1"
  local script_path="${SCRIPT_DIR}/${script_name}"
  ensure_executable "$script_path"

  mkdir -p "$LOG_DIR"
  local log_file="${LOG_DIR}/${script_name%.sh}.log"

  local attempt=0
  local max_attempt=$((RETRY + 1))

  while (( attempt < max_attempt )); do
    attempt=$((attempt + 1))

    echo "[$(ts)] >>> START ${script_name} (attempt ${attempt}/${max_attempt})"
    echo "[$(ts)] >>> LOG   ${log_file}"
    echo "[$(ts)] >>> AE_LOG_DIR=${LOG_DIR}"

    (
      cd "$REPO_ROOT"
      export AE_LOG_DIR="$LOG_DIR"
      bash "$script_path" ${EXTRA_ARGS[@]:-}
    ) 2>&1 | tee -a "$log_file"
    local rc="${PIPESTATUS[0]}"

    if [[ "$rc" -eq 0 ]]; then
      echo "[$(ts)] <<< OK    ${script_name}"
      return 0
    fi

    echo "[$(ts)] <<< FAIL  ${script_name} (rc=${rc})" >&2
    if (( attempt < max_attempt )); then
      echo "[$(ts)] ... RETRY ${script_name} after 1s" >&2
      sleep 1
    else
      return "$rc"
    fi
  done

  return 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --log-root-dir) LOG_ROOT_DIR="$2"; shift 2;;
    --log-dir) LOG_DIR="$2"; shift 2;;
    --continue-on-fail) CONTINUE_ON_FAIL=1; shift;;
    --retry) RETRY="$2"; shift 2;;
    --only) ONLY="$2"; shift 2;;
    --)
      shift
      EXTRA_ARGS=("$@")
      break
      ;;
    -h|--help) usage; exit 0;;
    *)
      echo "[ERROR] Unknown arg: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$LOG_DIR" ]]; then
  LOG_DIR="${LOG_ROOT_DIR}/$(run_id)"
else
  # Make relative log-dir relative to repo root for consistency.
  if [[ "${LOG_DIR:0:1}" != "/" ]]; then
    LOG_DIR="${REPO_ROOT}/${LOG_DIR}"
  fi
fi

SCRIPTS=("${TABLE_SCRIPTS_DEFAULT[@]}")
if [[ -n "$ONLY" ]]; then
  IFS=',' read -r -a only_items <<< "$ONLY"
  SCRIPTS=()
  for item in "${only_items[@]}"; do
    SCRIPTS+=("$(normalize_only_item "$item")")
  done
fi

echo "Repo root       : ${REPO_ROOT}"
echo "Script dir      : ${SCRIPT_DIR}"
echo "Log root dir    : ${LOG_ROOT_DIR}"
echo "Log dir         : ${LOG_DIR}"
echo "Scripts         : ${SCRIPTS[*]}"
echo "Retry           : ${RETRY}"
echo "Continue on fail: ${CONTINUE_ON_FAIL}"
if ((${#EXTRA_ARGS[@]} > 0)); then
  echo "Extra args      : ${EXTRA_ARGS[*]}"
fi
echo

FAILED=()
for s in "${SCRIPTS[@]}"; do
  if run_one "$s"; then
    :
  else
    FAILED+=("$s")
    if (( CONTINUE_ON_FAIL == 0 )); then
      echo "[ERROR] Stopping due to failure: $s" >&2
      echo "[INFO] Logs are available at: ${LOG_DIR}" >&2
      exit 1
    fi
  fi
done

echo
echo "========== SUMMARY =========="
if ((${#FAILED[@]} == 0)); then
  echo "All table scripts succeeded."
  echo "Logs are available at: ${LOG_DIR}"
  exit 0
else
  echo "Failed scripts:"
  for s in "${FAILED[@]}"; do
    echo "  - $s"
  done
  echo "Logs are available at: ${LOG_DIR}"
  exit 1
fi