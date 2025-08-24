# Development Workflow Guide

## Overview
This guide covers the complete development workflow for the drone simulation project, from local development to automated deployment on Google Cloud Platform.

## Development Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local Dev     │    │   GitHub        │    │   GCP Cloud     │
│                 │    │                 │    │                 │
│ • Code Editor   │───▶│ • Version Ctrl  │───▶│ • Auto Deploy   │
│ • Testing       │    │ • CI/CD Pipeline│    │ • Cost Mgmt     │
│ • Formatting    │    │ • Code Review   │    │ • Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 1. Local Development Setup

### Prerequisites
- Python 3.11+
- Git
- Docker (optional)
- Virtual environment

### Initial Setup
```bash
# Clone repository
git clone https://github.com/yourusername/drone-vision.git
cd drone-vision

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy bandit isort
```

### Development Workflow Script
Use the automated workflow script for consistent development:

```bash
# Run full development workflow
./scripts/dev-workflow.sh

# Or run individual steps
./scripts/dev-workflow.sh format    # Format code only
./scripts/dev-workflow.sh lint      # Run linting only
./scripts/dev-workflow.sh test      # Run tests only
./scripts/dev-workflow.sh docker    # Test Docker build
./scripts/dev-workflow.sh deploy    # Prepare for deployment
```

## 2. Branching Strategy

### Branch Structure
```
main (production)
├── develop (staging)
│   ├── feature/new-algorithm
│   ├── feature/improved-vision
│   └── bugfix/crash-fix
└── hotfix/urgent-fix
```

### Workflow
1. **Feature Development:**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   # ... develop your feature
   git push origin feature/your-feature-name
   # Create PR to develop
   ```

2. **Bug Fixes:**
   ```bash
   git checkout develop
   git checkout -b bugfix/description-of-fix
   # ... fix the bug
   git push origin bugfix/description-of-fix
   # Create PR to develop
   ```

3. **Release to Production:**
   ```bash
   # Merge develop to main
   git checkout main
   git merge develop
   git push origin main
   # Triggers production deployment
   ```

## 3. Code Quality Standards

### Code Formatting
- **Black:** Automatic code formatting
- **isort:** Import sorting
- **Line length:** 88 characters

### Linting
- **Flake8:** Style guide enforcement
- **MyPy:** Type checking
- **Bandit:** Security scanning

### Testing
- **pytest:** Unit and integration tests
- **Coverage:** Minimum 80% code coverage
- **Integration:** End-to-end testing

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## 4. CI/CD Pipeline

### GitHub Actions Workflow
The `.github/workflows/ci-cd.yml` file defines the complete pipeline:

1. **Test Stage:**
   - Code formatting check
   - Linting (Flake8, MyPy)
   - Unit tests with coverage
   - Security scanning

2. **Build Stage:**
   - Docker image build
   - Image testing

3. **Deploy Stage:**
   - **Staging:** Deploy to GCP on `develop` branch
   - **Production:** Deploy to GCP on `main` branch

### Pipeline Triggers
- **Push to `develop`:** Deploy to staging
- **Push to `main`:** Deploy to production
- **Pull Request:** Run tests only
- **Manual:** Trigger via GitHub Actions UI

## 5. Deployment Strategy

### Environment Management
- **Local:** Development and testing
- **Staging:** Pre-production testing
- **Production:** Live environment

### Deployment Process
1. **Code Review:** All changes require PR review
2. **Automated Testing:** CI pipeline validates changes
3. **Staging Deployment:** Test in staging environment
4. **Production Deployment:** Deploy to production after staging validation

### Rollback Strategy
```bash
# Quick rollback to previous version
git revert HEAD
git push origin main

# Or rollback to specific commit
git revert <commit-hash>
git push origin main
```

## 6. Cost Management

### Development Phase
- **Instance Type:** Preemptible n1-standard-4
- **Auto-shutdown:** 30 minutes of inactivity
- **Estimated Cost:** $10-30/month

### Production Phase
- **Instance Type:** Regular n1-standard-4
- **Auto-scaling:** Based on load
- **Estimated Cost:** $200-500/month

### Cost Monitoring
```bash
# Check current costs
gcloud billing accounts list

