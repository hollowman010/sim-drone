#!/usr/bin/env bash
set -euo pipefail
export RUN_MODE=${RUN_MODE:-live}
export AIRSIM_HOST=${AIRSIM_HOST:-127.0.0.1}
export AIRSIM_PORT=${AIRSIM_PORT:-41451}
export PYTHONUNBUFFERED=1

echo "🚁 Starting Drone Vision (Live Mode)"
echo "AirSim: ${AIRSIM_HOST}:${AIRSIM_PORT}"

# Ensure AirSim settings are in place
mkdir -p "$HOME/Documents/AirSim"
cp -f "$(dirname "$0")/quick_settings.json" "$HOME/Documents/AirSim/settings.json" || true
echo "✅ AirSim settings installed"

# Activate virtual environment
if [ -f "$HOME/.venv/bin/activate" ]; then
    source "$HOME/.venv/bin/activate"
elif [ -f ".venv/bin/activate" ]; then
    source ".venv/bin/activate"
else
    echo "Warning: No virtual environment found. Using system Python."
fi

# Run the simulation
echo "🚀 Launching drone simulation..."
python -m src.main
