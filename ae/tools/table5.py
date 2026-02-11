import argparse
import csv
import time
import sys
from pathlib import Path

# Ensure project root is importable (so `import src...` works)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from exp.simulation.rus.rus_1 import circ
from src.parser import QiskitParser
from src.simulator import BDDSimulator

OUT_DIR = PROJECT_ROOT / "ae" / "results"


def run_table5(k_max: int, repeat_runs: int):
    parser = QiskitParser(circ)
    structure = parser.parse()
    sim = BDDSimulator(structure)

    rows = []
    cumulative = 0.0

    for k in range(0, k_max + 1):
        times = []
        ppath = None

        # pattern: 1^k 0 on clbit 0
        for _ in range(repeat_runs):
            t0 = time.perf_counter()
            sim.run(mode="preset", presets={0: ([1] * k + [0])})
            t1 = time.perf_counter()
            times.append(t1 - t0)
            ppath = sim.global_probability

        avg_time = sum(times) / len(times)
        cumulative += (ppath or 0.0)

        rows.append(
            {
                "k": k,
                "ppath": f"{ppath:.10f}" if ppath is not None else "",
                "pterm": f"{cumulative:.10f}",
                "time_seconds_avg": f"{avg_time:.6f}",
                "repeat_runs": repeat_runs,
            }
        )

    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="Run a small subset for quick sanity check")
    ap.add_argument("--k-max", type=int, default=8, help="Max k (default 8, i.e., k=0..8)")
    ap.add_argument("--repeat-runs", type=int, default=5, help="Repeats per k for averaging (default 5)")
    args = ap.parse_args()

    # Smoke defaults: very fast, still checks preset-path probability plumbing
    if args.smoke:
        if args.k_max == 8:
            args.k_max = 2  # only k=0..2
        if args.repeat_runs == 5:
            args.repeat_runs = 3

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = run_table5(k_max=args.k_max, repeat_runs=args.repeat_runs)

    out_csv = OUT_DIR / "table5.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"[Table5] Saved: {out_csv}")
    print(f"[Table5] k_max={args.k_max}, repeat_runs={args.repeat_runs}")


if __name__ == "__main__":
    main()