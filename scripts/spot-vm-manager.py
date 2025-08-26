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
