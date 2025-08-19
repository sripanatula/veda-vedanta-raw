#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import re
import argparse
import sys

def next_verse_number(dirpath: Path) -> int:
    maxn = 0
    for p in dirpath.glob("verse-*.txt"):
        m = re.match(r"verse-(\d+)\.txt", p.name)
        if m:
            maxn = max(maxn, int(m.group(1)))
    return maxn + 1

def last_verse_path(dirpath: Path) -> Path | None:
    files = sorted(dirpath.glob("verse-*.txt"))
    return files[-1] if files else None

def main():
    ap = argparse.ArgumentParser(description="Copy latest message into next verse-NNN.txt (Vishnu only).")
    ap.add_argument("--input", default="inbox/temp.txt", help="Path to the latest message file. Default: inbox/temp.txt")
    ap.add_argument("--outdir", default="raw_data/mvr/vishnu", help="Target directory. Default: raw_data/mvr/vishnu")
    ap.add_argument("--no-trim", action="store_true", help="Do not trim leading/trailing whitespace in the saved verse.")
    ap.add_argument("--clear-input", action="store_true", help="Truncate the input file after successful publish.")
    ap.add_argument("--dedupe-last", action="store_true", help="Skip if input equals the last verse content (after trim).")
    ap.add_argument("--dry-run", action="store_true", help="Show what would happen without writing.")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    in_file = (repo_root / args.input).resolve()
    out_dir = (repo_root / args.outdir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_file.exists():
        print(f"❌ Not found: {in_file}")
        sys.exit(1)

    raw = in_file.read_text(encoding="utf-8", errors="replace")
    stripped = raw.strip()

    # Treat whitespace-only as empty regardless of --no-trim
    if not stripped:
        print("ℹ️ Input is empty or whitespace-only. Nothing to publish.")
        sys.exit(0)

    # Dedupe against last verse if requested
    if args.dedupe_last:
        lastp = last_verse_path(out_dir)
        if lastp and lastp.exists():
            last_raw = lastp.read_text(encoding="utf-8", errors="replace")
            if stripped == last_raw.strip():
                print(f"ℹ️ Input is identical to last verse ({lastp.name}). Skipping.")
                sys.exit(0)

    content_to_write = (raw if args.no_trim else stripped + "\n")

    n = next_verse_number(out_dir)
    out_path = out_dir / f"verse-{n:03d}.txt"

    if args.dry_run:
        print(f"⚪ would create: {out_path}")
        sys.exit(0)

    out_path.write_text(content_to_write, encoding="utf-8")
    print(f"✅ created: {out_path}")

    if args.clear_input:
        in_file.write_text("", encoding="utf-8")
        print("🧹 Cleared input file.")

if __name__ == "__main__":
    main()
