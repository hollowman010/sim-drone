#!/bin/bash
# Deploy drone simulation project to GCP instance

set -e

# Configuration - use environment variables or defaults
PROJECT_ID="${GCP_PROJECT:-drone-sim-project}"
INSTANCE_NAME="${GPU_VM_NAME:-airsim-gpu}"
ZONE="${GCP_ZONE:-us-central1-a}"
REMOTE_USER="medimonam"
REMOTE_DIR="/home/medimonam/drone-vision"

echo "🚀 Deploying drone simulation to GCP..."

# Check if instance is running
echo "Checking instance status..."
INSTANCE_STATUS=$(gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format="value(status)")

if [ "$INSTANCE_STATUS" != "RUNNING" ]; then
    echo "Starting instance..."
    gcloud compute instances start $INSTANCE_NAME --zone=$ZONE
    
    echo "Waiting for instance to be ready..."
    sleep 30
fi

# Get instance external IP
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format="value(networkInterfaces[0].accessConfigs[0].natIP)")

echo "Instance IP: $EXTERNAL_IP"

# Create remote directory
echo "Setting up remote directory..."
gcloud compute ssh $REMOTE_USER@$INSTANCE_NAME --zone=$ZONE --command="mkdir -p $REMOTE_DIR"

# Copy project files
echo "Copying project files..."
gcloud compute scp --recurse . $REMOTE_USER@$INSTANCE_NAME:$REMOTE_DIR --zone=$ZONE

# Set up the environment
echo "Setting up environment..."
gcloud compute ssh $REMOTE_USER@$INSTANCE_NAME --zone=$ZONE --command="
cd $REMOTE_DIR

# Install system dependencies for vision and AirSim
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv curl wget \\
    python3-opencv libopencv-dev \\
    python3-numpy python3-scipy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies including vision support
pip install -r requirements.txt
pip install opencv-python numpy airsim

# Make scripts executable
chmod +x scripts/cloud_management.py
chmod +x scripts/startup.sh

# Install systemd service
sudo cp scripts/cloud-manager.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cloud-manager.service
sudo systemctl start cloud-manager.service

echo '✅ Deployment complete!'
echo 'Cloud manager service is now running.'
echo 'Check status with: sudo systemctl status cloud-manager'
"

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. SSH to your instance: gcloud compute ssh $REMOTE_USER@$INSTANCE_NAME --zone=$ZONE"
echo "2. Check cloud manager status: sudo systemctl status cloud-manager"
echo "3. View logs: sudo journalctl -u cloud-manager -f"
echo "4. Test your simulation:"
echo "   Basic flight: cd $REMOTE_DIR && python src/main.py"
echo "   With vision:  cd $REMOTE_DIR && VISION=1 OUTPUT_DIR=~/runs/\$(date +%F_%H%M%S) python src/main.py"
echo ""
echo "💰 Cost management:"
echo "- Instance will auto-shutdown after 30 minutes of inactivity"
echo "- Won't shutdown if simulation is running"
echo "- Monitor costs: gcloud billing accounts list"
echo ""
echo "🔧 Manual controls:"
echo "- Start instance: gcloud compute instances start $INSTANCE_NAME --zone=$ZONE"
echo "- Stop instance: gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE"
echo "- Check status: gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE"
