#!/bin/bash
# Helper script to run commands with the virtual environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at .venv/"
    echo "Please run: python -m venv .venv && .venv/bin/pip install -e ."
    exit 1
fi

# Run the command with the venv python
exec "$VENV_PYTHON" "$@"
