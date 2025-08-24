#!/usr/bin/env bash
set -euo pipefail

# Set Python to use UTF-8 encoding for its standard streams.
# This prevents UnicodeEncodeError on Windows when printing emojis.
export PYTHONUTF8=1

# --- Config ---------------------------------------------------------------
RAW_REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
INPUT="${INPUT:-$RAW_REPO/inbox/temp.txt}"
OUTDIR="${OUTDIR:-$RAW_REPO/raw_data/mvr/vishnu}"
DATA_REPO="${DATA_REPO:-$RAW_REPO/../veda-vedanta-data}"
BRANCH="${BRANCH:-main}"
REMOTE="${REMOTE:-origin}"

AUTO=0
DRY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --auto) AUTO=1; shift ;;
    --dry-run) DRY=1; shift ;;
    *) shift ;;
  esac
done

run() { echo "+ $*"; [[ $DRY -eq 1 ]] || eval "$@"; }

nonblank_file() { grep -q '[^[:space:]]' "$1" 2>/dev/null; }

# --- Guards ---------------------------------------------------------------
if [[ ! -f "$INPUT" ]] || ! nonblank_file "$INPUT"; then
  echo "ℹ️ $INPUT is missing or whitespace-only. Nothing to do."
  exit 0
fi
[[ -d "$DATA_REPO" ]] || { echo "❌ DATA_REPO not found: $DATA_REPO"; exit 1; }

# Remember the latest verse before we run Python
BEFORE=$(ls "$OUTDIR"/verse-*.txt 2>/dev/null | sort | tail -n1 || true)

# --- 1) Create next verse in RAW repo -------------------------------------
CMD="python3 \"$RAW_REPO/scripts/add_vishnu_verse.py\" \
  --input \"$INPUT\" \
  --outdir \"$OUTDIR\" \
  --dedupe-last \
  --clear-input"
[[ $DRY -eq 1 ]] && CMD+=" --dry-run"
run "$CMD"

AFTER=$(ls "$OUTDIR"/verse-*.txt 2>/dev/null | sort | tail -n1 || true)
if [[ -z "$AFTER" || "$AFTER" == "$BEFORE" ]]; then
  echo "ℹ️ No new verse file was created."
  if nonblank_file "$INPUT"; then
    echo "  This is likely because the content in '$INPUT' is a duplicate of the last verse."
    echo "  The data update and push steps will be skipped."
  fi
  exit 0
fi
echo "✅ New verse: $(basename "$AFTER")"

# --- 2) Update vv-data using existing parser ------------------------------
cd "$DATA_REPO"
run "python3 tools/update_from_raw.py"

# --- 3) Commit & push vv-data --------------------------------------------
CHANGES=$(git status --porcelain)
if [[ -n "$CHANGES" ]]; then
  run "git add -A"
  run "git commit -m \"auto: update data for $(basename "$AFTER")\""
else
  echo "ℹ️ No uncommitted changes (parser may have committed already)."
fi

if [[ $AUTO -eq 1 ]]; then
  run "git push \"$REMOTE\" \"$BRANCH\""
else
  read -r -p "Push vv-data to $REMOTE/$BRANCH now? [Y/n] " ans
  if [[ -z "${ans:-}" || "$ans" =~ ^[Yy]$ ]]; then
    run "git push \"$REMOTE\" \"$BRANCH\""
  else
    echo "⏭️ Skipping push."
  fi
fi

echo "🎉 Done."
