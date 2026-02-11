import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
QRW = PROJECT_ROOT / "exp" / "simulation" / "qrw.py"
QRW_DATA_LOG_DIR = PROJECT_ROOT / "exp" / "simulation" / "data"

REPORT_RE = re.compile(rf"{re.escape('[REPORT]')}\s+n=(\d+)\s+iter=(\d+)\s+time=([\d\.]+)")

# Full (paper-like) Table 2a configs
QRW_CONFIGS_FULL = {
    16: {"gates": 31, "iters": [3, 10, 100, 200, 785]},
    128: {"gates": 255, "iters": [3, 10, 100, 200, 244]},
    1024: {"gates": 2047, "iters": [3, 5, 8, 10, 13]},
}

# Smoke configs: fast, stable, still representative
QRW_CONFIGS_SMOKE = {
    16: {"gates": 31, "iters": [3, 10]},
}


def get_log_dir(out_dir: Path) -> Path:
    """
    Prefer a shared run directory if AE_LOG_DIR is set by the runner.
    Fallback to ae/results/logs for standalone runs.
    """
    d = os.environ.get("AE_LOG_DIR", "").strip()
    if d:
        p = Path(d)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        p.mkdir(parents=True, exist_ok=True)
        return p
    p = out_dir / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def classify_status(returncode: int, output: str) -> str:
    out = (output or "").lower()
    timeout_markers = [
        "status: timeout",
        "timeout",
        "timed out",
        "time limit exceeded",
        "deadline exceeded",
        "terminated due to timeout",
        "sigkill",
        "signal: 9",
    ]
    if any(m in out for m in timeout_markers):
        return "timeout"
    if returncode == 0:
        return "success"
    return "error"


def run_and_collect(script: Path, n: int, report_iters: list[int], timeout_s: int):
    max_iters = max(report_iters)
    arg_report = ",".join(str(x) for x in report_iters)

    cmd = [
        sys.executable,
        str(script),
        "--n",
        str(n),
        "--max-iters",
        str(max_iters),
        "--report-iters",
        arg_report,
        "--timeout",
        str(timeout_s),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stdout or "") + "\n" + (p.stderr or "")

    seen: dict[int, float] = {}
    for m in REPORT_RE.finditer(out):
        nn = int(m.group(1))
        it = int(m.group(2))
        t = float(m.group(3))
        if nn == n:
            seen[it] = t

    status = classify_status(p.returncode, out)
    return status, seen, out, cmd


def archive_data_log(src: Path, dst: Path) -> bool:
    """
    Archive per-iteration log from exp/simulation/data into the AE run log dir.
    Prefer hard-link (O(1)); fallback to copy2 across filesystems.
    """
    if not src.exists():
        return False

    dst.parent.mkdir(parents=True, exist_ok=True)

    try:
        if dst.exists():
            dst.unlink()
    except OSError:
        pass

    try:
        os.link(src, dst)
        return True
    except OSError:
        shutil.copy2(src, dst)
        return True


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="Run a fast subset but still generate table2a.csv")
    ap.add_argument("--timeout", type=int, default=None, help="Override timeout seconds per run")
    args = ap.parse_args()

    out_dir = PROJECT_ROOT / "ae" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = get_log_dir(out_dir)

    cfgs = QRW_CONFIGS_SMOKE if args.smoke else QRW_CONFIGS_FULL
    timeout_s = args.timeout if args.timeout is not None else (300 if args.smoke else 1800)

    rows = []
    for n, cfg in cfgs.items():
        iters = cfg["iters"]
        gates = cfg["gates"]
        print(f"[Table2a] QRW n={n} report={iters} timeout={timeout_s}s", flush=True)

        run_status, seen, out, cmd = run_and_collect(QRW, n, iters, timeout_s=timeout_s)
        need_debug = (run_status != "success") or any(it not in seen for it in iters)

        if need_debug:
            # Subprocess stdout/stderr snapshot
            (log_dir / f"table2a_qrw_n{n}.txt").write_text(
                "CMD: " + " ".join(map(str, cmd)) + "\n\n" + out,
                encoding="utf-8",
            )

            # Per-iteration log produced by qrw.py itself
            src = QRW_DATA_LOG_DIR / f"qrw_{n}.log"
            dst = log_dir / f"table2a_qrw_n{n}_per_iter.log"
            if not archive_data_log(src, dst):
                print(f"[Table2a][WARN] per-iter log not found: {src}")

        for it in iters:
            has = it in seen
            if has:
                time_val = seen[it]
                row_status = "success"
            else:
                time_val = "timeout" if run_status == "timeout" else ""
                row_status = f"{run_status}_missing_iter"

            rows.append(
                {
                    "benchmark": "QRW",
                    "qubits": n,
                    "gates_per_iteration": gates,
                    "iterations": it,
                    "time_seconds": time_val,
                    "status": row_status,
                }
            )

    write_csv(out_dir / "table2a.csv", rows)
    print(f"\n[Table2a] Saved: {out_dir / 'table2a.csv'}")


if __name__ == "__main__":
    main()