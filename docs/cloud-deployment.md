# Cloud Deployment Guide

## Overview
This guide covers deploying your Drone Vision AirSim project to Google Cloud Platform with cost optimization.

## Architecture

### VM Types
- **GPU VM**: Runs AirSim simulations (T4 GPU)
- **CPU VM**: Handles data processing and analysis
- **Cost Optimization**: Spot instances, auto-shutdown, workload-based scaling

## Prerequisites

### 1. Google Cloud Setup
```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable APIs
```bash
# Enable Compute Engine API
gcloud services enable compute.googleapis.com

# Enable Cloud Resource Manager API
gcloud services enable cloudresourcemanager.googleapis.com
```

## Configuration

### 1. Update Configuration Files

**GPU VM Configuration** (`config/gpu_vm.json`):
```json
{
  "compute": {
    "instance_name": "airsim-gpu",
    "instance_type": "n1-standard-4",
    "zone": "us-central1-a",
    "project_id": "YOUR_PROJECT_ID",
    "gpu_type": "nvidia-tesla-t4",
    "gpu_count": 1
  },
  "cost_optimization": {
    "use_spot_instances": true,
    "auto_shutdown": true,
    "max_runtime_hours": 4,
    "budget_limit": 50.0
  }
}
```

**CPU VM Configuration** (`config/cpu_vm.json`):
```json
{
  "compute": {
    "instance_name": "drone-cpu",
    "instance_type": "n1-standard-4",
    "zone": "us-central1-a",
    "project_id": "YOUR_PROJECT_ID"
  },
  "cost_optimization": {
    "use_spot_instances": true,
    "auto_shutdown": true,
    "max_runtime_hours": 8,
    "budget_limit": 20.0
  }
}
```

**Remote AirSim Configuration** (`config/remote_airsim.json`):
```json
{
  "airsim": {
    "host": "YOUR_GPU_VM_IP",
    "port": 41451,
    "timeout": 10.0
  }
}
```

## Deployment Steps

### 1. Create VMs
```bash
# Create GPU VM for AirSim
python scripts/gpu-vm-manager.py create

# Create CPU VM for processing
python scripts/cpu-vm-manager.py create
```

### 2. Start VMs
```bash
# Start GPU VM
python scripts/gpu-vm-manager.py start

# Start CPU VM
python scripts/cpu-vm-manager.py start
```

### 3. Get VM IPs
```bash
# Get GPU VM IP
python scripts/gpu-vm-manager.py ip

# Get CPU VM IP
python scripts/cpu-vm-manager.py ip
```

### 4. Update Remote Configuration
Update `config/remote_airsim.json` with the GPU VM IP address.

## Cost Optimization

### 1. Workload-Based Optimization
```bash
# For AirSim simulations (GPU + CPU)
python scripts/cost-optimizer.py airsim

# For processing only (CPU only)
python scripts/cost-optimizer.py processing

# Shutdown all VMs
python scripts/cost-optimizer.py shutdown
```

### 2. Cost Monitoring
```bash
# Get cost summary
python scripts/cost-optimizer.py cost --hours 24

# Monitor costs in real-time
python scripts/cost-optimizer.py monitor --monitor-hours 2

# Generate cost report
python scripts/cost-optimizer.py report --days 30
```

### 3. Cost Estimates
- **GPU VM (Spot)**: ~$0.16/hour
- **CPU VM (Spot)**: ~$0.06/hour
- **Total (Both)**: ~$0.22/hour
- **Daily Cost**: ~$5.28
- **Monthly Cost**: ~$158

## Running Simulations

### 1. Local Development
```bash
# Run locally
python src/main.py
```

### 2. Remote AirSim
```bash
# Run with remote AirSim
python src/main.py config/remote_airsim.json
```

### 3. Cloud Processing
```bash
# SSH to CPU VM for processing
gcloud compute ssh drone-cpu --zone=us-central1-a

# Run processing tasks
python src/main.py config/cpu_vm.json
```

## Best Practices

### 1. Cost Management
- Use spot instances for cost savings
- Implement auto-shutdown for idle periods
- Monitor costs regularly
- Set budget alerts

### 2. Performance
- Use GPU only for AirSim simulations
- Use CPU for data processing and analysis
- Optimize workload distribution
- Scale based on demand

### 3. Security
- Use service accounts with minimal permissions
- Enable firewall rules appropriately
- Keep VMs updated
- Monitor access logs

## Troubleshooting

### Common Issues
1. **Authentication Errors**: Run `gcloud auth application-default login`
2. **Permission Errors**: Check service account roles
3. **VM Not Starting**: Check quotas and billing
4. **Connection Issues**: Verify firewall rules and IP addresses

### Useful Commands
```bash
# Check VM status
python scripts/gpu-vm-manager.py status
python scripts/cpu-vm-manager.py status

# Get VM details
gcloud compute instances describe airsim-gpu --zone=us-central1-a
gcloud compute instances describe drone-cpu --zone=us-central1-a

# View logs
gcloud compute ssh airsim-gpu --zone=us-central1-a --command="sudo journalctl -f"
```

## Next Steps
- Set up automated deployment pipelines
- Implement monitoring and alerting
- Optimize for your specific workload
- Scale based on usage patterns
