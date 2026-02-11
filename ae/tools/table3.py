import argparse
import csv
import os
import re
import shutil
import statistics
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AE_BENCH_DIR = PROJECT_ROOT / "ae" / "benchmarks" / "table3"
FROZEN_DIR = AE_BENCH_DIR / "circuits_py"
EXP_RQC_DIR = PROJECT_ROOT / "exp" / "simulation" / "rqc"
EXP_ENGINE = PROJECT_ROOT / "exp" / "simulation" / "exp_engine.py"

RUNTIME_RE = re.compile(r"Total Runtime\s*:\s*([\d\.]+)\s*s")
LOOPOUT_MARKER = "Max iterations"

TABLE3_MATRIX = [
    (50, 5), (50, 10), (50, 20),
    (100, 5), (100, 10), (100, 20),
    (200, 5), (200, 10), (200, 20),
]


@dataclass
class RunResult:
    benchmark: str
    qubits: int
    gates: int
    mid_meas: int
    run_id: int
    rng_seed: Optional[int]
    status: str               # SUCCESS/TIMEOUT/LOOPOUT/ERROR
    time_seconds: Optional[float]
    note: str = ""


def get_table3_log_dir() -> Path:
    """
    If AE_LOG_DIR is set, store logs under <AE_LOG_DIR>/table3/.
    Otherwise, fallback to ae/results/logs/table3/.
    """
    out_dir = PROJECT_ROOT / "ae" / "results"
    d = os.environ.get("AE_LOG_DIR", "").strip()
    if d:
        p = Path(d)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        return p / "table3"
    return out_dir / "logs" / "table3"


def ensure_dirs(log_dir: Path):
    (PROJECT_ROOT / "ae" / "results").mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    EXP_RQC_DIR.mkdir(parents=True, exist_ok=True)


def sync_frozen_circuits_to_exp_rqc(selected: List[Tuple[int, int, int]]):
    for q, g, m in selected:
        name = f"rqc_q{q}_g{g}_m{m}.py"
        src = FROZEN_DIR / name
        if not src.exists():
            raise FileNotFoundError(f"Frozen circuit not found: {src}")
        dst = EXP_RQC_DIR / name
        shutil.copy2(src, dst)


def parse_runtime(output: str) -> Optional[float]:
    m = RUNTIME_RE.search(output)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def run_once(q: int, g: int, m: int, run_id: int, timeout_s: int, rng_seed: Optional[int]) -> Tuple[RunResult, str, str]:
    bench_py = f"rqc_q{q}_g{g}_m{m}.py"
    bench_mod = f"rqc/rqc_q{q}_g{g}_m{m}"
    cmd = [sys.executable, str(EXP_ENGINE), bench_mod]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    if rng_seed is not None:
        env["QSEQSIM_RNG_SEED"] = str(rng_seed)

    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=str(PROJECT_ROOT / "exp" / "simulation"),
            env=env,
        )
        out = (p.stdout or "")
        err = (p.stderr or "")
        merged = out + "\n" + err

        if LOOPOUT_MARKER in merged:
            return RunResult(bench_py, q, g, m, run_id, rng_seed, "LOOPOUT", None, "Max iterations reached"), out, err

        if p.returncode != 0:
            note = (err.strip() or out.strip()).replace("\n", " ")[:200]
            return RunResult(bench_py, q, g, m, run_id, rng_seed, "ERROR", None, note), out, err

        t = parse_runtime(out)
        if t is None:
            return RunResult(bench_py, q, g, m, run_id, rng_seed, "ERROR", None, "Could not parse Total Runtime"), out, err

        return RunResult(bench_py, q, g, m, run_id, rng_seed, "SUCCESS", t, ""), out, err

    except subprocess.TimeoutExpired:
        return RunResult(bench_py, q, g, m, run_id, rng_seed, "TIMEOUT", None, f"Process timed out > {timeout_s}s"), "", ""


def quantiles_q1_q3(xs: List[float]) -> Tuple[float, float]:
    if len(xs) < 2:
        return xs[0], xs[0]
    qs = statistics.quantiles(xs, n=4)
    return qs[0], qs[2]


