#!/usr/bin/env python3
"""
Windows VM Manager for AirSim on GCP

This script manages the Windows VM to optimize costs by starting/stopping
the instance based on usage patterns.
"""

import subprocess
import time
import logging
import sys
import argparse
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WindowsVMManager:
    """Manages Windows VM for AirSim on GCP."""
    
    def __init__(self, instance_name: str = "airsim-windows", zone: str = "us-central1-a"):
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
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get VM status: {e}")
            return "UNKNOWN"
    
    def start_vm(self) -> bool:
        """Start the Windows VM."""
        try:
            logger.info(f"Starting VM {self.instance_name}...")
            subprocess.run([
                'gcloud', 'compute', 'instances', 'start', self.instance_name,
                '--zone', self.zone
            ], check=True)
            logger.info(f"VM {self.instance_name} started successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start VM: {e}")
            return False
    
    def stop_vm(self) -> bool:
        """Stop the Windows VM."""
        try:
            logger.info(f"Stopping VM {self.instance_name}...")
            subprocess.run([
                'gcloud', 'compute', 'instances', 'stop', self.instance_name,
                '--zone', self.zone
            ], check=True)
            logger.info(f"VM {self.instance_name} stopped successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stop VM: {e}")
            return False
    
    def get_external_ip(self) -> Optional[str]:
        """Get external IP of the VM."""
        try:
            result = subprocess.run([
                'gcloud', 'compute', 'instances', 'describe', self.instance_name,
                '--zone', self.zone, '--format', 'value(networkInterfaces[0].accessConfigs[0].natIP)'
            ], capture_output=True, text=True, check=True)
            ip = result.stdout.strip()
            return ip if ip != "None" else None
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get external IP: {e}")
            return None
    
    def wait_for_vm_ready(self, timeout: int = 300) -> bool:
        """Wait for VM to be ready (running status)."""
        logger.info(f"Waiting for VM to be ready (timeout: {timeout}s)...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_vm_status()
            if status == "RUNNING":
                logger.info("VM is ready!")
                return True
            elif status == "STOPPING":
                logger.info("VM is stopping, waiting...")
            elif status == "STARTING":
                logger.info("VM is starting, waiting...")
            else:
                logger.info(f"VM status: {status}")
            
            time.sleep(10)
        
        logger.error(f"Timeout waiting for VM to be ready")
        return False
    
    def get_cost_estimate(self, hours: int = 24) -> dict:
        """Get cost estimate for running the VM."""
        # These are approximate costs (actual may vary)
        cpu_cost_per_hour = 0.38  # n1-standard-8
        gpu_cost_per_hour = 0.35  # NVIDIA T4 (if applicable)
        disk_cost_per_hour = 0.17  # 100GB SSD
        
        total_per_hour = cpu_cost_per_hour + disk_cost_per_hour
        total_cost = total_per_hour * hours
        
        return {
            "cpu_cost_per_hour": cpu_cost_per_hour,
            "disk_cost_per_hour": disk_cost_per_hour,
            "total_per_hour": total_per_hour,
            "total_cost": total_cost,
            "hours": hours
        }

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Manage Windows VM for AirSim")
    parser.add_argument("action", choices=["start", "stop", "status", "ip", "cost"],
                       help="Action to perform")
    parser.add_argument("--instance", default="airsim-windows",
                       help="Instance name (default: airsim-windows)")
    parser.add_argument("--zone", default="us-central1-a",
                       help="Zone (default: us-central1-a)")
    parser.add_argument("--hours", type=int, default=24,
                       help="Hours for cost calculation (default: 24)")
    
    args = parser.parse_args()
    
    manager = WindowsVMManager(args.instance, args.zone)
    
    if args.action == "start":
        success = manager.start_vm()
        if success:
            manager.wait_for_vm_ready()
            ip = manager.get_external_ip()
            if ip:
                logger.info(f"VM external IP: {ip}")
                logger.info("You can now connect via RDP to this IP")
        sys.exit(0 if success else 1)
    
    elif args.action == "stop":
        success = manager.stop_vm()
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
        logger.info(f"  CPU cost per hour: ${cost_info['cpu_cost_per_hour']:.2f}")
        logger.info(f"  Disk cost per hour: ${cost_info['disk_cost_per_hour']:.2f}")
        logger.info(f"  Total per hour: ${cost_info['total_per_hour']:.2f}")
        logger.info(f"  Total for {args.hours} hours: ${cost_info['total_cost']:.2f}")

if __name__ == "__main__":
    main()