# Set up budget alerts
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT \
  --display-name="Drone Simulation Budget" \
  --budget-amount=100USD
```

## 7. Development Best Practices

### Code Organization
```
drone-vision/
├── src/                    # Source code
│   ├── main.py            # Entry point
│   ├── flight_control.py  # Drone control
│   ├── vision_targeting.py # Computer vision
│   ├── mission_logic.py   # Mission planning
│   └── utils/             # Utilities
├── tests/                 # Test files
├── scripts/               # Automation scripts
├── docs/                  # Documentation
├── docker/                # Docker configuration
└── .github/               # GitHub Actions
```

### Commit Messages
Use conventional commit format:
```
feat: add new obstacle detection algorithm
fix: resolve memory leak in vision processing
docs: update deployment instructions
test: add unit tests for mission logic
refactor: improve code organization
```

### Documentation
- **README.md:** Project overview and setup
- **docs/:** Detailed documentation
- **Code comments:** Inline documentation
- **API docs:** Auto-generated from docstrings

## 8. Monitoring and Debugging

### Local Debugging
```bash
# Run with debug logging
python src/main.py --debug

# Run specific component
python -c "from src.flight_control import DroneController; print('Test')"

# Profile performance
python -m cProfile -o profile.stats src/main.py
```

### Cloud Monitoring
- **Cloud Logging:** Application logs
- **Cloud Monitoring:** System metrics
- **Error Reporting:** Exception tracking

### Health Checks
```bash
# Check instance status
gcloud compute instances describe drone-sim-dev --zone=us-central1-a

# Check application logs
gcloud compute ssh medimonam@drone-sim-dev --zone=us-central1-a --command="sudo journalctl -u cloud-manager -f"
```

## 9. Security Best Practices

### Code Security
- **Dependency scanning:** Regular security updates
- **Secret management:** Use environment variables
- **Input validation:** Validate all inputs
- **Error handling:** Don't expose sensitive information

### Infrastructure Security
- **IAM:** Least privilege access
- **Network security:** VPC and firewall rules
- **Encryption:** Data at rest and in transit

## 10. Performance Optimization

### Code Optimization
- **Profiling:** Identify bottlenecks
- **Caching:** Cache expensive operations
- **Async operations:** Use async/await where appropriate
- **Memory management:** Monitor memory usage

### Infrastructure Optimization
- **Instance sizing:** Right-size based on usage
- **Auto-scaling:** Scale based on demand
- **CDN:** Use CDN for static assets
- **Database optimization:** Index and query optimization

## 11. Troubleshooting

### Common Issues

#### CI/CD Pipeline Fails
1. Check GitHub Actions logs
2. Verify all tests pass locally
3. Check for linting errors
4. Verify Docker build works

#### Deployment Fails
1. Check GCP instance status
2. Verify credentials and permissions
3. Check application logs
4. Verify network connectivity

#### Performance Issues
1. Monitor system resources
2. Check application profiling
3. Review database queries
4. Optimize algorithms

### Debug Commands
```bash
# Check instance status
gcloud compute instances describe drone-sim-dev --zone=us-central1-a

# View application logs
gcloud compute ssh medimonam@drone-sim-dev --zone=us-central1-a --command="tail -f /tmp/cloud_manager.log"

# Check system resources
gcloud compute ssh medimonam@drone-sim-dev --zone=us-central1-a --command="htop"

# Test connectivity
gcloud compute ssh medimonam@drone-sim-dev --zone=us-central1-a --command="ping google.com"
```

## 12. Next Steps

1. **Set up GitHub repository** and push your code
2. **Configure GitHub Actions** with your GCP credentials
3. **Set up monitoring** and alerting
4. **Create development environment** with proper tooling
5. **Establish code review process** with your team
6. **Document APIs** and interfaces
7. **Set up automated testing** for critical paths
8. **Implement logging** and error tracking

This workflow ensures consistent, high-quality development with automated deployment and cost management! 🚀
