# Cost-Effective AirSim Setup: Spot VM + Pre-compiled Binaries

## 🎯 **Strategy Overview**
This approach uses **Spot VMs** (60-91% discount) with **pre-compiled AirSim binaries** to achieve maximum cost-effectiveness while avoiding complex compilation.

## 💰 **Cost Analysis**

### **Spot VM Pricing (Estimated)**
| Configuration | On-Demand/Hour | Spot/Hour | Monthly (24/7) |
|---------------|----------------|-----------|-----------------|
| n1-standard-4 + T4 GPU | ~$0.90 | ~$0.15-0.30 | ~$50-100 |
| n1-standard-8 + T4 GPU | ~$1.25 | ~$0.25-0.50 | ~$80-150 |

### **Cost Savings**
- **75-87% cost reduction** compared to on-demand pricing
- **80-90% cost reduction** compared to Windows VM approach
- **Perfect for development and testing**

## 🚀 **Step-by-Step Implementation**

### **Step 1: Request GPU Quota**

```bash
# Check current quota
gcloud compute regions describe us-central1 --format="value(quotas[].limit,quotas[].usage,quotas[].metric)"

# Request quota increase via GCP Console:
# 1. Go to IAM & Admin > Quotas
# 2. Filter for "Compute Engine API"
# 3. Search for "Preemptible NVIDIA T4 GPUs"
# 4. Request limit of 1
# 5. Reason: "Running AirSim drone simulations"
```

### **Step 2: Create Spot VM with GPU**

```bash
# Create cost-effective Spot VM
gcloud compute instances create airsim-spot \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --maintenance-policy=TERMINATE \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --metadata=install-nvidia-driver=true \
  --metadata-from-file=startup-script=scripts/airsim-setup.sh
```

### **Step 3: Create Startup Script**

Create `scripts/airsim-setup.sh`:
```bash
#!/bin/bash

# Update system
apt-get update
apt-get install -y wget unzip python3 python3-pip git

# Install NVIDIA drivers (if not already installed)
if ! command -v nvidia-smi &> /dev/null; then
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
    curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    apt-get update
    apt-get install -y nvidia-container-toolkit
fi

# Install Python dependencies
pip3 install airsim opencv-python numpy

# Download pre-compiled AirSim environments
mkdir -p /opt/airsim
cd /opt/airsim

# Download Blocks environment (small, good for testing)
wget -O Blocks.zip https://github.com/Microsoft/AirSim/releases/download/v1.6.0-linux/Blocks.zip
unzip -o Blocks.zip

# Download other environments as needed
# wget -O Neighborhood.zip https://github.com/Microsoft/AirSim/releases/download/v1.6.0-linux/Neighborhood.zip
# unzip -o Neighborhood.zip

# Set up display for headless operation
export DISPLAY=:0
Xvfb :0 -screen 0 1024x768x24 &
```

### **Step 4: Create VM Management Script**

