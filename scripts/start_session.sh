#!/usr/bin/env bash
set -euo pipefail

# Start VNC (local-only) and AirSim Blocks
vncserver -list | grep -q ":1" || vncserver :1 -localhost yes -geometry 1600x900 -depth 24 -xstartup /usr/bin/startxfce4

export DISPLAY=:1
cd ~/airsim_env/LinuxBlocks1.8.1/LinuxNoEditor

# choose renderer via env (default: opengl)
RENDERER="${RENDERER:-opengl}"  # or set RENDERER=vulkan

if pgrep -fa '/Blocks/Binaries/Linux/Blocks' >/dev/null; then
  echo "Blocks already running."
else
  ./Blocks/Binaries/Linux/Blocks -${RENDERER} -windowed -ResX=1600 -ResY=900 -NoSplash -FullStdOutLogOutput \
    > /tmp/Blocks.ui.out 2>&1 &
  echo "Blocks started with ${RENDERER}. Log: /tmp/Blocks.ui.out"
fi
