#!/bin/bash
# Start the Recovery Tracker server with ONE command.
# It handles everything that keeps tripping you up:
#   - moves into the project folder (no matter where you run it from)
#   - activates THIS project's virtual environment
#   - starts the server with auto-reload
#
# Run it with:   bash run.sh
# Stop it with:  Ctrl+C

# Move to the folder this script lives in (your project folder).
cd "$(dirname "$0")"

# Turn on the project's virtual environment.
source venv/bin/activate

# Start the server.
python -m uvicorn main:app --reload