Create `scripts/spot-vm-manager.py`:
```python
#!/usr/bin/env python3
"""
Spot VM Manager for AirSim on GCP
Optimized for cost-effective simulation development.
"""

import subprocess
import time
import logging
import sys
import argparse
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpotVMManager:
    def __init__(self, instance_name: str = "airsim-spot", zone: str = "us-central1-a"):
        self.instance_name = instance_name
        self.zone = zone
    
    def create_spot_vm(self) -> bool:
        """Create a new Spot VM with GPU."""
        try:
            logger.info(f"Creating Spot VM {self.instance_name}...")
            
            # Create startup script
            startup_script = self._create_startup_script()
            
            subprocess.run([
                'gcloud', 'compute', 'instances', 'create', self.instance_name,
                '--zone', self.zone,
                '--machine-type', 'n1-standard-4',
                '--image-family', 'ubuntu-2004-lts',
                '--image-project', 'ubuntu-os-cloud',
                '--boot-disk-size', '100GB',
                '--boot-disk-type', 'pd-ssd',
                '--accelerator', 'type=nvidia-tesla-t4,count=1',
                '--maintenance-policy', 'TERMINATE',
                '--provisioning-model', 'SPOT',
                '--instance-termination-action', 'STOP',
                '--scopes', 'https://www.googleapis.com/auth/cloud-platform',
                '--metadata', 'install-nvidia-driver=true',
                '--metadata-from-file', f'startup-script={startup_script}'
            ], check=True)
            
            logger.info(f"Spot VM {self.instance_name} created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create Spot VM: {e}")
            return False
    
    def _create_startup_script(self) -> str:
        """Create startup script content."""
        script_content = '''#!/bin/bash
apt-get update
apt-get install -y wget unzip python3 python3-pip git xvfb

# Install NVIDIA drivers
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
apt-get update
apt-get install -y nvidia-container-toolkit

# Install Python dependencies
pip3 install airsim opencv-python numpy

# Download AirSim environments
mkdir -p /opt/airsim
cd /opt/airsim
wget -O Blocks.zip https://github.com/Microsoft/AirSim/releases/download/v1.6.0-linux/Blocks.zip
unzip -o Blocks.zip

# Setup display
export DISPLAY=:0
Xvfb :0 -screen 0 1024x768x24 &
'''
        
        script_path = "/tmp/airsim-setup.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return script_path
    
    def get_vm_status(self) -> str:
        """Get current VM status."""
        try:
            result = subprocess.run([
                'gcloud', 'compute', 'instances', 'describe', self.instance_name,
                '--zone', self.zone, '--format', 'value(status)'
            ], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "NOT_FOUND"
    
    def get_external_ip(self) -> Optional[str]:
        """Get external IP of the VM."""
        try:
            result = subprocess.run([
                'gcloud', 'compute', 'instances', 'describe', self.instance_name,
                '--zone', self.zone, '--format', 'value(networkInterfaces[0].accessConfigs[0].natIP)'
            ], capture_output=True, text=True, check=True)
            ip = result.stdout.strip()
            return ip if ip != "None" else None
        except subprocess.CalledProcessError:
            return None
    
    def delete_vm(self) -> bool:
        """Delete the Spot VM."""
        try:
            logger.info(f"Deleting Spot VM {self.instance_name}...")
            subprocess.run([
                'gcloud', 'compute', 'instances', 'delete', self.instance_name,
                '--zone', self.zone, '--quiet'
            ], check=True)
            logger.info(f"Spot VM {self.instance_name} deleted successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete Spot VM: {e}")
            return False
    
    def get_cost_estimate(self, hours: int = 24) -> dict:
        """Get cost estimate for Spot VM."""
        # Spot pricing estimates (actual may vary)
        spot_cost_per_hour = 0.25  # Conservative estimate
        total_cost = spot_cost_per_hour * hours
        
        return {
            "spot_cost_per_hour": spot_cost_per_hour,
            "total_cost": total_cost,
            "hours": hours,
            "savings_vs_ondemand": "75-87%"
        }

def main():
    parser = argparse.ArgumentParser(description="Manage Spot VM for AirSim")
    parser.add_argument("action", choices=["create", "delete", "status", "ip", "cost"],
                       help="Action to perform")
    parser.add_argument("--instance", default="airsim-spot",
                       help="Instance name (default: airsim-spot)")
    parser.add_argument("--zone", default="us-central1-a",
                       help="Zone (default: us-central1-a)")
    parser.add_argument("--hours", type=int, default=24,
                       help="Hours for cost calculation (default: 24)")
    
    args = parser.parse_args()
    manager = SpotVMManager(args.instance, args.zone)
    
    if args.action == "create":
        success = manager.create_spot_vm()
        if success:
            logger.info("Waiting for VM to be ready...")
            time.sleep(30)  # Wait for startup
            ip = manager.get_external_ip()
            if ip:
                logger.info(f"VM external IP: {ip}")
                logger.info("You can now SSH to this IP")
        sys.exit(0 if success else 1)
    
    elif args.action == "delete":
        success = manager.delete_vm()
        sys.exit(0 if success else 1)
    
    elif args.action == "status":
        status = manager.get_vm_status()
        logger.info(f"VM status: {status}")
        if status == "RUNNING":
            ip = manager.get_external_ip()
            if ip:
                logger.info(f"External IP: {ip}")
    
    elif args.action == "ip":
        ip = manager.get_external_ip()
        if ip:
            logger.info(f"External IP: {ip}")
        else:
            logger.error("Could not get external IP")
            sys.exit(1)
    
    elif args.action == "cost":
        cost_info = manager.get_cost_estimate(args.hours)
        logger.info(f"Cost estimate for {args.hours} hours:")
        logger.info(f"  Spot cost per hour: ${cost_info['spot_cost_per_hour']:.2f}")
        logger.info(f"  Total for {args.hours} hours: ${cost_info['total_cost']:.2f}")
        logger.info(f"  Savings vs on-demand: {cost_info['savings_vs_ondemand']}")

if __name__ == "__main__":
    main()
```

