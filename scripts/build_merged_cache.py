"""Build a merged price cache root (raw/ folder of symlinks) without copying or touching data/raw.

Each entry is a symlink to either a main-cache file (data/raw/<T>.parquet, Tier A and base names)
or a converted Tier B file. Name collisions are an error, so a Tier B name can never shadow a main
file.

Usage (from repo root):
    .venv/bin/python -I scripts/build_merged_cache.py --main data/raw \
        --extra runs_final/raw_tierB_adj/raw --out runs_final/merged_cache/raw
"""
import argparse
import os
from pathlib import Path


def build(main_dir: Path, extra_dir: Path, out_dir: Path) -> int:
    main = {p.name for p in main_dir.glob("*.parquet")}
    extra = {p.name for p in extra_dir.glob("*.parquet")}
    clash = sorted(main & extra)
    if clash:
        raise SystemExit(f"name collision between main and extra caches: {clash[:10]}")
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.parquet"):
        if old.is_symlink():
            old.unlink()
    for name in sorted(main):
        os.symlink((main_dir / name).resolve(), out_dir / name)
    for name in sorted(extra):
        os.symlink((extra_dir / name).resolve(), out_dir / name)
    return len(main) + len(extra)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--main", required=True, type=Path)
    ap.add_argument("--extra", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    if str(args.out.resolve()).startswith(str(Path("data").resolve())):
        raise SystemExit("refusing to write under data/")
    n = build(args.main, args.extra, args.out)
    print(f"merged cache: {n} symlinks -> {args.out}")


if __name__ == "__main__":
    main()
