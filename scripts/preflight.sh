#!/usr/bin/env bash
set -euo pipefail

echo "⛽ creating venv + installing deps"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt || pip install -e .[dev]

echo "🧪 checking AirSim RPC"
python scripts/airsim_takeoff.py --timeout 20