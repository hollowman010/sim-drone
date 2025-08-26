# GPU VM Quick Start Guide

## 🎯 **Your Current Setup**
- **GPU Instance:** `airsim-gpu` (Spot VM)
- **Zone:** `us-central1-f`
- **GPU:** NVIDIA T4
- **Cost:** ~$0.35/hour (Spot pricing)

## 🚀 **Step 1: Install AirSim (Automated)**

Run the automated installation script:
```bash
python scripts/install_airsim_gpu.py
```

This will:
1. Install NVIDIA GPU drivers
2. Download and install AirSim
3. Install Python AirSim client
4. Create a test flight script

## 💰 **Step 2: Cost Management**

### **Check Costs:**
```bash
python scripts/gpu-vm-manager.py cost --hours 24
```

### **Stop VM when not using:**
```bash
python scripts/gpu-vm-manager.py stop
```

### **Start VM when needed:**
```bash
python scripts/gpu-vm-manager.py start
```

### **Check VM Status:**
```bash
python scripts/gpu-vm-manager.py status
```

## 🎮 **Step 3: Run AirSim**

### **Start AirSim (Terminal 1):**
```bash
# SSH to your GPU VM
gcloud compute ssh airsim-gpu --zone=us-central1-f

# Start AirSim
./Blocks/LinuxNoEditor/Blocks.sh -windowed
```

### **Run Test Flight (Terminal 2):**
```bash
# Open another SSH window
gcloud compute ssh airsim-gpu --zone=us-central1-f

# Run test flight
python3 hello_drone.py
```

## 🔧 **Step 4: Connect Your Python Code**

### **Update Configuration:**
Edit `config/spot_airsim.json` with your GPU VM IP:
```bash
# Get GPU VM IP
python scripts/gpu-vm-manager.py ip

# Update config file with the IP
```

### **Run Your Simulation:**
```bash
# On your CPU VM (development environment)
python src/main.py config/spot_airsim.json
```

## 📊 **Cost Comparison**

| Instance | Purpose | Cost/Hour | Monthly (24/7) |
|----------|---------|-----------|----------------|
| **airsim-gpu** | AirSim + GPU | ~$0.35 | ~$255 |
| **drone-sim-dev** | Development | ~$0.19 | ~$139 |
| **Total** | Complete Setup | ~$0.54 | ~$394 |

## 💡 **Cost Optimization Tips**

### **Automated Shutdown:**
```bash
# Stop GPU VM at 10 PM daily
echo "0 22 * * * python scripts/gpu-vm-manager.py stop" | crontab -

# Start GPU VM at 8 AM daily
echo "0 8 * * * python scripts/gpu-vm-manager.py start" | crontab -
```

### **Manual Management:**
```bash
# Start when working
python scripts/gpu-vm-manager.py start

# Stop when done
python scripts/gpu-vm-manager.py stop
```

## 🆘 **Troubleshooting**

### **Check GPU Status:**
```bash
python scripts/gpu-vm-manager.py check-gpu
```

### **Check VM Status:**
```bash
python scripts/gpu-vm-manager.py status
```

### **Get VM IP:**
```bash
python scripts/gpu-vm-manager.py ip
```

## 🎯 **Workflow Summary**

1. **Start GPU VM:** `python scripts/gpu-vm-manager.py start`
2. **Install AirSim:** `python scripts/install_airsim_gpu.py`
3. **Start AirSim:** SSH to VM and run `./Blocks/LinuxNoEditor/Blocks.sh -windowed`
4. **Run Your Code:** On CPU VM, run `python src/main.py config/spot_airsim.json`
5. **Stop GPU VM:** `python scripts/gpu-vm-manager.py stop`

## ⚠️ **Important Notes**

- **Spot VM:** Can be terminated with 30 seconds notice
- **Cost:** ~$0.35/hour when running
- **Backup:** Keep CPU VM for development and testing
- **Data:** Use persistent disks for important data

## 🎉 **You're Ready!**

Your GPU VM is set up and ready for AirSim development. The automated scripts handle installation and cost management, so you can focus on your drone simulation!
