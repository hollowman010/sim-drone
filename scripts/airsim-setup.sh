#!/bin/bash

# AirSim Setup Script for GCP Spot VM
# This script automatically installs AirSim and all dependencies

set -e  # Exit on any error

echo "Starting AirSim setup on GCP Spot VM..."

# Update system packages
echo "Updating system packages..."
apt-get update
apt-get install -y wget unzip python3 python3-pip git xvfb

# Install NVIDIA drivers and CUDA
echo "Installing NVIDIA drivers..."
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
apt-get update
apt-get install -y nvidia-container-toolkit

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install airsim opencv-python numpy

# Create AirSim directory
echo "Setting up AirSim environments..."
mkdir -p /opt/airsim
cd /opt/airsim

# Download pre-compiled AirSim environments
echo "Downloading AirSim Blocks environment..."
wget -O Blocks.zip https://github.com/Microsoft/AirSim/releases/download/v1.6.0-linux/Blocks.zip
unzip -o Blocks.zip

# Download additional environments (optional)
# echo "Downloading AirSim Neighborhood environment..."
# wget -O Neighborhood.zip https://github.com/Microsoft/AirSim/releases/download/v1.6.0-linux/Neighborhood.zip
# unzip -o Neighborhood.zip

# Set up display for headless operation
echo "Setting up virtual display..."
export DISPLAY=:0
Xvfb :0 -screen 0 1024x768x24 &

# Create startup script for easy AirSim launch
cat > /opt/airsim/start_airsim.sh << 'EOF'
#!/bin/bash
cd /opt/airsim/Blocks/LinuxNoEditor
export DISPLAY=:0
./Blocks.sh
EOF

chmod +x /opt/airsim/start_airsim.sh

# Create a simple test script
cat > /opt/airsim/test_connection.py << 'EOF'
#!/usr/bin/env python3
import airsim
import time

def test_airsim_connection():
    try:
        print("Connecting to AirSim...")
        client = airsim.MultirotorClient()
        client.confirmConnection()
        print("Successfully connected to AirSim!")
        
        # Test basic functionality
        print("Testing basic functionality...")
        client.enableApiControl(True)
        client.armDisarm(True)
        print("API control enabled and armed successfully!")
        
        return True
    except Exception as e:
        print(f"Error connecting to AirSim: {e}")
        return False

if __name__ == "__main__":
    test_airsim_connection()
EOF

chmod +x /opt/airsim/test_connection.py

echo "AirSim setup completed successfully!"
echo "To start AirSim: cd /opt/airsim && ./start_airsim.sh"
echo "To test connection: python3 /opt/airsim/test_connection.py"
