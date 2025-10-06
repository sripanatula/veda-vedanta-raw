# Veda Vedanta - Raw Content Repository

This repository is the starting point for the Veda Vedanta content pipeline. It holds the raw, unprocessed verses and commentary as they are received, before they are processed.

The final published content is available at [vedavedanta.com](https://vedavedanta.com).

## 🕉️ Purpose

The primary purpose of this repository is to capture and version-control the daily verses. It acts as a staging area where new content from sources like WhatsApp messages can be saved and prepared for automated processing.

This repository contains:
-   **Raw Data**: The `raw_data/` directory contains the verses, organized by collection (e.g., `raw_data/mvr/vishnu`).
-   **Inbox**: The `inbox/` directory can be used as a temporary holding area for new messages.
-   **Scripts**: The `scripts/` directory contains helper scripts to create new verse files (e.g., `add_vishnu_verse.py`).

## Workflow

The typical content publishing workflow starts here:

1.  **Capture**: A new verse and its meaning are received (e.g., via a WhatsApp message).
2.  **Save**: The content is saved into a new, sequentially numbered text file (e.g., `raw_data/mvr/vishnu/verse-NNN.txt`). This can be done manually or with a helper script.
    -   Numbered "namas" are saved as `name-NNN.txt`.
    -   Unnumbered introductory "prarthana shlokas" are saved as `verse-NNN.txt`.
3.  **Commit**: The new file is committed and pushed to this repository's `main` branch.

This push triggers an automated workflow in the `veda-vedanta-data` repository, which takes over the processing from this point.

## Scripts

### `scripts/add_vishnu_verse.py`

This is a helper script for adding new verses to the 'Vishnu' collection.

**Usage:**

1.  Paste the new verse content into `inbox/temp.txt`.
2.  Run the script:
    ```bash
    python scripts/add_vishnu_verse.py
    ```
3.  The script will intelligently create either a `name-NNN.txt` or `verse-NNN.txt` file based on the content.