### **Step 5: Update Configuration for Spot VM**

Update `config/spot_airsim.json`:
```json
{
  "airsim": {
    "host": "SPOT_VM_EXTERNAL_IP",
    "port": 41451,
    "timeout": 10.0
  },
  "drone": {
    "max_speed": 10.0,
    "takeoff_height": 5.0,
    "safety_distance": 5.0,
    "emergency_landing_height": 2.0
  },
  "vision": {
    "min_object_area": 100,
    "obstacle_threshold": 0.3,
    "min_landing_area": 1000,
    "detection_model_path": null,
    "segmentation_model_path": null
  },
  "navigation": {
    "obstacle_avoidance": true,
    "safety_distance": 5.0,
    "max_speed": 10.0,
    "waypoint_tolerance": 2.0
  },
  "logging": {
    "level": "INFO",
    "file": "drone_vision.log",
    "max_size": "10MB",
    "backup_count": 5
  },
  "data_collection": {
    "enabled": true,
    "save_images": true,
    "save_sensor_data": true,
    "output_dir": "data/collected"
  }
}
```

## 🎮 **Step 6: Run AirSim Simulation**

### **On Spot VM:**
```bash
# SSH to Spot VM
gcloud compute ssh airsim-spot --zone=us-central1-a

# Start AirSim (Blocks environment)
cd /opt/airsim/Blocks/LinuxNoEditor
./Blocks.sh
```

### **On GCP Linux VM (your existing VM):**
```bash
# Get Spot VM IP
python scripts/spot-vm-manager.py ip

# Update configuration with Spot VM IP
# Edit config/spot_airsim.json

# Run simulation
python src/main.py config/spot_airsim.json
```

## 💡 **Cost Management**

### **Spot VM Lifecycle:**
```bash
# Create Spot VM
python scripts/spot-vm-manager.py create

# Check status
python scripts/spot-vm-manager.py status

# Get IP
python scripts/spot-vm-manager.py ip

# Delete when done
python scripts/spot-vm-manager.py delete
```

### **Cost Monitoring:**
```bash
# Check daily cost
python scripts/spot-vm-manager.py cost --hours 24

# Check monthly cost
python scripts/spot-vm-manager.py cost --hours 730
```

## ⚠️ **Important Notes**

### **Spot VM Limitations:**
1. **Preemption:** VM can be terminated with 30 seconds notice
2. **No guaranteed availability:** May not be available during high demand
3. **Best for development/testing:** Not ideal for production workloads

### **Mitigation Strategies:**
1. **Save work frequently:** Use persistent disks for important data
2. **Monitor preemption:** Check VM status regularly
3. **Have backup plan:** Keep on-demand VM as fallback

## 🎯 **Next Steps**
1. Request GPU quota
2. Create Spot VM
3. Install AirSim
4. Test connection
5. Run simulation
6. Monitor costs
7. Implement backup strategies

## 📊 **Cost Comparison Summary**

| Approach | Monthly Cost (24/7) | Setup Time | Reliability |
|----------|-------------------|------------|-------------|
| Windows VM (on-demand) | ~$401 | Hours | High |
| Spot VM + Pre-compiled | ~$50-100 | Minutes | Medium |
| **Savings** | **75-87%** | **90% faster** | Acceptable for dev |

This approach gives you the best cost-performance ratio for AirSim development and testing!
