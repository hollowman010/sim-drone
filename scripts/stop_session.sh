#!/usr/bin/env bash
set -euo pipefail
pkill -f '/Blocks/Binaries/Linux/Blocks' || true
vncserver -kill :1 || true
