# 🖥️ AirSim Visualization Guide

## 🎯 **How to See Your AirSim Simulation**

There are several ways to view your AirSim simulation running on the GPU VM:

---

## 🖥️ **Option 1: VNC Remote Desktop (Recommended)**

### **Step 1: Start AirSim with VNC**
```bash
# SSH to your GPU VM
gcloud compute ssh airsim-gpu --zone=us-central1-a

# Start AirSim with VNC support
./start_airsim_with_vnc.sh
```

### **Step 2: Create SSH Tunnel**
```bash
# On your local machine, create SSH tunnel
ssh -L 5900:localhost:5900 medimonam@35.192.89.122
```

### **Step 3: Connect with VNC Client**
1. **Download VNC Viewer:** [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/)
2. **Connect to:** `localhost:5900`
3. **You'll see:** Full AirSim interface with 3D environment

---

## 🖼️ **Option 2: Screenshot Capture**

### **Capture Screenshots from Python**
```python
import airsim
import cv2

# Connect to AirSim
client = airsim.MultirotorClient()
client.confirmConnection()

# Get camera image
responses = client.simGetImages([
    airsim.ImageRequest("0", airsim.ImageType.Scene),
    airsim.ImageRequest("1", airsim.ImageType.DepthVis)
])

# Save images
for i, response in enumerate(responses):
    if response.pixels_as_float:
        # Depth image
        airsim.write_pfm('depth.pfm', airsim.get_pfm_array(response))
    else:
        # RGB image
        airsim.write_file(f'image_{i}.png', response.image_data_uint8)
```

---

## 📊 **Option 3: Real-time Data Visualization**

### **View Telemetry Data**
```python
import airsim
import time

client = airsim.MultirotorClient()
client.confirmConnection()

while True:
    # Get drone state
    state = client.getMultirotorState()
    
    print(f"Position: {state.kinematics_estimated.position}")
    print(f"Velocity: {state.kinematics_estimated.linear_velocity}")
    print(f"Orientation: {state.kinematics_estimated.orientation}")
    print("---")
    
    time.sleep(1)
```

---

## 🎮 **Option 4: Web Interface (Advanced)**

### **Create a Simple Web Dashboard**
```python
# Install Flask
pip install flask

# Create web interface
from flask import Flask, render_template
import airsim

app = Flask(__name__)

@app.route('/')
def dashboard():
    client = airsim.MultirotorClient()
    state = client.getMultirotorState()
    
    return f"""
    <h1>AirSim Dashboard</h1>
    <p>Position: {state.kinematics_estimated.position}</p>
    <p>Velocity: {state.kinematics_estimated.linear_velocity}</p>
    <p>Battery: {state.battery_level}%</p>
    """
```

---

## 🚀 **Quick Start: See AirSim Right Now**

### **1. Start AirSim with VNC**
```bash
# SSH to GPU VM
gcloud compute ssh airsim-gpu --zone=us-central1-a

# Start AirSim with display
./start_airsim_with_vnc.sh
```

### **2. Create Tunnel (New Terminal)**
```bash
# Create SSH tunnel for VNC
ssh -L 5900:localhost:5900 medimonam@35.192.89.122
```

### **3. Connect VNC Client**
- **Download:** [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/)
- **Connect to:** `localhost:5900`
- **You'll see:** Full AirSim 3D environment!

---

## 🎯 **What You'll See**

### **AirSim Interface:**
- **3D Environment:** Blocks world with buildings and obstacles
- **Drone View:** First-person camera from the drone
- **HUD:** Telemetry data, controls, and status
- **Settings:** Graphics, physics, and simulation options

### **Available Views:**
- **Scene Camera:** Main RGB camera view
- **Depth Camera:** Distance information
- **Segmentation:** Object classification
- **Surface Normals:** Surface orientation data

---

## 🔧 **Troubleshooting**

### **VNC Connection Issues:**
```bash
# Check if VNC is running
ps aux | grep x11vnc

# Restart VNC server
pkill x11vnc
x11vnc -display :0 -nopw -listen localhost -xkb -ncache 10 -ncache_cr -forever &
```

### **Display Issues:**
```bash
# Check display
echo $DISPLAY

# Set display manually
export DISPLAY=:0
```

### **AirSim Not Starting:**
```bash
# Check GPU
nvidia-smi

# Check AirSim logs
./Blocks/LinuxNoEditor/Blocks.sh -log
```

---

## 💡 **Pro Tips**

### **For Best Performance:**
1. **Use VNC Option 1** for full GUI access
2. **Lower resolution** if connection is slow
3. **Use screenshots** for documentation
4. **Monitor GPU usage** with `nvidia-smi`

### **For Development:**
1. **Use Python API** for automated testing
2. **Save images** for computer vision development
3. **Log telemetry** for analysis
4. **Use web dashboard** for monitoring

---

## 🎉 **You're Ready to See AirSim!**

Choose the visualization method that works best for you:

- **🖥️ VNC:** Full GUI access (recommended)
- **📸 Screenshots:** For documentation and CV
- **📊 Telemetry:** For data analysis
- **🌐 Web:** For remote monitoring

**Start with Option 1 (VNC) for the best experience!** 🚁