def write_csv(path: Path, rows: List[Dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


import json, hashlib

MANIFEST_PATH = AE_BENCH_DIR / "manifest.json"


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_manifest_if_present():
    if not MANIFEST_PATH.exists():
        print(f"[Table3] Manifest not found (skip verify): {MANIFEST_PATH}")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    items = manifest.get("items", {})
    bad = 0
    missing = 0
    for name, meta in items.items():
        p = FROZEN_DIR / name
        if not p.exists():
            print(f"[Table3] Manifest MISSING file: {name}")
            missing += 1
            continue
        exp = meta.get("sha256")
        got = _sha256_file(p)
        if exp != got:
            print(f"[Table3] Manifest HASH MISMATCH: {name}")
            bad += 1
    if missing or bad:
        raise SystemExit(f"[Table3] Manifest verify failed: missing={missing}, mismatch={bad}")
    print(f"[Table3] Manifest verify OK: {len(items)} files")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="Run a small subset quickly, still generates table3_raw.csv and table3.csv")
    ap.add_argument("--repeats", type=int, default=50, help="Number of runs per benchmark (default 50)")
    ap.add_argument("--timeout", type=int, default=600, help="Timeout seconds per run (default 600)")
    ap.add_argument("--base-seed", type=int, default=20240201, help="Base RNG seed for sample mode (requires exp_engine.py seed patch)")
    ap.add_argument("--no-seed", action="store_true", help="Do not set QSEQSIM_RNG_SEED (non-deterministic sampling)")
    ap.add_argument("--only", type=str, default="", help="Comma-separated list like g50m5,g200m20 to run a subset")
    args = ap.parse_args()

    log_dir = get_table3_log_dir()
    ensure_dirs(log_dir)

    q = 100
    matrix = TABLE3_MATRIX

    if args.only.strip():
        wanted = set()
        for part in args.only.split(","):
            part = part.strip().lower()
            if not part:
                continue
            mm = re.fullmatch(r"g(\d+)m(\d+)", part)
            if not mm:
                raise ValueError(f"Bad --only item: {part} (expected g<gates>m<meas>)")
            wanted.add((int(mm.group(1)), int(mm.group(2))))
        matrix = [(g, m) for (g, m) in matrix if (g, m) in wanted]

    if args.smoke:
        matrix = [(50, 5), (50, 10)]
        repeats = min(args.repeats, 5)
    else:
        repeats = args.repeats

    selected = [(q, g, m) for (g, m) in matrix]
    sync_frozen_circuits_to_exp_rqc(selected)

    raw_results: List[RunResult] = []

    for (g, m) in matrix:
        bench = f"rqc_q{q}_g{g}_m{m}.py"
        print(f"[Table3] Running {bench} repeats={repeats} timeout={args.timeout}s", flush=True)

        for i in range(1, repeats + 1):
            rng_seed = None if args.no_seed else (args.base_seed + (g * 1000 + m * 10) + i)
            rr, out, err = run_once(q, g, m, i, args.timeout, rng_seed)
            raw_results.append(rr)

            if rr.status != "SUCCESS":
                (log_dir / f"{bench}.run{i}.txt").write_text(
                    f"status={rr.status}\nseed={rng_seed}\n\nSTDOUT:\n{out}\n\nSTDERR:\n{err}\n",
                    encoding="utf-8",
                )

    raw_rows = [
        {
            "benchmark": r.benchmark,
            "qubits": r.qubits,
            "gates": r.gates,
            "mid_meas": r.mid_meas,
            "run_id": r.run_id,
            "rng_seed": "" if r.rng_seed is None else r.rng_seed,
            "status": r.status,
            "time_seconds": "" if r.time_seconds is None else f"{r.time_seconds:.6f}",
            "note": r.note,
        }
        for r in raw_results
    ]

    raw_path = PROJECT_ROOT / "ae" / "results" / "table3_raw.csv"
    write_csv(raw_path, raw_rows)

    summary = []
    for (g, m) in matrix:
        times = [
            r.time_seconds
            for r in raw_results
            if r.gates == g and r.mid_meas == m and r.status == "SUCCESS" and r.time_seconds is not None
        ]
        valid = len(times)
        if valid == 0:
            median = q1 = q3 = None
        else:
            times_sorted = sorted(times)
            median = statistics.median(times_sorted)
            q1, q3 = quantiles_q1_q3(times_sorted)

        summary.append(
            {
                "benchmark": f"rqc_q{q}_g{g}_m{m}",
                "qubits": q,
                "gates": g,
                "mid_meas": m,
                "valid_runs": valid,
                "median_seconds": "" if median is None else f"{median:.3f}",
                "q1_seconds": "" if q1 is None else f"{q1:.3f}",
                "q3_seconds": "" if q3 is None else f"{q3:.3f}",
            }
        )

    summary_path = PROJECT_ROOT / "ae" / "results" / "table3.csv"
    write_csv(summary_path, summary)

    print(f"\n[Table3] Saved raw: {raw_path}")
    print(f"[Table3] Saved summary: {summary_path}")
    print(f"[Table3] Failure logs dir: {log_dir}")


if __name__ == "__main__":
    verify_manifest_if_present()
    main()