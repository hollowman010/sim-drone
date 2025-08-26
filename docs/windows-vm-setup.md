# Windows VM Setup on GCP for AirSim

## Overview
This guide covers setting up a Windows VM on GCP to run AirSim, since you don't have a local Windows machine.

## Cost Analysis

### Monthly Costs (24/7 usage)
| Configuration | Hourly Cost | Monthly Cost |
|---------------|-------------|--------------|
| CPU Only (n1-standard-8) | $0.55 | $401.50 |
| With GPU (NVIDIA T4) | $0.90 | $657.00 |
| Preemptible CPU Only | $0.22 | $160.60 |
| Preemptible with GPU | $0.36 | $262.80 |

### Cost Optimization
1. **Scheduled Usage (8 hours/day):**
   - CPU Only: ~$134/month
   - With GPU: ~$219/month

2. **Preemptible Instances:**
   - 60-80% cost reduction
   - Less reliable but much cheaper

3. **Spot Instances:**
   - Even cheaper than preemptible
   - Highest risk of interruption

## Step 1: Create Windows VM

### Option A: CPU Only (Recommended to start)
```bash
gcloud compute instances create airsim-windows \
  --zone=us-central1-a \
  --machine-type=n1-standard-8 \
  --image-family=windows-2019 \
  --image-project=windows-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --network-interface=network-tier=PREMIUM,subnet=default \
  --maintenance-policy=MIGRATE \
  --provisioning-model=STANDARD \
  --service-account=YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --create-disk=auto-delete=yes,boot=yes,device-name=airsim-windows,image=projects/windows-cloud/global/images/family/windows-2019,mode=rw,size=100,type=projects/YOUR_PROJECT/zones/us-central1-a/diskTypes/pd-ssd \
  --no-shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --reservation-affinity=any
```

### Option B: With GPU (After quota approval)
```bash
gcloud compute instances create airsim-windows-gpu \
  --zone=us-central1-a \
  --machine-type=n1-standard-8 \
  --image-family=windows-2019 \
  --image-project=windows-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --maintenance-policy=TERMINATE \
  --provisioning-model=STANDARD \
  --service-account=YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --create-disk=auto-delete=yes,boot=yes,device-name=airsim-windows-gpu,image=projects/windows-cloud/global/images/family/windows-2019,mode=rw,size=100,type=projects/YOUR_PROJECT/zones/us-central1-a/diskTypes/pd-ssd \
  --no-shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --reservation-affinity=any
```

## Step 2: Connect to Windows VM

### Get RDP Connection Details
```bash
gcloud compute instances get-serial-port-output airsim-windows --zone=us-central1-a
```

### Connect via RDP
1. **On MacBook:** Use Microsoft Remote Desktop app
2. **Download:** https://apps.apple.com/us/app/microsoft-remote-desktop/id1295203466
3. **Connect to:** `EXTERNAL_IP:3389`

### Alternative: Use Chrome RDP
1. Go to GCP Console
2. Navigate to Compute Engine > VM instances
3. Click "RDP" button next to your instance

## Step 3: Install Required Software

### Install Visual Studio 2019/2022
1. Download Visual Studio Community
2. Install with C++ development tools
3. Include Windows 10 SDK

### Install Unreal Engine
1. Create Epic Games account
2. Download Epic Games Launcher
3. Install Unreal Engine 5.x

### Install Git
1. Download Git for Windows
2. Install with default settings

## Step 4: Build AirSim

### Clone AirSim Repository
```cmd
git clone https://github.com/microsoft/AirSim.git
cd AirSim
```

### Build AirSim
```cmd
build.cmd
```

### Create Unreal Project
1. Open Unreal Engine
2. Create new C++ project
3. Add AirSim plugin
4. Build project

## Step 5: Configure AirSim

