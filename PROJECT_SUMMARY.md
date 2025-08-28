# Drone Vision AirSim Project - Complete Summary

## 🎯 Project Purpose & Goals

This is a **cloud-based drone simulation system** built on Google Cloud Platform (GCP) using Microsoft AirSim for realistic UAV (Unmanned Aerial Vehicle) simulation. The project enables:

- **Autonomous drone control** with waypoint navigation and patrol missions
- **Computer vision processing** for object detection and targeting
- **Cost-optimized cloud deployment** using GPU and CPU VMs strategically
- **Remote simulation capabilities** without requiring local AirSim installation

### High-Level Objectives:
1. **Realistic Drone Simulation**: Full physics-based drone control using AirSim
2. **Cloud-First Architecture**: No local dependencies, everything runs on GCP
3. **Cost Optimization**: Smart VM management to minimize cloud costs
4. **Vision Processing**: Real-time image analysis for autonomous navigation
5. **Mission Logic**: Autonomous patrol and target detection capabilities

## 🏗️ Current Architecture

### **Core Components:**

#### 1. **Simulation Engine**
- **Platform**: Microsoft AirSim 1.8.1 on Unreal Engine
- **Environment**: Blocks environment (prebuilt Linux binary)
- **Location**: GPU VM with NVIDIA Tesla T4
- **Access**: VNC desktop for visual interface

#### 2. **Python Codebase** (`src/`)
```
src/
├── main.py              # Main simulation orchestrator
├── flight_control.py    # AirSim drone controller (with mock fallback)
├── mission_logic.py     # Autonomous mission planning and execution
├── vision_targeting.py  # Computer vision processing for images
└── utils/
    ├── config.py        # Configuration management
    └── __init__.py      # Module exports
```

#### 3. **Cloud Infrastructure** (`scripts/`)
```
scripts/
├── gpu-vm-manager.py     # NVIDIA T4 GPU VM management
├── cpu-vm-manager.py     # CPU VM management for processing
├── cost-optimizer.py     # Cross-VM cost optimization
├── airsim_takeoff.py     # AirSim connectivity test script
└── quick_settings.json   # Minimal AirSim configuration
```

#### 4. **Configuration** (`config/`)
```
config/
├── gpu_vm.json          # GPU VM specifications (NVIDIA T4)
├── cpu_vm.json          # CPU VM specifications
├── remote_airsim.json   # Remote AirSim connection settings
└── spot_airsim.json     # Spot instance configuration
```

## 💰 Cost Management Strategy

### **VM Architecture:**
- **GPU VM (`airsim-gpu`)**: 
  - Instance: `n1-standard-4` with NVIDIA Tesla T4
  - Purpose: AirSim simulation, complex rendering
  - Zone: `us-central1-a`
  - Note: Uses preemptible instances for cost savings

- **CPU VM (`drone-sim-dev`)**: 
  - Instance: `n1-standard-4` (CPU only)
  - Purpose: Data processing, model training, batch work
  - Zone: `us-central1-a`
  - Note: Uses preemptible instances for cost savings

