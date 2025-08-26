#!/usr/bin/env python3
"""
GPU VM Manager for cost-optimized AirSim instances.
Streamlined management of GPU VMs for AirSim simulations.
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import google.auth
from google.cloud import compute_v1
from google.auth.exceptions import DefaultCredentialsError


class GPUVMManager:
    """Manages GPU VMs for AirSim simulations with cost optimization."""

    def __init__(self, config_path: str = "config/gpu_vm.json"):
        """Initialize the GPU VM manager.

        Args:
            config_path: Path to GPU VM configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        try:
            self.credentials, self.project_id = google.auth.default()
            self.compute_client = compute_v1.InstancesClient()
            self.zones_client = compute_v1.ZonesClient()
            self.zone_operations_client = compute_v1.ZoneOperationsClient()
        except DefaultCredentialsError:
            self.logger.error("Google Cloud credentials not found. Run 'gcloud auth application-default login'")
            sys.exit(1)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load GPU VM configuration."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default GPU VM configuration."""
        return {
            "compute": {
                "instance_name": "airsim-gpu",
                "instance_type": "n1-standard-4",
                "zone": "us-central1-a",
                "project_id": "your-project-id",
                "gpu_type": "nvidia-tesla-t4",
                "gpu_count": 1
            },
            "cost_optimization": {
                "use_spot_instances": True,
                "auto_shutdown": True,
                "max_runtime_hours": 4,
                "budget_limit": 50.0
            },
            "airsim": {
                "image_family": "debian-11",
                "image_project": "debian-cloud",
                "disk_size_gb": 50
            }
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(__name__)

    def create_gpu_vm(self) -> bool:
        """Create a GPU VM for AirSim."""
        try:
            config = self.config["compute"]
            
            # Check if instance already exists
            if self._instance_exists(config["instance_name"], config["zone"]):
                self.logger.info(f"Instance {config['instance_name']} already exists")
                return True

            # Create instance configuration
            instance_config = self._create_instance_config()
            
            # Create the instance
            operation = self.compute_client.insert(
                project=config["project_id"],
                zone=config["zone"],
                instance_resource=instance_config
            )
            
            self.logger.info(f"Creating GPU VM: {config['instance_name']}")
            self._wait_for_operation(operation, config["project_id"], config["zone"])
            
            self.logger.info("GPU VM created successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create GPU VM: {e}")
            return False

    def start_gpu_vm(self) -> bool:
        """Start the GPU VM."""
        try:
            config = self.config["compute"]
            
            if not self._instance_exists(config["instance_name"], config["zone"]):
                self.logger.error(f"Instance {config['instance_name']} does not exist")
                return False

            operation = self.compute_client.start(
                project=config["project_id"],
                zone=config["zone"],
                instance=config["instance_name"]
            )
            
            self.logger.info(f"Starting GPU VM: {config['instance_name']}")
            self._wait_for_operation(operation, config["project_id"], config["zone"])
            
            self.logger.info("GPU VM started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start GPU VM: {e}")
            return False

    def stop_gpu_vm(self) -> bool:
        """Stop the GPU VM to save costs."""
        try:
            config = self.config["compute"]
            
            operation = self.compute_client.stop(
                project=config["project_id"],
                zone=config["zone"],
                instance=config["instance_name"]
            )
            
            self.logger.info(f"Stopping GPU VM: {config['instance_name']}")
            self._wait_for_operation(operation, config["project_id"], config["zone"])
            
            self.logger.info("GPU VM stopped successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to stop GPU VM: {e}")
            return False

    def get_vm_status(self) -> Optional[str]:
        """Get the current status of the GPU VM."""
        try:
            config = self.config["compute"]
            
            instance = self.compute_client.get(
                project=config["project_id"],
                zone=config["zone"],
                instance=config["instance_name"]
            )
            
            return instance.status
            
        except Exception as e:
            self.logger.error(f"Failed to get VM status: {e}")
            return None

    def get_vm_ip(self) -> Optional[str]:
        """Get the external IP address of the GPU VM."""
        try:
            config = self.config["compute"]
            
            instance = self.compute_client.get(
                project=config["project_id"],
                zone=config["zone"],
                instance=config["instance_name"]
            )
            
            for interface in instance.network_interfaces:
                if interface.access_configs:
                    return interface.access_configs[0].nat_i_p
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get VM IP: {e}")
            return None

    def estimate_cost(self, hours: int = 24) -> float:
        """Estimate the cost for running the GPU VM."""
        try:
            # Rough cost estimation (you can make this more accurate)
            gpu_cost_per_hour = 0.35  # T4 GPU cost
            cpu_cost_per_hour = 0.19  # n1-standard-4 cost
            total_per_hour = gpu_cost_per_hour + cpu_cost_per_hour
            
            if self.config["cost_optimization"]["use_spot_instances"]:
                total_per_hour *= 0.3  # 70% discount for spot instances
            
            return total_per_hour * hours
            
        except Exception as e:
            self.logger.error(f"Failed to estimate cost: {e}")
            return 0.0

    def _instance_exists(self, instance_name: str, zone: str) -> bool:
        """Check if instance exists."""
        try:
            config = self.config["compute"]
            self.compute_client.get(
                project=config["project_id"],
                zone=zone,
                instance=instance_name
            )
            return True
        except Exception:
            return False

    def _create_instance_config(self):
        """Create instance configuration for GPU VM."""
        config = self.config["compute"]
        airsim_config = self.config["airsim"]
        
        # Create the instance resource
        instance = compute_v1.Instance()
        instance.name = config["instance_name"]
        instance.machine_type = f"zones/{config['zone']}/machineTypes/{config['instance_type']}"
        
        # Configure disk
        disk = compute_v1.AttachedDisk()
        disk.auto_delete = True
        disk.boot = True
        disk.device_name = "boot-disk"
        disk.initialize_params = compute_v1.AttachedDiskInitializeParams()
        disk.initialize_params.disk_size_gb = airsim_config["disk_size_gb"]
        disk.initialize_params.source_image = f"projects/{airsim_config['image_project']}/global/images/family/{airsim_config['image_family']}"
        instance.disks = [disk]
        
        # Configure network
        network_interface = compute_v1.NetworkInterface()
        network_interface.name = "nic0"
        network_interface.access_configs = [compute_v1.AccessConfig()]
        network_interface.access_configs[0].name = "external-nat"
        network_interface.access_configs[0].type_ = "ONE_TO_ONE_NAT"
        instance.network_interfaces = [network_interface]
        
        # Configure GPU
        if config.get("gpu_type") and config.get("gpu_count"):
            accelerator = compute_v1.AcceleratorConfig()
            accelerator.accelerator_count = config["gpu_count"]
            accelerator.accelerator_type = f"zones/{config['zone']}/acceleratorTypes/{config['gpu_type']}"
            
            instance.guest_accelerators = [accelerator]
        
        # Configure scheduling (for spot instances)
        if self.config["cost_optimization"]["use_spot_instances"]:
            instance.scheduling = compute_v1.Scheduling()
            instance.scheduling.provisioning_model = "SPOT"
            instance.scheduling.instance_termination_action = "STOP"
        
        return instance

    def _wait_for_operation(self, operation, project_id: str, zone: str):
        """Wait for operation to complete."""
        while operation.status != "DONE":
            operation = self.zone_operations_client.get(
                project=project_id,
                zone=zone,
                operation=operation.name
            )


def main():
    """Main function for GPU VM management."""
    parser = argparse.ArgumentParser(description="Manage GPU VMs for AirSim")
    parser.add_argument("action", choices=["create", "start", "stop", "status", "ip", "cost"])
    parser.add_argument("--config", default="config/gpu_vm.json", help="Configuration file path")
    parser.add_argument("--hours", type=int, default=24, help="Hours for cost estimation")
    
    args = parser.parse_args()
    
    manager = GPUVMManager(args.config)
    
    if args.action == "create":
        success = manager.create_gpu_vm()
        sys.exit(0 if success else 1)
    elif args.action == "start":
        success = manager.start_gpu_vm()
        sys.exit(0 if success else 1)
    elif args.action == "stop":
        success = manager.stop_gpu_vm()
        sys.exit(0 if success else 1)
    elif args.action == "status":
        status = manager.get_vm_status()
        print(f"VM Status: {status}")
    elif args.action == "ip":
        ip = manager.get_vm_ip()
        print(f"VM IP: {ip}")
    elif args.action == "cost":
        cost = manager.estimate_cost(args.hours)
        print(f"Estimated cost for {args.hours} hours: ${cost:.2f}")


if __name__ == "__main__":
    main()
