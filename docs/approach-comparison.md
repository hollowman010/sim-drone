# AirSim Setup Approaches: Cost & Technical Comparison

## 📊 **Cost Comparison**

| Approach | Monthly Cost (24/7) | Daily Cost | Setup Time | Reliability | Best For |
|----------|-------------------|------------|------------|-------------|----------|
| **Windows VM (On-Demand)** | ~$401 | ~$13.20 | Hours | High | Production |
| **Spot VM + Pre-compiled** | ~$50-100 | ~$2-4 | Minutes | Medium | Development |
| **Savings** | **75-87%** | **70-85%** | **90% faster** | Acceptable | Testing |

## 🎯 **Recommended Strategy: Spot VM + Pre-compiled Binaries**

### **Why This Approach is Superior:**

#### **💰 Cost Benefits:**
- **75-87% cost reduction** vs on-demand pricing
- **80-90% cost reduction** vs Windows VM approach
- **Perfect for development and testing**
- **Pay only when needed**

#### **⚡ Technical Advantages:**
- **No Windows complexity** - Linux is much easier to manage
- **Pre-compiled binaries** - Skip hours of compilation
- **GPU acceleration** - Better performance for AirSim
- **Faster setup** - Minutes instead of hours
- **Headless operation** - No GUI needed

#### **🛠️ Implementation Benefits:**
- **Automated setup** - Scripts handle everything
- **Easy management** - Simple commands to start/stop
- **Cost monitoring** - Built-in cost estimation
- **Flexible usage** - Create/destroy as needed

## 🚀 **Implementation Steps**

### **Step 1: Request GPU Quota**
```bash
# Go to GCP Console > IAM & Admin > Quotas
# Request "Preemptible NVIDIA T4 GPUs" quota of 1
```

### **Step 2: Create Spot VM**
```bash
# Create cost-effective Spot VM
python scripts/spot-vm-manager.py create
```

### **Step 3: Connect and Test**
```bash
# Get VM IP
python scripts/spot-vm-manager.py ip

# SSH to VM
gcloud compute ssh airsim-spot --zone=us-central1-a

# Test AirSim
python3 /opt/airsim/test_connection.py
```

### **Step 4: Run Simulation**
```bash
# On your existing GCP Linux VM
python src/main.py config/spot_airsim.json
```

## 💡 **Cost Management**

### **Spot VM Lifecycle:**
```bash
# Create when needed
python scripts/spot-vm-manager.py create

# Check status
python scripts/spot-vm-manager.py status

# Delete when done
python scripts/spot-vm-manager.py delete
```

### **Cost Monitoring:**
```bash
# Check daily cost
python scripts/spot-vm-manager.py cost --hours 24

# Check monthly cost
python scripts/spot-vm-manager.py cost --hours 730
```

## ⚠️ **Important Considerations**

### **Spot VM Limitations:**
1. **Preemption:** VM can be terminated with 30 seconds notice
2. **No guaranteed availability:** May not be available during high demand
3. **Best for development/testing:** Not ideal for production workloads

### **Mitigation Strategies:**
1. **Save work frequently:** Use persistent disks for important data
2. **Monitor preemption:** Check VM status regularly
3. **Have backup plan:** Keep on-demand VM as fallback

## 🎯 **When to Use Each Approach**

### **Use Spot VM + Pre-compiled When:**
- ✅ Development and testing
- ✅ Cost is a major concern
- ✅ Workload can tolerate interruptions
- ✅ Quick setup needed
- ✅ Linux environment is acceptable

### **Use Windows VM When:**
- ✅ Production workloads
- ✅ Maximum reliability needed
- ✅ Windows-specific requirements
- ✅ Long-running simulations
- ✅ Budget allows for higher costs

## 📈 **Cost Optimization Tips**

### **For Spot VM:**
1. **Use only when needed** - Create/destroy as required
2. **Monitor usage patterns** - Schedule around your work hours
3. **Use persistent disks** - Save important data
4. **Have backup plans** - Keep alternative options ready

### **For Windows VM:**
1. **Schedule shutdowns** - Stop when not in use
2. **Use preemptible instances** - If available
3. **Optimize resource usage** - Right-size the VM
4. **Consider committed use discounts** - For long-term usage

## 🎯 **Recommendation**

**For your use case (drone simulation development), we strongly recommend the Spot VM + Pre-compiled approach because:**

1. **Massive cost savings** (75-87% reduction)
2. **Faster setup** (minutes vs hours)
3. **Simpler management** (Linux vs Windows)
4. **Better for development** (easy to recreate)
5. **GPU acceleration** (better performance)

The Spot VM approach gives you the best cost-performance ratio for AirSim development and testing while maintaining the flexibility to scale up to Windows VMs for production workloads when needed.
