# Quick Start (Cloud, GCP)

This gets you from **powered-off VM** to **drone flying in AirSim**.

## Prereqs
- `gcloud` installed & logged in (`gcloud auth login`, `gcloud config set project drone-sim-project`)
- GPU quota for T4 in `us-central1-a`

## Start the GPU VM + Desktop
```bash
gcloud compute instances start airsim-gpu --zone=us-central1-a
gcloud compute ssh airsim-gpu --zone=us-central1-a
vncserver -kill :1 || true
vncpasswd    # set your secret; not stored in repo
vncserver :1 -localhost yes -geometry 1600x900 -depth 24 -xstartup /usr/bin/startxfce4
```

## Open the VNC tunnel from your laptop

In a separate terminal on your laptop:

```bash
gcloud compute ssh airsim-gpu --zone=us-central1-a -- -N -L 5901:localhost:5901 -o ExitOnForwardFailure=yes
```

Then open your VNC viewer to `localhost:5901`.

## Launch AirSim (inside VNC)

Open a terminal in the XFCE desktop:

```bash
cd ~/airsim_env/LinuxBlocks1.8.1/LinuxNoEditor
./Blocks/Binaries/Linux/Blocks -opengl -windowed -ResX=1600 -ResY=900 -NoSplash
```

Wait until you see the quadcopter.

## Run your code (live mode)

Open another terminal (can be SSH or within VNC):

```bash
cd ~/sim-drone
git pull  # get latest code
source .venv/bin/activate
pip install -r requirements.txt
scripts/run_live.sh
```

You should see the drone take off to ~5 m and begin your mission.

## Shutdown (to save costs)
```bash
pkill -f Blocks || true
vncserver -kill :1 || true
exit  # if you're inside SSH to the VM
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
