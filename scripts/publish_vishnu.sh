#!/bin/bash
#
# publish_vishnu.sh - Full end-to-end publishing pipeline for a new Vishnu verse.
#
# This script automates the following process:
# 1. Adds a new verse from the inbox/temp.txt file to the veda-vedanta-raw repo.
# 2. Commits and pushes the new raw verse.
# 3. Navigates to the veda-vedanta-data repo.
# 4. Runs the processor to generate JSON from the new raw verse.
# 5. Commits and pushes the new data.
#

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
# Get the directory of the currently executing script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
RAW_REPO_ROOT="$SCRIPT_DIR/.."
DATA_REPO_ROOT="$RAW_REPO_ROOT/../veda-vedanta-data"

AUTO_PUSH=false
if [[ "$1" == "--auto" ]]; then
  AUTO_PUSH=true
fi

echo "=== 1. Processing Raw Content (veda-vedanta-raw) ==="
cd "$RAW_REPO_ROOT"

# Run the python script in dry-run mode first to see what it plans to do.
ADD_SCRIPT_OUTPUT=$(PYTHONIOENCODING=utf-8 python3 scripts/add_vishnu_verse.py --dedupe-last --dry-run)

echo "Python script plans to:"
echo "$ADD_SCRIPT_OUTPUT"

read -p "Do you want to proceed with creating this file? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled by user. Exiting."
    exit 1
fi

# If confirmed, run the script for real to create the file and clear the inbox.
PYTHONIOENCODING=utf-8 python3 scripts/add_vishnu_verse.py --dedupe-last --clear-input

# --- Git Commit ---
# The python script will have created/modified a file. Let's find it.
# This is more robust. It asks for the status of the whole repo and then filters for the specific directory.
CHANGED_FILE=$(git status --porcelain | grep "raw_data/mvr/vishnu/" | head -n 1 | awk '{print $2}')

if [ -z "$CHANGED_FILE" ]; then
  echo "No raw file changes detected by git. Exiting."
  exit 0
fi

echo "Staging file: $CHANGED_FILE"
git add "$CHANGED_FILE"

# Create a nice commit message from the filename
FILENAME=$(basename "$CHANGED_FILE")
COMMIT_MSG="feat: Add ${FILENAME%.*}" # Default to "feat: Add name-052"

# Check if the file existed before this change to decide between "feat:" and "fix:"
if git cat-file -e HEAD:"$CHANGED_FILE" 2>/dev/null; then
    COMMIT_MSG="fix: Update ${FILENAME%.*}" # e.g. "fix: Update name-052"
fi

git commit -m "$COMMIT_MSG"

if [ "$AUTO_PUSH" = true ]; then
  git push
  echo "Pushed changes to veda-vedanta-raw."
else
  read -p "Push changes to veda-vedanta-raw? (y/N) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push
  fi
fi

echo ""
echo "=== 2. Generating Structured Data (veda-vedanta-data) ==="
cd "$DATA_REPO_ROOT"

# Run the update script, which will detect the new raw file and auto-commit/push
python3 tools/update_from_raw.py --push

echo ""
echo "✅ Publish complete."