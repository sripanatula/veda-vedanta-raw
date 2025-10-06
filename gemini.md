# Gemini Code Assist - Project Configuration

This file provides context to Gemini Code Assist about the `veda-vedanta-raw` repository.

## Project Overview

This repository, `veda-vedanta-raw`, is the first stage in a multi-repo content pipeline for the vedavedanta.com website. Its sole role is to capture and store raw, unprocessed spiritual verses and commentary as plain text files.

## Key Components

-   **`raw_data/`**: This is the primary data store. It contains the canonical, version-controlled `.txt` files for each verse. The structure is typically `raw_data/<source>/<collection>/verse-NNN.txt`.
-   **`scripts/`**: Contains helper scripts to automate the creation of new verse files.

## Workflow

A user adds a new `verse-NNN.txt` file and commits it. This commit triggers a downstream process in the `veda-vedanta-data` repository that processes this new file.