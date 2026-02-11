import argparse
import csv
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXP_ENGINE = PROJECT_ROOT / "exp" / "simulation" / "exp_engine.py"

TOTAL_RUNTIME_RE = re.compile(r"Total Runtime\s*:\s*([\d\.]+)\s*s", re.IGNORECASE)

# Table 1 metadata (from the paper). Time is measured by exp_engine.
RUS_CASES = [
    # (benchmark_name, exp_rel_path, qubits, gates_per_iter)
    ("RUS-1", "rus/rus_1", 2, 7),
    ("RUS-2", "rus/rus_2", 2, 13),
    ("RUS-3", "rus/rus_3", 2, 12),
    ("RUS-4", "rus/rus_4", 2, 20),
    ("RUS-5", "rus/rus_5", 2, 37),
    ("RUS-6", "rus/rus_6", 2, 33),
]

ITER_LIST = [10, 100]


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


def run_one(exp_rel_path: str, iter_time: int) -> tuple[float, str, list[str]]:
    env = os.environ.copy()
    env["ITER_TIME"] = str(iter_time)

    cmd = [sys.executable, str(EXP_ENGINE), exp_rel_path]
    p = subprocess.run(
        cmd,
        cwd=str(EXP_ENGINE.parent),
        env=env,
        capture_output=True,
        text=True,
    )

    out = (p.stdout or "") + "\n" + (p.stderr or "")
    returncode = p.returncode

    if returncode != 0:
        raise RuntimeError(
            f"Experiment failed: {exp_rel_path} ITER_TIME={iter_time}\n\n"
            f"CMD: {' '.join(map(str, cmd))}\n\n{out}"
        )

    m = TOTAL_RUNTIME_RE.search(out)
    if not m:
        raise RuntimeError(
            f"Cannot parse Total Runtime from output: {exp_rel_path} ITER_TIME={iter_time}\n\n"
            f"CMD: {' '.join(map(str, cmd))}\n\n{out}"
        )

    return float(m.group(1)), out, cmd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--smoke",
        action="store_true",
        help="Run a small subset (RUS-1 with 10 and 100 iterations)",
    )
    args = ap.parse_args()

    out_dir = PROJECT_ROOT / "ae" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = get_log_dir(out_dir)

    cases = RUS_CASES
    if args.smoke:
        cases = [c for c in RUS_CASES if c[0] == "RUS-1"]

    out_csv = out_dir / "table1.csv"

    rows = []
    for bench, rel, qubits, gates in cases:
        for it in ITER_LIST:
            print(f"[Table1] Running {bench} ITER_TIME={it} ...", flush=True)
            try:
                t, raw_out, cmd = run_one(rel, it)
            except Exception as e:
                # Save failure details into AE log dir for debugging
                fail_path = log_dir / f"table1_{bench}_it{it}.txt"
                fail_path.write_text(str(e), encoding="utf-8")
                raise

            rows.append(
                {
                    "benchmark": bench,
                    "qubits": qubits,
                    "gates_per_iteration": gates,
                    "iterations": it,
                    "time_seconds": t,
                }
            )
            print(f"[Table1] {bench} it={it} -> {t:.6f} s")

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["benchmark", "qubits", "gates_per_iteration", "iterations", "time_seconds"],
        )
        w.writeheader()
        w.writerows(rows)

    print(f"\n[Table1] Saved: {out_csv}")


if __name__ == "__main__":
    main()