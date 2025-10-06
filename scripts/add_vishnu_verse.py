#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import re
import hashlib
import argparse
import sys
import difflib
from typing import Optional

def next_sequential_verse_number(dirpath: Path) -> int:
    maxn = 0
    for p in dirpath.glob("verse-*.txt"):
        m = re.match(r"verse-(\d+)\.txt", p.name)
        if m:
            maxn = max(maxn, int(m.group(1)))
    return maxn + 1

def find_last_verse_file(dirpath: Path) -> Optional[Path]:
    files = sorted(dirpath.glob("verse-*.txt"))
    return files[-1] if files else None

def parse_verse_number_from_content(content: str) -> Optional[int]:
    """
    Parses the first digits from the content to find the verse number.
    Looks for a line starting with digits, like "52 TVASHTAA".
    """
    m = re.search(r"^\s*(\d+)", content, re.MULTILINE)
    if m:
        return int(m.group(1))
    return None

def split_content_by_signature(content: str) -> list[str]:
    """
    Splits content into chunks based on the author's signature.
    The signature is assumed to be on its own line, possibly with whitespace.
    Example: "Bubhukshitah mvr sharma"
    """
    # The signature acts as a delimiter. We split by it and then re-add it
    # to each chunk, as it's part of the content.
    signature_pattern = r"(Bubhukshitah mvr sharma)"
    parts = re.split(signature_pattern, content, flags=re.IGNORECASE)
    chunks = [parts[i] + (parts[i+1] if i+1 < len(parts) else '') for i in range(0, len(parts), 2)]
    # Filter out any empty strings that might result from splitting
    return [chunk.strip() for chunk in chunks if chunk.strip()]

def sha256_string(s: str) -> str:
    """Returns the SHA256 hash of a string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


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

    # --- Smart File Naming & Chunking ---
    chunks = split_content_by_signature(raw)
    if not chunks:
        print("No content chunks found. Exiting.")
        sys.exit(0)

    print(f"Found {len(chunks)} message chunk(s) to process.")

    for i, chunk_content in enumerate(chunks):
        print(f"\n--- Processing chunk {i+1}/{len(chunks)} ---")
        stripped_chunk = chunk_content.strip()
        content_to_write = chunk_content if args.no_trim else stripped_chunk + "\n"

        # Dedupe against last verse if requested
        if args.dedupe_last:
            lastp = find_last_verse_file(out_dir)
            if lastp and lastp.exists():
                last_raw = lastp.read_text(encoding="utf-8", errors="replace")
                if stripped_chunk == last_raw.strip():
                    print(f"ℹ️ Input is identical to last verse ({lastp.name}). Skipping chunk.")
                    continue

        content_verse_num = parse_verse_number_from_content(content_to_write)

        if content_verse_num:
            # It's a numbered name, use name-NNN.txt format
            out_path = out_dir / f"name-{content_verse_num:03d}.txt"
        else:
            # It's likely a prarthana shloka, use sequential verse-NNN.txt format
            next_n = next_sequential_verse_number(out_dir)
            out_path = out_dir / f"verse-{next_n:03d}.txt"

        if args.dry_run:
            if out_path.exists():
                old_content = out_path.read_text(encoding="utf-8")
                if sha256_string(content_to_write) != sha256_string(old_content):
                    print(f"🟠 would modify: {out_path.name}")
                else:
                    print(f"⚪️ content is unchanged for: {out_path.name}")
            else:
                print(f"⚪️ would create: {out_path.name}")
            continue # Move to next chunk in dry run

        # --- Write Mode ---
        if out_path.exists():
            old_content = out_path.read_text(encoding="utf-8")
            if sha256_string(content_to_write) == sha256_string(old_content):
                print(f"✅ Content for {out_path.name} is already up-to-date. No changes made.")
                continue
            else:
                print(f"⚠️  File '{out_path.name}' already exists. Differences:")
                diff = difflib.unified_diff(
                    old_content.splitlines(keepends=True),
                    content_to_write.splitlines(keepends=True),
                    fromfile=f"a/{out_path.name}",
                    tofile=f"b/{out_path.name}",
                )
                sys.stdout.writelines(diff)

                confirm = input(f"\nDo you want to overwrite this file? (y/N) ")
                if confirm.lower() != 'y':
                    print("Operation cancelled. No changes were made for this chunk.")
                    continue
                print(f"Overwriting existing file: {out_path}")

        out_path.write_text(content_to_write, encoding="utf-8")
        print(f"✅ Wrote to {out_path.name}")

    if args.dry_run:
        print("\nDry run complete. No files were written.")
        sys.exit(0)

    if args.clear_input:
        in_file.write_text("", encoding="utf-8")
        print("🧹 Cleared input file.")

if __name__ == "__main__":
    main()
