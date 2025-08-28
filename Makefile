.PHONY: help venv demo live clean install

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv:  ## Create and setup virtual environment
	python3 -m venv .venv
	.venv/bin/pip install -U pip wheel
	.venv/bin/pip install -r requirements.txt
	@echo "Virtual environment ready. Activate with: source .venv/bin/activate"

install:  ## Install dependencies in current environment
	pip install -U pip wheel
	pip install -r requirements.txt

demo:  ## Run in demo mode (no AirSim needed)
	RUN_MODE=demo python -m src.main

live:  ## Run in live mode (requires AirSim)
	RUN_MODE=live AIRSIM_HOST=127.0.0.1 AIRSIM_PORT=41451 ./scripts/run_live.sh

test:  ## Run tests
	python -m pytest tests/ -v

lint:  ## Run linting
	flake8 src/ scripts/
	black --check src/ scripts/

format:  ## Format code
	black src/ scripts/

clean:  ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f drone_vision.log
