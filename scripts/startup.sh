#!/bin/bash
# Startup script for drone simulation instance

set -e

echo "Starting drone simulation instance setup..."

# Update system
sudo apt-get update

# Install required packages
sudo apt-get install -y python3-pip python3-venv git curl wget

# Create project directory
mkdir -p /home/medimonam/drone-vision
cd /home/medimonam/drone-vision

# Clone your project (you'll need to push to GitHub first)
# git clone https://github.com/yourusername/drone-vision.git .

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make cloud management script executable
chmod +x scripts/cloud_management.py

# Install systemd service
sudo cp scripts/cloud-manager.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cloud-manager.service
sudo systemctl start cloud-manager.service

echo "Instance setup complete!"
echo "Cloud manager service is now running and will automatically manage instance lifecycle."
