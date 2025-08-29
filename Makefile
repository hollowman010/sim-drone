# ----- config -----
PY        := python3
VENV      := .venv
PIP       := $(VENV)/bin/pip
PYBIN     := $(VENV)/bin/python

PROJECT   ?= drone-sim-project
ZONE      ?= us-central1-a
INSTANCE  ?= airsim-gpu

# ----- basic env -----
.PHONY: help venv install settings fmt lint test clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv:  ## Create virtual environment
	$(PY) -m venv $(VENV)

install: venv  ## Install dependencies
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt

settings:  ## Copy AirSim settings to user directory
	mkdir -p $$HOME/Documents/AirSim
	# Copy the correct AirSim server config (not the app config)
	cp -f scripts/quick_settings.json $$HOME/Documents/AirSim/settings.json 2>/dev/null || true
	@echo "✅ AirSim server settings copied"

fmt:  ## Format code with black and ruff
	$(PIP) install -q black ruff || true
	$(PYBIN) -m black src tests scripts || true
	$(PYBIN) -m ruff format src tests scripts || true

lint:  ## Lint code with ruff
	$(PIP) install -q ruff || true
	$(PYBIN) -m ruff check src tests scripts || true

test:  ## Run tests with pytest
	$(PIP) install -q pytest || true
	$(PYBIN) -m pytest -q

clean:  ## Clean up build artifacts
	rm -rf $(VENV) *.egg-info build dist
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# ----- sim flow -----
.PHONY: smoke sim demo

smoke: install settings  ## Quick smoke test (takeoff/hover/land)
	$(PYBIN) scripts/airsim_takeoff.py

sim: install settings  ## Run full simulation with real AirSim
	cd src && $(PYBIN) main.py --mode=live

demo: install  ## Run demo mode (no AirSim needed)
	cd src && $(PYBIN) main.py --mode=demo

# ----- gcp helpers -----
.PHONY: up tunnel down status

up:  ## Start GCP VM and VNC
	@echo "🚀 Starting VM and VNC..."
	gcloud compute instances start $(INSTANCE) --zone=$(ZONE)
	gcloud compute ssh $(INSTANCE) --zone=$(ZONE) --command \
	  "vncserver -kill :1 || true; vncserver :1 -localhost yes -geometry 1600x900 -depth 24 -xstartup /usr/bin/startxfce4"
	@echo "✅ VM started. Run 'make tunnel' in another terminal, then connect VNC to localhost:5901"

tunnel:  ## Open SSH tunnel for VNC (keep terminal open)
	@echo "🔗 Opening SSH tunnel... Connect VNC to localhost:5901"
	gcloud compute ssh $(INSTANCE) --zone=$(ZONE) -- \
	  -N -L 5901:localhost:5901 \
	  -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3

down:  ## Stop AirSim and VM
	@echo "🛑 Stopping AirSim and VM..."
	# Try gracefully stopping AirSim + VNC, then stop the VM
	gcloud compute ssh $(INSTANCE) --zone=$(ZONE) --command \
	  "pkill -f Blocks || true; vncserver -kill :1 || true" || true
	gcloud compute instances stop $(INSTANCE) --zone=$(ZONE)
	@echo "✅ VM stopped"

status:  ## Check VM status
	gcloud compute instances describe $(INSTANCE) --zone=$(ZONE) --format='get(status)'