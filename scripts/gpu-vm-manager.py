#!/usr/bin/env python3
"""
GPU VM Manager for AirSim on GCP
Manages the airsim-gpu instance for cost optimization.
"""

import subprocess
import time
import logging
import sys
import argparse
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GPUVMManager:
    def __init__(self, instance_name: str = "airsim-gpu", zone: str = "us-central1-a"):
        self.instance_name = instance_name
        self.zone = zone
    
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
    
    def stop_vm(self) -> bool:
        """Stop the GPU VM to save costs."""
        try:
            logger.info(f"Stopping GPU VM {self.instance_name}...")
            subprocess.run([
                'gcloud', 'compute', 'instances', 'stop', self.instance_name,
                '--zone', self.zone
            ], check=True)
            logger.info(f"GPU VM {self.instance_name} stopped successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop GPU VM: {e}")
            return False
    
    def start_vm(self) -> bool:
        """Start the GPU VM."""
        try:
            logger.info(f"Starting GPU VM {self.instance_name}...")
            subprocess.run([
                'gcloud', 'compute', 'instances', 'start', self.instance_name,
                '--zone', self.zone
            ], check=True)
            logger.info(f"GPU VM {self.instance_name} started successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start GPU VM: {e}")
            return False
    
    def delete_vm(self) -> bool:
        """Delete the GPU VM."""
        try:
            logger.info(f"Deleting GPU VM {self.instance_name}...")
            subprocess.run([
                'gcloud', 'compute', 'instances', 'delete', self.instance_name,
                '--zone', self.zone, '--quiet'
            ], check=True)
            logger.info(f"GPU VM {self.instance_name} deleted successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to delete GPU VM: {e}")
            return False
    
    def get_cost_estimate(self, hours: int = 24) -> dict:
        """Get cost estimate for GPU VM."""
        # GPU VM pricing estimates (Spot pricing)
        spot_cost_per_hour = 0.35  # Conservative estimate for n1-standard-4 + T4 GPU
        total_cost = spot_cost_per_hour * hours
        
        return {
            "spot_cost_per_hour": spot_cost_per_hour,
            "total_cost": total_cost,
            "hours": hours,
            "savings_vs_ondemand": "60-80%"
        }
    
    def check_gpu_status(self) -> bool:
        """Check if GPU is properly configured."""
        try:
            # SSH into VM and check GPU status
            result = subprocess.run([
                'gcloud', 'compute', 'ssh', self.instance_name,
                '--zone', self.zone,
                '--command', 'nvidia-smi'
            ], capture_output=True, text=True, check=True)
            
            if "NVIDIA T4" in result.stdout:
                logger.info("GPU is properly configured and working")
                return True
            else:
                logger.warning("GPU not detected or not properly configured")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to check GPU status: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Manage GPU VM for AirSim")
    parser.add_argument("action", choices=["start", "stop", "delete", "status", "ip", "cost", "check-gpu"],
                       help="Action to perform")
    parser.add_argument("--instance", default="airsim-gpu",
                       help="Instance name (default: airsim-gpu)")
    parser.add_argument("--zone", default="us-central1-a",
                       help="Zone (default: us-central1-a)")
    parser.add_argument("--hours", type=int, default=24,
                       help="Hours for cost calculation (default: 24)")
    
    args = parser.parse_args()
    manager = GPUVMManager(args.instance, args.zone)
    
    if args.action == "start":
        success = manager.start_vm()
        if success:
            logger.info("Waiting for VM to be ready...")
            time.sleep(30)
            ip = manager.get_external_ip()
            if ip:
                logger.info(f"VM external IP: {ip}")
        sys.exit(0 if success else 1)
    
    elif args.action == "stop":
        success = manager.stop_vm()
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
    
    elif args.action == "check-gpu":
        gpu_ok = manager.check_gpu_status()
        sys.exit(0 if gpu_ok else 1)

if __name__ == "__main__":
    main()
