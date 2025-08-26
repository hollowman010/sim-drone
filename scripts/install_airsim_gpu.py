#!/usr/bin/env python3
"""
Automated AirSim Installation Script for GPU VM
Follows the step-by-step guide for installing AirSim on GCP GPU instance.
"""

import subprocess
import time
import logging
import sys
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AirSimGPUInstaller:
    def __init__(self, instance_name: str = "airsim-gpu", zone: str = "us-central1-f"):
        self.instance_name = instance_name
        self.zone = zone
    
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
    
    def run_remote_command(self, command: str, description: str) -> bool:
        """Run a command on the remote VM."""
        try:
            logger.info(f"Running: {description}")
            result = subprocess.run([
                'gcloud', 'compute', 'ssh', self.instance_name,
                '--zone', self.zone,
                '--command', command
            ], capture_output=True, text=True, check=True)
            logger.info(f"✓ {description} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ {description} failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
    
    def install_gpu_drivers(self) -> bool:
        """Part 1: Install GPU drivers."""
        logger.info("=== Part 1: Installing GPU Drivers ===")
        
        commands = [
            ("sudo apt-get update", "Updating package list"),
            ("sudo apt-get install -y wget", "Installing wget"),
            ("wget https://raw.githubusercontent.com/GoogleCloudPlatform/compute-gpu-installation/main/linux/install_gpu_driver.py", "Downloading GPU installer"),
            ("sudo python3 install_gpu_driver.py", "Installing GPU drivers")
        ]
        
        for command, description in commands:
            if not self.run_remote_command(command, description):
                return False
        
        logger.info("GPU driver installation completed. VM will reboot automatically.")
        logger.info("Waiting 60 seconds for reboot...")
        time.sleep(60)
        
        # Verify GPU installation
        logger.info("Verifying GPU installation...")
        return self.run_remote_command("nvidia-smi", "Checking GPU status")
    
    def install_airsim(self) -> bool:
        """Part 2: Download and install AirSim."""
        logger.info("=== Part 2: Installing AirSim ===")
        
        commands = [
            ("sudo apt-get install -y unzip", "Installing unzip"),
            ("wget https://github.com/Microsoft/AirSim/releases/download/v1.6.0-linux/Blocks.zip", "Downloading AirSim Blocks environment"),
            ("unzip -o Blocks.zip", "Extracting AirSim"),
            ("chmod +x Blocks/LinuxNoEditor/Blocks.sh", "Making AirSim executable")
        ]
        
        for command, description in commands:
            if not self.run_remote_command(command, description):
                return False
        
        return True
    
    def install_python_client(self) -> bool:
        """Part 3: Install Python AirSim client."""
        logger.info("=== Part 3: Installing Python AirSim Client ===")
        
        commands = [
            ("sudo apt-get update", "Updating package list"),
            ("sudo apt-get install -y python3-pip", "Installing pip"),
            ("pip3 install airsim", "Installing AirSim Python client")
        ]
        
        for command, description in commands:
            if not self.run_remote_command(command, description):
                return False
        
        return True
    
    def create_test_script(self) -> bool:
        """Part 4: Create test flight script."""
        logger.info("=== Part 4: Creating Test Flight Script ===")
        
        test_script = '''import airsim
import time

# Connect to the AirSim simulator
client = airsim.MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)

# Take off
print("Taking off...")
client.takeoffAsync().join()

# Move forward
print("Moving forward...")
client.moveToPositionAsync(-10, 0, -10, 5).join()

# Land
print("Landing...")
client.landAsync().join()

# Disarm
client.armDisarm(False)
client.enableApiControl(False)

print("Test flight completed successfully!")
'''
        
        # Create the test script on the VM
        command = f'echo \'{test_script}\' > hello_drone.py'
        return self.run_remote_command(command, "Creating test flight script")
    
    def run_complete_installation(self) -> bool:
        """Run the complete AirSim installation process."""
        logger.info("Starting complete AirSim installation on GPU VM...")
        
        # Check if VM is running
        ip = self.get_external_ip()
        if not ip:
            logger.error("VM is not running or IP not available")
            return False
        
        logger.info(f"VM IP: {ip}")
        
        # Run all installation steps
        if not self.install_gpu_drivers():
            logger.error("GPU driver installation failed")
            return False
        
        if not self.install_airsim():
            logger.error("AirSim installation failed")
            return False
        
        if not self.install_python_client():
            logger.error("Python client installation failed")
            return False
        
        if not self.create_test_script():
            logger.error("Test script creation failed")
            return False
        
        logger.info("=== Installation Complete! ===")
        logger.info("Next steps:")
        logger.info("1. SSH to your VM: gcloud compute ssh airsim-gpu --zone=us-central1-f")
        logger.info("2. Start AirSim: ./Blocks/LinuxNoEditor/Blocks.sh -windowed")
        logger.info("3. In another SSH window, run: python3 hello_drone.py")
        
        return True

def main():
    installer = AirSimGPUInstaller()
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        # Just check GPU status
        ip = installer.get_external_ip()
        if ip:
            logger.info(f"VM IP: {ip}")
            installer.run_remote_command("nvidia-smi", "Checking GPU status")
        else:
            logger.error("VM not running")
    else:
        # Run complete installation
        success = installer.run_complete_installation()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
