#!/usr/bin/env bash
set -euo pipefail
mkdir -p ~/Documents/AirSim
cp -f "$(dirname "$0")/quick_settings.json" ~/Documents/AirSim/settings.json
echo "Installed AirSim settings to ~/Documents/AirSim/settings.json"
