# Quick Start (Cloud, GCP)

This gets you from **powered-off VM** to **drone flying in AirSim**.

## Prereqs
- `gcloud` installed & logged in (`gcloud auth login`, `gcloud config set project drone-sim-project`)
- GPU quota for T4 in `us-central1-a`

## Start-of-Day (Copy/Paste Commands)

### 1) Start GPU VM
```bash
gcloud compute instances start airsim-gpu --zone=us-central1-a
```

### 2) Start VNC on the VM (if not already running)
```bash
gcloud compute ssh airsim-gpu --zone=us-central1-a --command \
  "vncserver -kill :1 || true; vncserver :1 -localhost yes -geometry 1600x900 -depth 24 -xstartup /usr/bin/startxfce4"
```

**Note**: Use a strong VNC password when prompted (not "password")

### 3) Open the SSH tunnel (run this in a terminal you keep open)
```bash
gcloud compute ssh airsim-gpu --zone=us-central1-a -- \
  -N -L 5901:localhost:5901 \
  -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3
```

### 4) Connect your VNC viewer to `localhost:5901`

### 5) Launch AirSim Blocks (in the VNC desktop terminal)
```bash
cd ~/airsim_env/LinuxBlocks1.8.1/LinuxNoEditor
./Blocks/Binaries/Linux/Blocks -opengl -windowed -ResX=1600 -ResY=900
```

### 6) Setup AirSim settings (first time or when you change them)
```bash
mkdir -p ~/Documents/AirSim
cp -f ~/sim-drone/config/settings.json ~/Documents/AirSim/settings.json 2>/dev/null || true
```

### 7) Run the smoke test (from a VM terminal - not your Mac)
```bash
cd ~/sim-drone
git pull  # get latest code
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt
./scripts/airsim_takeoff.py
```

### 8) Run your full mission
```bash
python -m src.main --mode=live
```

You should see the drone take off, hover, and land!

## End-of-Day (Save Costs)

### On the VM (stop AirSim + VNC):
```bash
pkill -f Blocks || true
vncserver -kill :1 || true
```

### On your laptop (stop VM):
```bash
# Close the SSH tunnel (Ctrl+C in the tunnel terminal)
gcloud compute instances stop airsim-gpu --zone=us-central1-a
```

## Troubleshooting

**Python prints "demo" banner** → set `RUN_MODE=live`.

**Connection refused** → ensure Blocks is running; check that settings.json has ApiServerPort: 41451.

**Viewer is blank / slow** → keep `-opengl` and `1600x900`; T4 under VNC is OK but not blazing fast.

**VNC won't open** → confirm the tunnel process is running locally and the server was started with `-localhost yes`.

## Mode Selection

- **Live Mode**: `RUN_MODE=live scripts/run_live.sh` - Controls real AirSim drone
- **Demo Mode**: `RUN_MODE=demo python -m src.main` - Simulation for testing (no AirSim needed)