*For current pricing, consult the [GCP Pricing Calculator](https://cloud.google.com/products/calculator) with your specific instance configurations.*

### **Cost Optimization Features:**
1. **Automated Start/Stop**: VMs only run when needed
2. **Workload-Based Allocation**: 
   - GPU for AirSim simulation
   - CPU for data processing
3. **Spot Instance Support**: Additional cost savings option
4. **Cost Monitoring**: Real-time cost tracking and budgets
5. **Auto-shutdown**: Configurable runtime limits

### **Cost Management Commands:**
```bash
# Get cost summary
python scripts/cost-optimizer.py cost

# Optimize for AirSim workload (start GPU + CPU)
python scripts/cost-optimizer.py airsim

# Optimize for processing only (stop GPU, start CPU)
python scripts/cost-optimizer.py processing

# Shutdown all VMs
python scripts/cost-optimizer.py shutdown

# Get VM IPs
python scripts/cost-optimizer.py ips
```

## 🚁 Simulation Capabilities

### **Current Features:**

#### 1. **Drone Control**
- **Connection**: Connects to AirSim RPC server (port 41451)
- **Control**: Full API control with arming/disarming
- **Navigation**: Waypoint navigation, velocity control, hover
- **Sensors**: RGB camera data collection
- **Safety**: Automated takeoff, landing, and emergency procedures

#### 2. **Mission Logic**
- **Patrol System**: Autonomous waypoint-based patrol
- **Target Detection**: Computer vision-based object detection
- **State Management**: Clean mission state handling
- **Completion**: Automatic mission completion and landing

#### 3. **Vision Processing**
- **Input**: RGB images from AirSim cameras
- **Processing**: Real-time image analysis
- **Output**: Target detection and navigation guidance
- **Format**: Handles both compressed and uncompressed image data

#### 4. **Mock Testing**
- **Fallback System**: Automatic mock mode when AirSim unavailable
- **Local Development**: Test logic without full AirSim setup
- **Realistic Data**: Mock provides realistic sensor data

## 🛠️ Technical Implementation

### **Dependencies:**
```
airsim==1.8.1           # Core AirSim client (pinned to match server)
numpy>=1.24.0           # Numerical operations
opencv-python>=4.8.0    # Computer vision
google-auth>=2.17.0     # GCP authentication
google-cloud-compute    # GCP VM management
msgpack-rpc-python      # AirSim communication
requests, pyyaml        # Utilities
```

### **Key Technologies:**
- **Language**: Python 3.10+
- **Simulation**: Microsoft AirSim 1.8.1
- **Cloud**: Google Cloud Platform
- **Graphics**: NVIDIA CUDA with Vulkan/OpenGL
- **Networking**: RPC over TCP (port 41451)
- **Desktop**: XFCE4 via TigerVNC
- **Security**: UFW firewall enabled, VNC localhost-only

## 🔧 Current Setup & Deployment

### **GCP Project Configuration:**
- **Project ID**: `drone-sim-project`
- **Zone**: `us-central1-a`
- **GPU VM**: `airsim-gpu` (currently STOPPED for cost savings)
- **CPU VM**: `drone-sim-dev` (currently STOPPED)

### **Deployment Status:**
✅ **Code Deployed**: Latest codebase on GPU VM  
✅ **AirSim Installed**: Blocks environment ready  
✅ **VNC Configured**: Desktop access via port 5901  
✅ **Dependencies**: All Python packages installed  
✅ **Configuration**: Settings and connections configured  
✅ **Testing**: Connection test scripts ready  

### **Ready-to-Run Commands:**

#### **Start Session:**
```bash
# Start GPU VM
gcloud compute instances start airsim-gpu --zone=us-central1-a

# SSH to VM
gcloud compute ssh airsim-gpu --zone=us-central1-a

# Start VNC server (on VM) - localhost only for security
vncserver :1 -localhost yes -geometry 1600x900 -depth 24 -xstartup /usr/bin/startxfce4

# Open VNC tunnel (local machine) - stable connection
gcloud compute ssh airsim-gpu --zone=us-central1-a -- \
  -N -L 5901:localhost:5901 \
  -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3

# Connect VNC viewer to localhost:5901 (use your VNC password)
```

#### **Run Simulation:**
```bash
# VM prep
cd ~/sim-drone && git pull
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -U pip wheel && pip install -r requirements.txt
scripts/ensure_settings.sh

# Start VNC + AirSim Blocks
scripts/start_session.sh

# Smoke test control
python scripts/airsim_takeoff.py

# Full run
python src/main.py
```

#### **End Session:**
```bash
# Stop AirSim and VNC (on VM)
scripts/stop_session.sh

# Stop VM (local machine)
gcloud compute instances stop airsim-gpu --zone=us-central1-a
```

## 📊 Current Status & Next Steps

### **What's Working:**
✅ Complete cloud infrastructure deployed  
✅ AirSim installed and tested  
✅ Python simulation code deployed  
✅ Cost optimization system functional  
✅ VNC desktop environment ready  
✅ Mock testing system for development  
✅ Git repository with all components  

### **Immediate Next Actions:**
1. **Test Full Integration**: Run complete simulation on cloud AirSim
2. **Validate Vision Pipeline**: Ensure camera data processing works
3. **Mission Testing**: Test autonomous patrol and target detection
4. **Performance Optimization**: Fine-tune simulation parameters
5. **Documentation**: Create user guides for operation

### **Network Configuration Notes:**
- Current setup runs both AirSim and Python client on same GPU VM
- For cross-VM setup (CPU VM → GPU VM), enable AirSim port:
  ```bash
  # On GPU VM (if needed for cross-VM communication)
  sudo ufw allow from 10.128.0.0/9 to any port 41451 proto tcp
  sudo ufw reload
  ```

### **Architecture Benefits:**
- **No Local Dependencies**: Everything runs in cloud
- **Cost Efficient**: Pay only when running simulations
- **Scalable**: Can add more VMs or upgrade instances
- **Visual**: VNC provides real-time simulation viewing
- **Robust**: Mock system allows development without cloud costs
- **Professional**: Production-ready cloud architecture

## 🎯 Project Context

This project enables **realistic drone simulation** and **autonomous control development** without requiring expensive local hardware or complex AirSim installations. The cloud-first approach makes it accessible while the cost optimization ensures it remains economical for development and testing.

The system is designed for **UAV research**, **autonomous navigation development**, and **computer vision applications** in a realistic physics-based simulation environment.

---

**Ready State**: The entire system is deployed and ready for immediate use. Simply start the VMs, launch AirSim, and begin simulation work.
