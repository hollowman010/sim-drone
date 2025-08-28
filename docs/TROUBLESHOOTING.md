# Troubleshooting

## Can't SSH: "Connection refused"
- On the VM console: `sudo systemctl status ssh`; if needed `sudo systemctl restart ssh`.
- Guest agent healthy? `systemctl status google-guest-agent`.

## VNC connects but desktop is black
- Kill & restart: `vncserver -kill :1 || true && vncserver :1 -localhost yes -geometry 1600x900 -depth 24 -xstartup /usr/bin/startxfce4`.

## AirSim doesn't expose RPC
- Ensure the game window is actually running (Blocks is visible).
- `~/Documents/AirSim/settings.json` contains `"SimMode": "Multirotor", "ApiServerPort": 41451`.
- From Python, test:
  ```python
  import airsim; c=airsim.MultirotorClient(); c.confirmConnection(); print(c.ping())
  ```

## Drone doesn't move

**You're still in demo mode.** Run with `RUN_MODE=live`.

In code, call:
```python
client.enableApiControl(True); client.armDisarm(True)
client.takeoffAsync(timeout_sec=30).join()
client.moveToZAsync(-5, 1).join()
```

## Port/Connection Issues

**AirSim RPC not available:**
- Check if Blocks is actually running: `pgrep -f Blocks`
- Verify settings: `cat ~/Documents/AirSim/settings.json`
- Test connection: `ss -tlnp | grep 41451`

**VNC tunnel issues:**
- Ensure VNC server is running: `vncserver -list`
- Check tunnel on laptop: `netstat -an | grep 5901`
- Restart tunnel with correct options

## Performance Issues

**Slow VNC/Graphics:**
- Use `-opengl` instead of `-vulkan` for stability
- Lower resolution: `-ResX=1280 -ResY=720`
- Check GPU usage: `nvidia-smi`

**Python import errors:**
- Ensure virtual environment is activated: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Check Python path: `python -c "import sys; print(sys.path)"`

## Common Environment Variables

Set these for consistent behavior:

```bash
export RUN_MODE=live          # or "demo"
export AIRSIM_HOST=127.0.0.1  # AirSim server
export AIRSIM_PORT=41451      # AirSim RPC port
export PYTHONUNBUFFERED=1     # See output immediately
```

## Debug Commands

Check system status:
```bash
# GPU status
nvidia-smi

# VNC status  
vncserver -list
ss -tlnp | grep 5901

# AirSim status
ss -tlnp | grep 41451
pgrep -fa Blocks

# Python environment
which python
pip list | grep airsim
```
