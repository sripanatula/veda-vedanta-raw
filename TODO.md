# Project TODO List

This file tracks planned improvements and future work for the Veda Vedanta project.

## Handling "Uttara Peethika" (Concluding Verses)

**Problem:**
The Vishnu Sahasranama content has three distinct sections:
1.  **Purva Peethika**: Introductory verses (currently handled as `verse-NNN.txt`).
2.  **Namas**: The 1000 numbered names (currently handled as `name-NNN.txt`).
3.  **Uttara Peethika**: Concluding verses, which are unnumbered like the introductory ones.

The current `add_vishnu_verse.py` script cannot distinguish between introductory and concluding verses. When we start adding the "uttara peethika", the script will incorrectly create files like `verse-015.txt`, mixing them with the "purva peethika" at the beginning of the collection.

---

**Proposed Solution:**

When we are ready to add the "uttara peethika", we should update the `add_vishnu_verse.py` script to be more intelligent.

1.  **Detect the Last Nama**: The script should check for the existence of the final nama file (e.g., `name-108.txt` or `name-1000.txt`).

2.  **Conditional Naming**:
    -   If the final nama file **does not** exist, any unnumbered content is considered "purva peethika" and should be named `verse-NNN.txt` (current behavior).
    -   If the final nama file **does** exist, any unnumbered content is considered "uttara peethika" and should be named `epilogue-NNN.txt`. A new sequential counter will be needed for these files.

3.  **Downstream Update**: The `update_from_raw.py` script in the `veda-vedanta-data` repository will also need to be updated to recognize and process `epilogue-NNN.txt` files, assigning them a `type: "epilogue"` in the `index.json`. This will allow the UI to place them correctly at the very end of the content.

This approach automates the distinction between the three content types, ensuring correct ordering and clear file organization without requiring manual user input.