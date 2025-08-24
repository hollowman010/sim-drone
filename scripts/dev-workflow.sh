#!/bin/bash
# Development Workflow Script
# Automates local development process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BRANCH_NAME=$(git branch --show-current)
REMOTE_NAME="origin"

echo -e "${BLUE}🚀 Drone Simulation Development Workflow${NC}"
echo "=========================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Check if we're on the right branch
check_branch() {
    echo -e "${BLUE}📋 Checking branch...${NC}"
    if [[ "$BRANCH_NAME" == "main" ]]; then
        print_warning "You're on main branch. Consider switching to develop for development work."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    print_status "Working on branch: $BRANCH_NAME"
}

# Step 2: Update dependencies
update_deps() {
    echo -e "${BLUE}📦 Updating dependencies...${NC}"
    
    # Activate virtual environment if it exists
    if [[ -d ".venv" ]]; then
        source .venv/bin/activate
        print_status "Virtual environment activated"
    else
        print_warning "No virtual environment found. Creating one..."
        python3 -m venv .venv
        source .venv/bin/activate
        print_status "Virtual environment created and activated"
    fi
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install/update dependencies
    pip install -r requirements.txt
    
    # Install development dependencies
    pip install pytest pytest-cov black flake8 mypy bandit
    
    print_status "Dependencies updated"
}

# Step 3: Run code formatting
format_code() {
    echo -e "${BLUE}🎨 Formatting code...${NC}"
    
    # Run Black formatter
    black src/ tests/ scripts/
    print_status "Code formatted with Black"
    
    # Run isort for import sorting
    pip install isort
    isort src/ tests/ scripts/
    print_status "Imports sorted with isort"
}

# Step 4: Run linting
run_linting() {
    echo -e "${BLUE}🔍 Running linting...${NC}"
    
    # Run Flake8
    if flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503; then
        print_status "Flake8 passed"
    else
        print_error "Flake8 failed"
        return 1
    fi
    
    # Run MyPy type checking
    if mypy src/ --ignore-missing-imports; then
        print_status "MyPy type checking passed"
    else
        print_warning "MyPy found some type issues (non-blocking)"
    fi
    
    # Run Bandit security scan
    if bandit -r src/ -f json -o bandit-report.json; then
        print_status "Security scan passed"
    else
        print_warning "Security scan found some issues (check bandit-report.json)"
    fi
}

# Step 5: Run tests
run_tests() {
    echo -e "${BLUE}🧪 Running tests...${NC}"
    
    # Run pytest with coverage
    if pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html; then
        print_status "All tests passed"
        print_status "Coverage report generated in htmlcov/"
    else
        print_error "Some tests failed"
        return 1
    fi
}

# Step 6: Build and test Docker image
test_docker() {
    echo -e "${BLUE}🐳 Testing Docker build...${NC}"
    
    if docker build -t drone-simulation:dev -f docker/Dockerfile .; then
        print_status "Docker build successful"
        
        # Test the image
        if docker run --rm drone-simulation:dev python -c "print('Docker test passed')"; then
            print_status "Docker image test passed"
        else
            print_error "Docker image test failed"
            return 1
        fi
    else
        print_error "Docker build failed"
        return 1
    fi
}

# Step 7: Check git status
check_git() {
    echo -e "${BLUE}📝 Checking git status...${NC}"
    
    # Check for uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "You have uncommitted changes:"
        git status --short
        
        read -p "Commit changes? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter commit message: " commit_msg
            git add .
            git commit -m "$commit_msg"
            print_status "Changes committed"
        fi
    else
        print_status "Working directory is clean"
    fi
    
    # Check if we're up to date with remote
    git fetch $REMOTE_NAME
    local_commits=$(git rev-list HEAD...$REMOTE_NAME/$BRANCH_NAME --count 2>/dev/null || echo "0")
    
    if [[ $local_commits -gt 0 ]]; then
        print_warning "You have $local_commits local commits ahead of remote"
    else
        print_status "Up to date with remote"
    fi
}

# Step 8: Prepare for deployment
prepare_deployment() {
    echo -e "${BLUE}🚀 Preparing for deployment...${NC}"
    
    # Create deployment summary
    echo "Deployment Summary" > deployment-summary.md
    echo "==================" >> deployment-summary.md
    echo "" >> deployment-summary.md
    echo "Branch: $BRANCH_NAME" >> deployment-summary.md
    echo "Commit: $(git rev-parse HEAD)" >> deployment-summary.md
    echo "Date: $(date)" >> deployment-summary.md
    echo "" >> deployment-summary.md
    echo "Changes:" >> deployment-summary.md
    git log --oneline -10 >> deployment-summary.md
    
    print_status "Deployment summary created"
    
    # Show next steps
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo "1. Push to GitHub: git push origin $BRANCH_NAME"
    echo "2. Create PR (if on develop): https://github.com/yourusername/drone-vision/compare/main...$BRANCH_NAME"
    echo "3. Monitor CI/CD pipeline: https://github.com/yourusername/drone-vision/actions"
    echo "4. Deploy manually: ./scripts/deploy_to_gcp.sh"
}

# Main workflow
main() {
    echo "Starting development workflow..."
    echo ""
    
    # Run all steps
    check_branch || exit 1
    update_deps || exit 1
    format_code || exit 1
    run_linting || exit 1
    run_tests || exit 1
    test_docker || exit 1
    check_git || exit 1
    prepare_deployment || exit 1
    
    echo ""
    print_status "Development workflow completed successfully! 🎉"
}

# Handle command line arguments
case "${1:-}" in
    "format")
        format_code
        ;;
    "lint")
        run_linting
        ;;
    "test")
        run_tests
        ;;
    "docker")
        test_docker
        ;;
    "deploy")
        prepare_deployment
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  format   - Format code only"
        echo "  lint     - Run linting only"
        echo "  test     - Run tests only"
        echo "  docker   - Test Docker build only"
        echo "  deploy   - Prepare for deployment only"
        echo "  (no args) - Run full workflow"
        ;;
    *)
        main
        ;;
esac
