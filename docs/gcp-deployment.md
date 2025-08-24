# GCP Deployment Guide for AirSim Drone Simulation

## Overview
This guide walks you through deploying your drone simulation project on Google Cloud Platform (GCP) for high-performance AirSim execution.

## Prerequisites
- Google Cloud Account
- Google Cloud SDK installed locally
- Docker installed locally (optional)

## Step 1: GCP Project Setup

### 1.1 Create GCP Project
```bash
# Create new project
gcloud projects create drone-sim-project --name="Drone Simulation Project"

# Set as default project
gcloud config set project drone-sim-project

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 1.2 Configure Billing
- Go to GCP Console → Billing
- Link billing account to your project
- Set up billing alerts (recommended: $50/day limit)

## Step 2: Instance Configuration

### 2.1 Development Instance (Cost-effective)
```bash
# Create development instance
gcloud compute instances create drone-sim-dev \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator="type=nvidia-tesla-t4,count=1" \
  --maintenance-policy=TERMINATE \
  --restart-on-failure \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --metadata="install-nvidia-driver=True"
```

### 2.2 Production Instance (High-performance)
```bash
# Create production instance
gcloud compute instances create drone-sim-prod \
  --zone=us-central1-a \
  --machine-type=n1-standard-8 \
  --accelerator="type=nvidia-tesla-v100,count=1" \
  --maintenance-policy=TERMINATE \
  --restart-on-failure \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=200GB \
  --boot-disk-type=pd-ssd \
  --metadata="install-nvidia-driver=True"
```

## Step 3: Instance Setup

### 3.1 Connect to Instance
```bash
# SSH into instance
gcloud compute ssh drone-sim-dev --zone=us-central1-a
```

### 3.2 Install Dependencies
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and development tools
sudo apt-get install -y python3 python3-pip python3-venv git wget curl

# Install Docker (for containerized deployment)
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER

# Install NVIDIA drivers (if not auto-installed)
sudo apt-get install -y nvidia-driver-470
```

### 3.3 Install AirSim Dependencies
```bash
# Install Unreal Engine dependencies
sudo apt-get install -y build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev

# Install additional libraries
sudo apt-get install -y libcanberra-gtk-module libcanberra-gtk3-module
```

## Step 4: Deploy Your Code

### 4.1 Upload Project
```bash
# From your local machine, upload project
gcloud compute scp --recurse ./src drone-sim-dev:~/drone-simulation/ --zone=us-central1-a
gcloud compute scp requirements.txt drone-sim-dev:~/drone-simulation/ --zone=us-central1-a
gcloud compute scp settings.json drone-sim-dev:~/drone-simulation/ --zone=us-central1-a
```

### 4.2 Setup Python Environment
```bash
# On the GCP instance
cd ~/drone-simulation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 5: Install AirSim

### 5.1 Clone AirSim
```bash
cd ~
git clone https://github.com/microsoft/AirSim.git
cd AirSim
```

### 5.2 Build AirSim (Linux)
```bash
# Install Unreal Engine (Linux version)
# Note: This is a simplified version - full setup requires Epic Games account

# Build AirSim
./setup.sh
./build.sh
```

### 5.3 Alternative: Use Pre-built Binaries
```bash
# Download pre-built AirSim binaries (if available)
wget https://github.com/microsoft/AirSim/releases/download/v1.8.1/AirSim-v1.8.1-linux.tar.gz
tar -xzf AirSim-v1.8.1-linux.tar.gz
```

## Step 6: Configure AirSim

### 6.1 Setup AirSim Settings
```bash
# Copy your settings.json to AirSim
cp ~/drone-simulation/settings.json ~/AirSim/settings.json

# Or create AirSim settings directory
mkdir -p ~/Documents/AirSim
cp ~/drone-simulation/settings.json ~/Documents/AirSim/
```

### 6.2 Configure Environment
```bash
# Set environment variables
echo 'export AIRSIM_PATH=~/AirSim' >> ~/.bashrc
echo 'export PYTHONPATH=$PYTHONPATH:~/drone-simulation/src' >> ~/.bashrc
source ~/.bashrc
```

## Step 7: Run Simulation

### 7.1 Start AirSim
```bash
# Start AirSim (this will launch Unreal Engine)
cd ~/AirSim
./AirSim.sh
```

### 7.2 Run Your Simulation
```bash
# In another terminal
cd ~/drone-simulation
source venv/bin/activate
python src/main.py
```

## Step 8: Cost Optimization

### 8.1 Instance Management
```bash
# Stop instance when not in use (saves money)
gcloud compute instances stop drone-sim-dev --zone=us-central1-a

# Start when needed
gcloud compute instances start drone-sim-dev --zone=us-central1-a
```

### 8.2 Preemptible Instances (Cost-effective)
```bash
# Use preemptible instances for development (60% cheaper)
gcloud compute instances create drone-sim-dev-preempt \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator="type=nvidia-tesla-t4,count=1" \
  --preemptible \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=100GB
```

## Step 9: Monitoring and Logging

### 9.1 Setup Cloud Monitoring
```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com

# View instance metrics
gcloud compute instances describe drone-sim-dev --zone=us-central1-a
```

### 9.2 Log Management
```bash
# Setup Cloud Logging
gcloud services enable logging.googleapis.com

# View logs
gcloud logging read "resource.type=gce_instance" --limit=50
```

## Step 10: Backup and Recovery

### 10.1 Create Snapshots
```bash
# Create disk snapshot
gcloud compute disks snapshot drone-sim-dev \
  --snapshot-names=drone-sim-backup-$(date +%Y%m%d) \
  --zone=us-central1-a
```

### 10.2 Restore from Snapshot
```bash
# Create new disk from snapshot
gcloud compute disks create drone-sim-restored \
  --source-snapshot=drone-sim-backup-20231201 \
  --zone=us-central1-a
```

## Cost Estimation

### Development Setup:
- **Instance:** n1-standard-4 + T4 GPU
- **Cost:** ~$0.50/hour = ~$12/day = ~$360/month
- **Usage:** 8 hours/day = ~$4/day = ~$120/month

### Production Setup:
- **Instance:** n1-standard-8 + V100 GPU  
- **Cost:** ~$3.00/hour = ~$72/day = ~$2,160/month
- **Usage:** 4 hours/day = ~$12/day = ~$360/month

## Best Practices

1. **Use Spot Instances** for development (60-80% cheaper)
2. **Schedule Instances** to start/stop automatically
3. **Monitor Usage** with billing alerts
4. **Use Snapshots** for backup and quick recovery
5. **Optimize Code** for cloud execution
6. **Use Docker** for consistent environments

## Troubleshooting

### Common Issues:
1. **GPU not detected:** Install NVIDIA drivers
2. **AirSim won't start:** Check Unreal Engine installation
3. **High latency:** Use closer GCP regions
4. **Cost overrun:** Set up billing alerts and use preemptible instances

### Support:
- GCP Documentation: https://cloud.google.com/docs
- AirSim Documentation: https://microsoft.github.io/AirSim/
- GCP Support: Available with paid support plan
