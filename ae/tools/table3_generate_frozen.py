import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GEN_RQC = PROJECT_ROOT / "exp" / "simulation" / "gen_rqc.py"
GEN_OUT_DIR = PROJECT_ROOT / "exp" / "simulation" / "rqc"

FROZEN_DIR = PROJECT_ROOT / "ae" / "benchmarks" / "table3" / "circuits_py"
MANIFEST_GEN = PROJECT_ROOT / "ae" / "tools" / "table3_gen_manifest.py"
MANIFEST_VERIFY = PROJECT_ROOT / "ae" / "tools" / "table3_verify_manifest.py"

TABLE3_MATRIX = [
    (50, 5), (50, 10), (50, 20),
    (100, 5), (100, 10), (100, 20),
    (200, 5), (200, 10), (200, 20),
]

def seed_formula(g: int, m: int) -> int:
    return 100000 + g * 100 + m

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(
            "Command failed:\n"
            + "CMD: " + " ".join(map(str, cmd)) + "\n\n"
            + "STDOUT:\n" + (p.stdout or "") + "\n\n"
            + "STDERR:\n" + (p.stderr or "")
        )
    return p.stdout, p.stderr

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", type=int, default=100, help="Number of qubits (default 100)")
    ap.add_argument("--force", action="store_true", help="Overwrite existing frozen circuits")
    ap.add_argument("--skip-verify", action="store_true", help="Skip manifest verification step")
    args = ap.parse_args()

    if not GEN_RQC.exists():
        raise FileNotFoundError(f"gen_rqc.py not found: {GEN_RQC}")

    FROZEN_DIR.mkdir(parents=True, exist_ok=True)
    GEN_OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) Generate 9 circuits with fixed seeds
    for g, m in TABLE3_MATRIX:
        seed = seed_formula(g, m)
        name = f"rqc_q{args.q}_g{g}_m{m}.py"

        print(f"[FreezeGen] Generating {name} seed={seed}", flush=True)
        cmd = [sys.executable, str(GEN_RQC), str(args.q), str(g), str(m), "--seed", str(seed)]
        run(cmd, cwd=str(PROJECT_ROOT / "exp" / "simulation"))

        src = GEN_OUT_DIR / name
        if not src.exists():
            raise FileNotFoundError(f"Expected generated circuit not found: {src}")

        dst = FROZEN_DIR / name
        if dst.exists() and not args.force:
            raise FileExistsError(
                f"Frozen circuit already exists: {dst}\n"
                f"Use --force to overwrite."
            )

        shutil.copy2(src, dst)

    # 2) Generate manifest (sha256)
    print("[FreezeGen] Generating manifest.json", flush=True)
    run([sys.executable, str(MANIFEST_GEN)], cwd=str(PROJECT_ROOT))

    # 3) Verify manifest
    if not args.skip_verify:
        print("[FreezeGen] Verifying manifest.json", flush=True)
        run([sys.executable, str(MANIFEST_VERIFY)], cwd=str(PROJECT_ROOT))

    print(f"[FreezeGen] Done. Frozen circuits at: {FROZEN_DIR}")

if __name__ == "__main__":
    main()