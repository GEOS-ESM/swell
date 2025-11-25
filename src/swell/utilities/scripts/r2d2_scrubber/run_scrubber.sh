#!/bin/bash
set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load R2D2 module
source "$SCRIPT_DIR/load_r2d2.sh"

# Run scrubber, write to log file
python3 "$SCRIPT_DIR/r2d2_scrub.py --scrub" >> "$SCRIPT_DIR/scrub.log" 2>&1