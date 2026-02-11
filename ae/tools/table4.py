import argparse
import csv
import time
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.kernel import BDDSeqSim

OUT_DIR = PROJECT_ROOT / "ae" / "results"


def run_table4(n: int, ks, r: int = 3):
    rows = []
    for k in ks:
        Sim = BDDSeqSim(n, n - 1, r)
        result_list = [0] * (k - 1) + [1]
        input_basis_list = [0] * len(result_list)

        Sim.init_stored_state_by_basis(0)

        t0 = time.time()
        for result, input_basis in zip(result_list, input_basis_list):
            Sim.init_input_state_by_basis(input_basis)
            Sim.init_comb_bdd()
            Sim.H(1)
            Sim.cwalk(1, list(range(2, n)))
            Sim.multi_controlled_X(list(range(1, n)), 0)
            Sim.measure([result])
        t1 = time.time()

        prob = Sim.prob_list[-1]
        reachable = (prob > 0.0)

        rows.append(
            {
                "qubits": n,
                "k": k,
                "reachable": "Yes" if reachable else "No",
                "probability": f"{prob}",
                "time_seconds": f"{(t1 - t0):.6f}",
            }
        )
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="Run a small subset for quick sanity check")
    ap.add_argument("--n", type=int, default=256, help="Number of qubits (default 256)")
    ap.add_argument("--k", type=str, default="", help="Comma-separated k list, e.g. 1,3,7 (overrides default)")
    args = ap.parse_args()

    if args.k.strip():
        ks = [int(x.strip()) for x in args.k.split(",") if x.strip()]
    else:
        ks = list(range(1, 11))

    if args.smoke and not args.k.strip():
        ks = [1, 2]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = run_table4(n=args.n, ks=ks)

    out_csv = OUT_DIR / "table4.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"[Table4] Saved: {out_csv}")
    print(f"[Table4] ks={ks}")


if __name__ == "__main__":
    main()