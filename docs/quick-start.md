# 🚀 Quick Start Guide: Drone Vision AirSim Project

## Overview
This guide will get you up and running with the streamlined Drone Vision AirSim project in minutes.

## Prerequisites
- Python 3.8+
- Git
- AirSim (Windows/Linux)

## Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/drone-vision.git
cd drone-vision
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install AirSim
Follow the [AirSim installation guide](https://microsoft.github.io/AirSim/build_linux.html) for your platform.

### 4. Configure Settings
Edit `config/settings.json` with your AirSim connection details:
```json
{
  "airsim": {
    "host": "127.0.0.1",
    "port": 41451,
    "timeout": 10.0
  }
}
```

### 5. Setup Settings (one-time or when you change them)
```bash
# Copy settings to AirSim directory
mkdir -p ~/Documents/AirSim
cp config/settings.json ~/Documents/AirSim/settings.json
```

### 6. Run the Simulation
```bash
python -m src.main --mode=live
```

## Cloud Start-of-Day (GCP)

### Copy/Paste Commands for Daily Use:
```bash
# 0) Start GPU VM
gcloud compute instances start airsim-gpu --zone=us-central1-a

# 1) Start VNC on the VM
gcloud compute ssh airsim-gpu --zone=us-central1-a --command \
  "vncserver -kill :1 || true; vncserver :1 -localhost yes -geometry 1600x900 -depth 24 -xstartup /usr/bin/startxfce4"

# 2) Open SSH tunnel (keep this terminal open)
gcloud compute ssh airsim-gpu --zone=us-central1-a -- \
  -N -L 5901:localhost:5901 \
  -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3

# 3) In VNC desktop, launch Blocks
cd ~/airsim_env/LinuxBlocks1.8.1/LinuxNoEditor
./Blocks/Binaries/Linux/Blocks -opengl -windowed -ResX=1600 -ResY=900

# 4) Setup settings (first time)
mkdir -p ~/Documents/AirSim
cp -f ~/sim-drone/config/settings.json ~/Documents/AirSim/settings.json

# 5) Run smoke test (in VM terminal)
cd ~/sim-drone && git pull
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt
./scripts/airsim_takeoff.py

# 6) Run full mission
python -m src.main --mode=live
```

## Cloud End-of-Day:
```bash
# Stop AirSim + VNC on VM
pkill -f Blocks || true
vncserver -kill :1 || true

# Stop VM from laptop
gcloud compute instances stop airsim-gpu --zone=us-central1-a
```

## What Happens Next

The system will automatically:
1. Connect to AirSim
2. Take off to 20m altitude
3. Follow predefined patrol waypoints
4. Detect objects using computer vision
5. Land when mission completes

## Customization

### Modify Waypoints
Edit the patrol waypoints in `src/main.py`:
```python
patrol_waypoints = [
    (0, 0, 20),    # Start position
    (50, 0, 20),   # Forward
    (50, 50, 20),  # Right
    (0, 50, 20),   # Back
    (0, 0, 20),    # Return to start
]
```

### Adjust Vision Settings
Modify `config/settings.json`:
```json
{
  "vision": {
    "min_object_area": 100
  },
  "mission": {
    "target_detection_threshold": 0.7
  }
}
```

## Testing
```bash
pytest tests/
```

## Troubleshooting

### Connection Issues
- Ensure AirSim is running and accessible
- Check firewall settings
- Verify host/port in configuration

### Performance Issues
- Reduce image resolution in AirSim settings
- Adjust waypoint tolerance
- Check system resources

## Next Steps
- Read the [AirSim Setup Guide](airsim-setup-guide.md) for detailed installation
- Check the [Final Setup Summary](final-setup-summary.md) for advanced configuration
- Explore the codebase structure in the main README
