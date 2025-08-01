#!/bin/bash
# Avvio ESPHomeGUIeasy (Linux)
cd "$(dirname "$0")"

PYTHON_EXEC="./python/bin/python3"
if [ -x "$PYTHON_EXEC" ]; then
    export PYTHONHOME="$(pwd)/python"
    echo "Launching ESPHomeGUIeasy using embedded Python..."
else
    PYTHON_EXEC="python3"
    echo "Launching ESPHomeGUIeasy using system Python..."
fi

$PYTHON_EXEC main.py "$@"
