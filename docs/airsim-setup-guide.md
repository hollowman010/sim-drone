# AirSim Setup Guide

## Overview
This guide explains how to set up AirSim for the Drone Vision project.

## Prerequisites
- Windows 10/11 or Linux
- Epic Games account (for Unreal Engine)
- Unreal Engine 5.x
- Git

## Installation Steps

### Step 1: Install Unreal Engine
1. Go to https://www.unrealengine.com/
2. Create Epic Games account
3. Download Epic Games Launcher
4. Install Unreal Engine 5.x (latest stable version)

### Step 2: Install AirSim

#### Option A: Pre-built Binaries (Recommended)
1. Download AirSim binaries from [releases](https://github.com/microsoft/AirSim/releases)
2. Extract to your Unreal project

#### Option B: Build from Source
```bash
# Clone AirSim
git clone https://github.com/microsoft/AirSim.git
cd AirSim

# Build (Windows)
build.cmd

# Build (Linux)
./build.sh
```

### Step 3: Create Unreal Project
1. Open Unreal Engine
2. Create new project (C++ project recommended)
3. Add AirSim plugin to project
4. Build the project

### Step 4: Configure AirSim Settings
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
        "Width": 640,
        "Height": 480
      }
    ]
  }
}
```

### Step 5: Test Connection
1. Start AirSim in Unreal Engine
2. Test with Python client:
```python
import airsim
client = airsim.MultirotorClient()
client.confirmConnection()
print("Connected to AirSim!")
```

## Configuration

### Network Settings
For remote connections, update your project's `config/settings.json`:
```json
{
  "airsim": {
    "host": "YOUR_AIRSIM_IP",
    "port": 41451,
    "timeout": 10.0
  }
}
```

### Performance Optimization
- Reduce image resolution for better performance
- Adjust camera settings based on your needs
- Use headless mode for cloud deployment

## Troubleshooting

### Common Issues
1. **Connection Refused**: Check if AirSim is running
2. **Plugin Not Found**: Ensure AirSim plugin is properly installed
3. **Build Errors**: Install Visual Studio with C++ tools (Windows)

### Performance Tips
- Use lower resolution images for faster processing
- Reduce simulation frequency if needed
- Close unnecessary applications

## Next Steps
- Run the [Quick Start Guide](quick-start.md)
- Check the [Final Setup Summary](final-setup-summary.md)
- Explore the main README for project structure

