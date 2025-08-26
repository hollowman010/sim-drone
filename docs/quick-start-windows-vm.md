# Quick Start: Windows VM for AirSim on GCP

## 🚀 **Step 1: Create Windows VM (CPU Only - Recommended)**

```bash
# Replace YOUR_PROJECT_ID with your actual project ID
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
  --scopes=https://www.googleapis.com/auth/cloud-platform
```

## 🔗 **Step 2: Connect to Windows VM**

### Option A: Microsoft Remote Desktop (Recommended)
1. Download Microsoft Remote Desktop from Mac App Store
2. Get VM IP: `python scripts/windows-vm-manager.py ip`
3. Connect to: `EXTERNAL_IP:3389`

### Option B: Chrome RDP
1. Go to GCP Console > Compute Engine > VM instances
2. Click "RDP" button next to your instance

## 💰 **Step 3: Check Costs**

```bash
# Check daily cost
python scripts/windows-vm-manager.py cost --hours 24

# Check monthly cost
python scripts/windows-vm-manager.py cost --hours 730
```

## ⚙️ **Step 4: Install Software on Windows VM**

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

## 🔧 **Step 5: Build AirSim**

```cmd
# On Windows VM
git clone https://github.com/microsoft/AirSim.git
cd AirSim
build.cmd
```

## 📁 **Step 6: Configure AirSim**

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

## 🌐 **Step 7: Configure Network**

### On Windows VM
```cmd
# Get IP address
ipconfig

# Configure firewall to allow port 41451
```

### On GCP (from your local machine)
```bash
# Create firewall rule
gcloud compute firewall-rules create airsim-rule \
  --allow tcp:41451 \
  --source-ranges=0.0.0.0/0 \
  --description="Allow AirSim connections"
```

## 🎮 **Step 8: Test Connection**

### On Windows VM
1. Start Unreal Engine
2. Open your AirSim project
3. Start the simulation

### On GCP Linux VM
```bash
# Get Windows VM IP
python scripts/windows-vm-manager.py ip

# Update configuration
# Edit config/remote_airsim.json with the Windows VM IP

# Test connection
python src/main.py config/remote_airsim.json
```

## 💡 **Cost Management**

### Start/Stop VM
```bash
# Start VM
python scripts/windows-vm-manager.py start

# Stop VM (save costs)
python scripts/windows-vm-manager.py stop

# Check status
python scripts/windows-vm-manager.py status
```

### Automated Scheduling
```bash
# Stop VM at 10 PM daily
echo "0 22 * * * python scripts/windows-vm-manager.py stop" | crontab -

# Start VM at 8 AM daily
echo "0 8 * * * python scripts/windows-vm-manager.py start" | crontab -
```

## 📊 **Cost Estimates**

| Usage Pattern | Monthly Cost |
|---------------|--------------|
| 24/7 (CPU only) | ~$401 |
| 8 hours/day (CPU only) | ~$134 |
| 24/7 with GPU | ~$657 |
| 8 hours/day with GPU | ~$219 |

## 🆘 **Troubleshooting**

### Common Issues
1. **RDP Connection Failed:**
   - Check if VM is running: `python scripts/windows-vm-manager.py status`
   - Try Chrome RDP instead

2. **AirSim Build Errors:**
   - Install Visual Studio C++ tools
   - Update Unreal Engine

3. **Network Issues:**
   - Check firewall rules
   - Verify IP addresses

### Get Help
```bash
# Check VM status
python scripts/windows-vm-manager.py status

# Get external IP
python scripts/windows-vm-manager.py ip

# Estimate costs
python scripts/windows-vm-manager.py cost
```

## 🎯 **Next Steps**
1. Create Windows VM
2. Install required software
3. Build AirSim
4. Configure network
5. Test connection
6. Run full simulation
7. Implement cost management