### Create Settings File
Create: `Documents/AirSim/settings.json`
```json
{
  "SettingsVersion": 1.2,
  "SimMode": "ComputerVision",
  "Vehicles": {
    "Drone1": {
      "VehicleType": "SimpleFlight",
      "X": 0,
      "Y": 0,
      "Z": -2
    }
  },
  "Recording": {
    "RecordOnMove": false,
    "RecordInterval": 0.05
  },
  "CameraDefaults": {
    "CaptureSettings": [
      {
        "ImageType": 0,
        "Width": 256,
        "Height": 144
      },
      {
        "ImageType": 1,
        "Width": 256,
        "Height": 144
      },
      {
        "ImageType": 2,
        "Width": 256,
        "Height": 144
      }
    ]
  }
}
```

## Step 6: Configure Network Access

### Get Windows VM IP
```cmd
ipconfig
```

### Configure Windows Firewall
1. Allow Unreal Engine through firewall
2. Allow port 41451 for AirSim

### Update GCP Firewall Rules
```bash
gcloud compute firewall-rules create airsim-rule \
  --allow tcp:41451 \
  --source-ranges=0.0.0.0/0 \
  --description="Allow AirSim connections"
```

## Step 7: Connect from GCP Linux VM

### Update Configuration
Edit `config/remote_airsim.json`:
```json
{
  "airsim": {
    "host": "WINDOWS_VM_EXTERNAL_IP",
    "port": 41451,
    "timeout": 10.0
  }
}
```

### Run Simulation
```bash
# On GCP Linux VM
cd /home/medimonam/drone-vision
source venv/bin/activate
python src/main.py config/remote_airsim.json
```

## Cost Management

### Automated Shutdown Script
Create `scripts/windows-vm-manager.py`:
```python
#!/usr/bin/env python3
import subprocess
import time
import logging

def stop_windows_vm():
    """Stop Windows VM to save costs."""
    subprocess.run([
        'gcloud', 'compute', 'instances', 'stop', 'airsim-windows',
        '--zone=us-central1-a'
    ])

def start_windows_vm():
    """Start Windows VM."""
    subprocess.run([
        'gcloud', 'compute', 'instances', 'start', 'airsim-windows',
        '--zone=us-central1-a'
    ])

def get_vm_status():
    """Get VM status."""
    result = subprocess.run([
        'gcloud', 'compute', 'instances', 'describe', 'airsim-windows',
        '--zone=us-central1-a', '--format=value(status)'
    ], capture_output=True, text=True)
    return result.stdout.strip()
```

### Scheduled Operations
```bash
# Create cron job to stop VM at night
echo "0 22 * * * /usr/bin/python3 /home/medimonam/drone-vision/scripts/windows-vm-manager.py stop" | crontab -

# Create cron job to start VM in morning
echo "0 8 * * * /usr/bin/python3 /home/medimonam/drone-vision/scripts/windows-vm-manager.py start" | crontab -
```

## Troubleshooting

### Common Issues
1. **RDP Connection Failed:**
   - Check firewall rules
   - Verify VM is running
   - Try Chrome RDP instead

2. **AirSim Build Errors:**
   - Install Visual Studio C++ tools
   - Update Unreal Engine
   - Check compatibility

3. **Network Connection Issues:**
   - Verify IP addresses
   - Check firewall settings
   - Test with ping

### Performance Optimization
1. **GPU Acceleration:**
   - Request GPU quota increase
   - Use NVIDIA T4 or V100
   - Install proper drivers

2. **Memory Optimization:**
   - Close unnecessary applications
   - Reduce camera resolution
   - Use simpler environments

## Next Steps
1. Create Windows VM (start with CPU only)
2. Install required software
3. Build and configure AirSim
4. Test connection from Linux VM
5. Implement cost management
6. Run full simulation

## Support Resources
- GCP Windows VM Documentation: https://cloud.google.com/compute/docs/instances/windows
- AirSim Documentation: https://microsoft.github.io/AirSim/
- Unreal Engine Documentation: https://docs.unrealengine.com/
