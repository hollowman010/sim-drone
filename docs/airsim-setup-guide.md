# AirSim Setup Guide for Remote Connection

## Overview
This guide explains how to set up AirSim on a Windows machine and connect it to your GCP Python simulation code.

## Prerequisites
- Windows 10/11 machine
- Epic Games account
- Unreal Engine 5.x
- Visual Studio 2019/2022 (for building AirSim)
- Git

## Step-by-Step Setup

### Step 1: Install Unreal Engine
1. Go to https://www.unrealengine.com/
2. Create Epic Games account
3. Download Epic Games Launcher
4. Install Unreal Engine 5.x (latest stable version)

### Step 2: Install Visual Studio
1. Download Visual Studio Community 2019/2022
2. Install with C++ development tools
3. Ensure Windows 10 SDK is included

### Step 3: Clone and Build AirSim
```bash
# Open Command Prompt as Administrator
git clone https://github.com/microsoft/AirSim.git
cd AirSim
build.cmd
```

### Step 4: Create Unreal Project
1. Open Unreal Engine
2. Create new project (C++ project recommended)
3. Add AirSim plugin to project
4. Build the project

### Step 5: Configure AirSim Settings
Create file: `Documents/AirSim/settings.json`
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

### Step 6: Configure Network Access
1. **Find your Windows IP address:**
   ```cmd
   ipconfig
   ```
   Note the IPv4 address (e.g., 192.168.1.100)

2. **Configure Windows Firewall:**
   - Allow Unreal Engine through firewall
   - Allow port 41451 for AirSim

3. **Test local connection:**
   - Start AirSim in Unreal Engine
   - Test with Python client locally first

### Step 7: Update GCP Configuration
1. **Update the remote configuration file:**
   ```bash
   # On GCP VM, edit config/remote_airsim.json
   # Replace YOUR_WINDOWS_IP_ADDRESS with actual IP
   ```

2. **Run with remote configuration:**
   ```bash
   # On GCP VM
   cd /home/medimonam/drone-vision
   source venv/bin/activate
   python src/main.py config/remote_airsim.json
   ```

## Troubleshooting

### Common Issues
1. **Connection Refused:**
   - Check Windows IP address
   - Verify firewall settings
   - Ensure AirSim is running

2. **Build Errors:**
   - Install Visual Studio C++ tools
   - Update Unreal Engine
   - Check AirSim compatibility

3. **Performance Issues:**
   - Reduce camera resolution
   - Use simpler environments
   - Consider GPU acceleration

### Network Configuration
- **Local Network:** Use local IP (192.168.x.x)
- **Internet:** Use public IP + port forwarding
- **VPN:** Use VPN IP address

## Alternative: Windows VM on GCP
If you prefer everything on GCP:

1. **Create Windows VM:**
   ```bash
   gcloud compute instances create airsim-windows \
     --zone=us-central1-a \
     --machine-type=n1-standard-8 \
     --image-family=windows-2019 \
     --image-project=windows-cloud \
     --boot-disk-size=100GB
   ```

2. **Install on Windows VM:**
   - Follow same steps as local Windows
   - Use RDP to connect to VM
   - Higher cost but everything in one place

## Cost Comparison
- **Local Windows + GCP:** ~$0.19/hour (GCP only)
- **Windows VM on GCP:** ~$0.50/hour (much more expensive)

## Next Steps
1. Set up AirSim on Windows
2. Test local connection
3. Configure network access
4. Update GCP configuration
5. Run full simulation

## Support
- AirSim Documentation: https://microsoft.github.io/AirSim/
- Unreal Engine Documentation: https://docs.unrealengine.com/
- GCP Documentation: https://cloud.google.com/docs

