# Cost Optimization Guide for Drone Simulation on GCP

## Overview
This guide covers strategies to minimize costs while running your drone simulation on Google Cloud Platform.

## Current Setup
- **Instance Type:** n1-standard-4 (4 vCPUs, 15 GB RAM)
- **Preemptible:** Yes (75% cost savings)
- **Zone:** us-central1-a
- **Estimated Cost:** ~$0.15/hour (~$108/month if running 24/7)

## Cost Optimization Strategies

### 1. **Preemptible Instances** ✅ (Already using)
**Savings:** 75% cost reduction
- **Pros:** Much cheaper, good for development/testing
- **Cons:** Can be terminated with 30 seconds notice
- **Best for:** Non-critical workloads, development

### 2. **Automatic Shutdown** ✅ (Implemented)
**Savings:** 90%+ when not in use
- Shuts down after 30 minutes of inactivity
- Won't shutdown if simulation is running
- Won't shutdown if user is active

### 3. **Scheduled Instances**
Create instances that only run during specific hours:

```bash
# Start instance at 9 AM
gcloud compute instances start drone-sim-dev --zone=us-central1-a

# Stop instance at 6 PM
gcloud compute instances stop drone-sim-dev --zone=us-central1-a
```

### 4. **Spot Instances** (Alternative to Preemptible)
**Savings:** Up to 91% cost reduction
```bash
gcloud compute instances create drone-sim-dev-spot \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --preemptible \
  --maintenance-policy=TERMINATE \
  --restart-on-failure
```

### 5. **Commitment Discounts**
For long-term usage (1-3 years):
- **1-year commitment:** 30% discount
- **3-year commitment:** 55% discount

### 6. **Right-sizing Instances**
Monitor usage and adjust instance size:

```bash
# Check current usage
gcloud compute instances describe drone-sim-dev --zone=us-central1-a

# Resize if needed
gcloud compute instances set-machine-type drone-sim-dev \
  --machine-type=n1-standard-2 \
  --zone=us-central1-a
```

### 7. **Multi-region Optimization**
Use cheaper regions:
- **us-central1:** $0.0475/hour (current)
- **us-east1:** $0.0475/hour
- **us-west1:** $0.0475/hour
- **europe-west1:** $0.0526/hour
- **asia-east1:** $0.0526/hour

## Cost Monitoring

### 1. **Set Up Budget Alerts**
```bash
# Create budget
gcloud billing budgets create \
  --billing-account=01F700-80DE18-DC4167 \
  --display-name="Drone Simulation Budget" \
  --budget-amount=100USD \
  --threshold-rule=percent=0.5 \
  --threshold-rule=percent=0.8 \
  --threshold-rule=percent=1.0
```

### 2. **Monitor Costs**
```bash
# View current costs
gcloud billing accounts list

# Export billing data
gcloud billing export create \
  --billing-account=01F700-80DE18-DC4167 \
  --destination-uri=gs://your-bucket/billing-export
```

## Usage Patterns & Recommendations

### Development Phase
- **Use:** Preemptible instances with auto-shutdown
- **Cost:** ~$10-30/month
- **Availability:** 24/7 with auto-restart

### Testing Phase
- **Use:** Regular instances during work hours
- **Cost:** ~$50-100/month
- **Availability:** 8-10 hours/day

### Production Phase
- **Use:** Commitment discounts + auto-scaling
- **Cost:** ~$200-500/month
- **Availability:** 24/7 with redundancy

## Automated Cost Management

### 1. **Cloud Manager Script**
The `cloud_management.py` script automatically:
- Monitors simulation status
- Detects user activity
- Shuts down when idle
- Prevents crashes during active work

### 2. **Usage Examples**
```bash
# Start monitoring
python scripts/cloud_management.py monitor

# Check status
python scripts/cloud_management.py status

# Manual shutdown
python scripts/cloud_management.py stop

# Manual start
python scripts/cloud_management.py start
```

### 3. **Systemd Service**
The cloud manager runs as a background service:
```bash
# Check service status
sudo systemctl status cloud-manager

# View logs
sudo journalctl -u cloud-manager -f

# Restart service
sudo systemctl restart cloud-manager
```

## Cost Estimation Examples

### Scenario 1: Light Development (10 hours/week)
- **Instance running:** 10 hours/week
- **Cost:** ~$6/month
- **Strategy:** Auto-shutdown + preemptible

### Scenario 2: Active Development (40 hours/week)
- **Instance running:** 40 hours/week
- **Cost:** ~$24/month
- **Strategy:** Auto-shutdown + preemptible

### Scenario 3: Continuous Development (24/7)
- **Instance running:** 24/7
- **Cost:** ~$108/month
- **Strategy:** Preemptible + monitoring

### Scenario 4: Production (24/7 with redundancy)
- **Instances:** 2 regular instances
- **Cost:** ~$432/month
- **Strategy:** Commitment discounts + auto-scaling

## Best Practices

1. **Always use preemptible for development**
2. **Set up budget alerts immediately**
3. **Monitor usage patterns weekly**
4. **Use auto-shutdown for non-critical workloads**
5. **Consider spot instances for batch processing**
6. **Right-size instances based on actual usage**
7. **Use cheaper regions when possible**
8. **Implement proper logging and monitoring**

## Emergency Cost Control

If costs exceed expectations:

1. **Immediate actions:**
   ```bash
   # Stop all instances
   gcloud compute instances stop drone-sim-dev --zone=us-central1-a
   
   # Delete unnecessary resources
   gcloud compute instances delete drone-sim-dev --zone=us-central1-a
   ```

2. **Review billing:**
   ```bash
   # Check current month's costs
   gcloud billing accounts list
   ```

3. **Set stricter budgets:**
   ```bash
   # Create lower budget limit
   gcloud billing budgets create \
     --billing-account=01F700-80DE18-DC4167 \
     --display-name="Emergency Budget" \
     --budget-amount=50USD
   ```

## Next Steps

1. **Push your code to GitHub** so it can be cloned on the instance
2. **Test the cloud manager script** locally first
3. **Set up budget alerts** immediately
4. **Monitor costs** for the first week
5. **Adjust strategies** based on actual usage patterns
