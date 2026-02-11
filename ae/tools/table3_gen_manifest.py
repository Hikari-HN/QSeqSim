import argparse
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FROZEN_DIR = PROJECT_ROOT / "ae" / "benchmarks" / "table3" / "circuits_py"
MANIFEST_PATH = PROJECT_ROOT / "ae" / "benchmarks" / "table3" / "manifest.json"

NAME_RE = re.compile(r"rqc_q(\d+)_g(\d+)_m(\d+)\.py$")

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--circuits-dir", type=str, default=str(FROZEN_DIR))
    ap.add_argument("--out", type=str, default=str(MANIFEST_PATH))
    ap.add_argument("--note", type=str, default="frozen circuits for Table 3 AE")
    args = ap.parse_args()

    circuits_dir = Path(args.circuits_dir)
    out_path = Path(args.out)

    if not circuits_dir.exists():
        raise FileNotFoundError(f"circuits dir not found: {circuits_dir}")

    items = {}
    for p in sorted(circuits_dir.glob("rqc_q*_g*_m*.py")):
        m = NAME_RE.search(p.name)
        if not m:
            continue
        q = int(m.group(1))
        g = int(m.group(2))
        mm = int(m.group(3))
        items[p.name] = {
            "qubits": q,
            "gates_target": g,
            "mid_meas_target": mm,
            "sha256": sha256_file(p),
        }

    manifest = {
        "schema": "qseqsim-ae.table3.manifest.v1",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "note": args.note,
        "circuits_dir": str(circuits_dir.relative_to(PROJECT_ROOT)) if str(circuits_dir).startswith(str(PROJECT_ROOT)) else str(circuits_dir),
        "items": items,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[Manifest] Wrote: {out_path}")
    print(f"[Manifest] Items: {len(items)}")

if __name__ == "__main__":
    main()