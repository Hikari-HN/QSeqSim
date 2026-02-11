import argparse
import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = PROJECT_ROOT / "ae" / "benchmarks" / "table3" / "manifest.json"
DEFAULT_DIR = PROJECT_ROOT / "ae" / "benchmarks" / "table3" / "circuits_py"

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=str, default=str(DEFAULT_MANIFEST))
    ap.add_argument("--circuits-dir", type=str, default=str(DEFAULT_DIR))
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    circuits_dir = Path(args.circuits_dir)

    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest not found: {manifest_path}")
    if not circuits_dir.exists():
        raise FileNotFoundError(f"circuits dir not found: {circuits_dir}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    items = manifest.get("items", {})

    bad = 0
    missing = 0
    checked = 0

    for name, meta in items.items():
        p = circuits_dir / name
        if not p.exists():
            print(f"[Verify] MISSING: {name}")
            missing += 1
            continue
        expected = meta.get("sha256")
        got = sha256_file(p)
        checked += 1
        if expected != got:
            print(f"[Verify] HASH MISMATCH: {name}")
            print(f"  expected: {expected}")
            print(f"  got     : {got}")
            bad += 1

    if missing or bad:
        raise SystemExit(f"[Verify] FAILED: checked={checked}, missing={missing}, mismatch={bad}")
    print(f"[Verify] OK: checked={checked}")

if __name__ == "__main__":
    main()