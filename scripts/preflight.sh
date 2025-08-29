#!/usr/bin/env bash
# Pre-flight smoke test for AirSim on the GPU VM.
# Checks: VNC server -> X display -> Blocks process -> AirSim RPC -> quick logs

set -u -o pipefail

# --- styling ---
if [ -t 1 ]; then
  BOLD="\033[1m"; RED="\033[31m"; GRN="\033[32m"; YEL="\033[33m"; BLU="\033[34m"; RST="\033[0m"
else
  BOLD=""; RED=""; GRN=""; YEL=""; BLU=""; RST=""
fi
ok()   { echo -e "${GRN}PASS${RST}  $*"; }
warn() { echo -e "${YEL}WARN${RST}  $*"; }
fail() { echo -e "${RED}FAIL${RST}  $*"; FAIL_COUNT=$((FAIL_COUNT+1)); }
info() { echo -e "${BLU}${BOLD}INFO${RST}  $*"; }

FAIL_COUNT=0
DISPLAY="${DISPLAY:-:1}"

# Compute VNC port from DISPLAY (:N -> 5900+N)
if [[ "$DISPLAY" =~ :([0-9]+) ]]; then
  DISP_NUM="${BASH_REMATCH[1]}"
else
  DISP_NUM="1"
fi
VNC_PORT=$((5900 + DISP_NUM))

# --- deps ---
need_cmd() { command -v "$1" >/dev/null 2>&1 || { fail "Missing command: $1"; }; }

info "Checking dependencies…"
for c in python3 vncserver pgrep ss; do need_cmd "$c"; done
command -v nvidia-smi >/dev/null 2>&1 && NV_PRESENT=1 || NV_PRESENT=0
[ $FAIL_COUNT -eq 0 ] && ok "Core commands present"

# --- VNC / X display ---
info "Checking VNC server on 127.0.0.1:${VNC_PORT} (DISPLAY ${DISPLAY})…"
if ss -tlnp | grep -q "127.0.0.1:${VNC_PORT}"; then
  ok "VNC is listening on 127.0.0.1:${VNC_PORT}"
else
  fail "VNC is NOT listening on 127.0.0.1:${VNC_PORT} (start: 'vncserver ${DISPLAY} -localhost yes -geometry 1600x900 -depth 24 -xstartup /usr/bin/startxfce4')"
fi

# Try a lightweight X check
if DISPLAY="$DISPLAY" xset q >/dev/null 2>&1; then
  ok "X display ${DISPLAY} is accessible"
else
  warn "Could not query X on ${DISPLAY}. If VNC just started, this can be transient."
fi

# --- Blocks (AirSim UE binary) ---
info "Checking Unreal/Blocks process…"
if pgrep -f "/Blocks/Binaries/Linux/Blocks" >/dev/null 2>&1; then
  ok "Blocks process is running"
else
  fail "Blocks process not running (start: '~/airsim_env/LinuxBlocks1.8.1/LinuxNoEditor/Blocks/Binaries/Linux/Blocks -opengl -windowed')"
fi

# Quick scan of Blocks log if present
if [ -f /tmp/Blocks.ui.out ]; then
  if grep -Eiq "fatal|segmentation|sigsegv|ensure condition failed|assert" /tmp/Blocks.ui.out; then
    warn "Potential crash/err in /tmp/Blocks.ui.out (showing last lines):"
    tail -n 10 /tmp/Blocks.ui.out | sed 's/^/       /'
  else
    ok "/tmp/Blocks.ui.out has no obvious fatal errors"
  fi
else
  warn "Blocks log not found at /tmp/Blocks.ui.out (it will appear after launch)"
fi

# --- AirSim RPC connectivity ---
info "Checking AirSim RPC connectivity…"
python3 - <<'PY'
import json, os, socket, sys
host = os.environ.get("AIRSIM_RPC_HOST", "127.0.0.1")
port_env = os.environ.get("AIRSIM_RPC_PORT")
port = None

# Try to read RpcPort from settings.json
settings = os.path.expanduser("~/Documents/AirSim/settings.json")
if os.path.isfile(settings):
    try:
        with open(settings) as f:
            j = json.load(f)
        p = j.get("RpcPort")
        if isinstance(p, int):
            port = p
    except Exception:
        pass

if port_env and port_env.isdigit():
    port = int(port_env)

if port is None:
    port = 41451

# TCP check
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1.5)
try:
    s.connect((host, port))
    s.close()
    print(f"OK TCP {host}:{port}")
except Exception as e:
    print(f"FAIL TCP {host}:{port} -> {e}")
    sys.exit(2)

# AirSim API ping
try:
    import airsim
    client = airsim.MultirotorClient(ip=host, port=port, timeout_value=2)
    client.confirmConnection()
    state = client.getMultirotorState()
    print("OK AirSim RPC (vehicle ready)")
except Exception as e:
    print(f"FAIL AirSim RPC -> {e}")
    sys.exit(3)
PY
case $? in
  0) ok "AirSim RPC reachable" ;;
  2) fail "AirSim TCP port unreachable (host/port wrong or Blocks not ready)" ;;
  3) fail "AirSim RPC handshake failed (Blocks running but RPC not alive)" ;;
  *) fail "AirSim RPC check unknown error" ;;
esac

# --- optional GPU check ---
if [ "$NV_PRESENT" -eq 1 ]; then
  if nvidia-smi >/dev/null 2>&1; then
    ok "NVIDIA driver present"
  else
    warn "NVIDIA driver not responding (not fatal for -opengl mode)"
  fi
fi

# --- settings.json presence ---
SETTINGS=~/Documents/AirSim/settings.json
if [ -f "$SETTINGS" ]; then
  ok "Settings present at $SETTINGS"
else
  warn "No settings at $SETTINGS (copy one: 'cp scripts/quick_settings.json \"$SETTINGS\"')"
fi

echo
if [ $FAIL_COUNT -eq 0 ]; then
  echo -e "${GRN}${BOLD}PRE-FLIGHT: ALL CHECKS PASSED ✅${RST}"
  exit 0
else
  echo -e "${RED}${BOLD}PRE-FLIGHT: $FAIL_COUNT CHECK(S) FAILED ❌${RST}"
  exit 1
fi
