# Quick Start Guide: Complete Development Workflow

## 🚀 Complete Setup in 10 Steps

This guide will set up your complete development workflow: **Local Development** → **GitHub Version Control** → **Automated CI/CD** → **GCP Deployment**

---

## Step 1: Create GitHub Repository

1. **Go to GitHub:** https://github.com/new
2. **Repository name:** `drone-vision`
3. **Description:** "AirSim-based drone simulation with computer vision and autonomous navigation"
4. **Visibility:** Public or Private
5. **Initialize with:** README, .gitignore (Python), License (MIT)
6. **Click:** "Create repository"

---

## Step 2: Set Up Local Repository

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/drone-vision.git

# Push your code
git push -u origin main

# Create develop branch
git checkout -b develop
git push -u origin develop
```

---

## Step 3: Set Up GCP Service Account

1. **Go to GCP Console:** https://console.cloud.google.com
2. **Navigate to:** IAM & Admin → Service Accounts
3. **Create Service Account:**
   - Name: `github-actions-deploy`
   - Description: "Service account for GitHub Actions deployment"
4. **Grant Roles:**
   - Compute Instance Admin
   - Service Account User
   - Cloud Build Editor
5. **Create Key:** JSON format
6. **Download the JSON file**

---

## Step 4: Configure GitHub Secrets

1. **Go to your GitHub repository**
2. **Settings** → **Secrets and variables** → **Actions**
3. **Add repository secrets:**
   - `GCP_SA_KEY`: Paste the entire JSON content from Step 3
   - `GCP_PROJECT_ID`: `drone-sim-project`

---

## Step 5: Test Your Workflow

```bash
# Make a small change
echo "# Test commit" >> README.md

# Commit and push
git add README.md
git commit -m "test: verify CI/CD pipeline"
git push origin develop
```

4. **Check GitHub Actions:** Go to Actions tab in your repository
5. **Verify:** Pipeline runs successfully

---

## Step 6: Set Up Local Development Environment

```bash
# Install development dependencies
pip install pytest pytest-cov black flake8 mypy bandit isort pre-commit

# Set up pre-commit hooks
pre-commit install

# Test the development workflow
./scripts/dev-workflow.sh
```

---

## Step 7: Create Your First Feature

```bash
# Create feature branch
git checkout develop
git checkout -b feature/improved-vision

# Make your changes
# ... edit code ...

# Run development workflow
./scripts/dev-workflow.sh

# Commit and push
git add .
git commit -m "feat: improve vision processing algorithm"
git push origin feature/improved-vision
```

---

## Step 8: Create Pull Request

1. **Go to GitHub:** Your repository
2. **Click:** "Compare & pull request" for your feature branch
3. **Title:** "feat: improve vision processing algorithm"
4. **Description:** Describe your changes
5. **Review:** Code will be automatically tested
6. **Merge:** When tests pass and code is reviewed

---

## Step 9: Deploy to Staging

```bash
# Merge to develop (if not already done)
git checkout develop
git merge feature/improved-vision
git push origin develop

# This automatically triggers staging deployment
# Check GitHub Actions for deployment status
```

---

## Step 10: Deploy to Production

```bash
# When ready for production
git checkout main
git merge develop
git push origin main

# This automatically triggers production deployment
# Check GitHub Actions for deployment status
```

---

## 🎯 Your Complete Workflow

### Daily Development Cycle

```bash
# 1. Start new feature
git checkout develop
git pull origin develop
git checkout -b feature/your-feature

# 2. Develop and test locally
./scripts/dev-workflow.sh

# 3. Commit and push
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature

# 4. Create PR on GitHub
# 5. Code review and merge
# 6. Automatic deployment to staging
# 7. Test in staging
# 8. Deploy to production when ready
```

### Cost Management

```bash
# Check costs
gcloud billing accounts list

# Set budget alerts
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Drone Simulation Budget" \
  --budget-amount=100USD

# Monitor instance
gcloud compute instances describe drone-sim-dev --zone=us-central1-a
```

---

## 🔧 Troubleshooting

### Common Issues

1. **GitHub Actions Fails:**
   - Check GCP credentials in secrets
   - Verify service account permissions
   - Check logs in Actions tab

2. **Deployment Fails:**
   - Verify GCP instance is running
   - Check network connectivity
   - Review application logs

3. **Local Tests Fail:**
   - Update dependencies: `pip install -r requirements.txt`
   - Check Python version: `python --version`
   - Verify virtual environment: `which python`

### Useful Commands

```bash
# Check instance status
gcloud compute instances describe drone-sim-dev --zone=us-central1-a

# SSH to instance
gcloud compute ssh medimonam@drone-sim-dev --zone=us-central1-a

# View logs
gcloud compute ssh medimonam@drone-sim-dev --zone=us-central1-a --command="sudo journalctl -u cloud-manager -f"

# Start/stop instance
gcloud compute instances start drone-sim-dev --zone=us-central1-a
gcloud compute instances stop drone-sim-dev --zone=us-central1-a
```

---

## 📊 Monitoring Your Workflow

### GitHub Actions Dashboard
- **URL:** `https://github.com/YOUR_USERNAME/drone-vision/actions`
- **Monitor:** Test results, deployment status, build times

### GCP Console
- **Compute Engine:** Instance status and metrics
- **Cloud Logging:** Application logs
- **Billing:** Cost monitoring and alerts

### Local Development
- **Coverage Reports:** `htmlcov/index.html`
- **Test Results:** `pytest` output
- **Linting:** `flake8`, `mypy` output

---

## 🎉 You're All Set!

Your development workflow is now complete:

✅ **Local Development** with automated testing and formatting  
✅ **GitHub Version Control** with branch protection  
✅ **Automated CI/CD** pipeline with quality gates  
✅ **GCP Deployment** with cost management  
✅ **Monitoring** and alerting  

**Next Steps:**
1. Start developing your drone simulation features
2. Use the workflow for all your changes
3. Monitor costs and performance
4. Scale as your project grows

Happy coding! 🚁✨
