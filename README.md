# 🚁 Drone Vision AirSim Project

A streamlined and efficient UAV simulation project using AirSim for autonomous drone flight with computer vision capabilities.

## 🎯 Project Goals

- **Efficient UAV Simulation**: High-performance drone simulation using AirSim
- **Computer Vision Integration**: Real-time object detection and target tracking
- **Autonomous Navigation**: Waypoint-based patrol and mission execution
- **Clean Architecture**: Streamlined, maintainable codebase

## 🏗️ Architecture

### Core Components

- **`main.py`**: Entry point and simulation orchestration
- **`flight_control.py`**: AirSim drone control and sensor data collection
- **`mission_logic.py`**: Mission planning and waypoint navigation
- **`vision_targeting.py`**: Computer vision processing and object detection
- **`utils/config.py`**: Configuration management

### Key Features

- **Simplified State Management**: Removed complex state machines for better performance
- **Efficient Vision Processing**: Basic contour-based object detection
- **Streamlined Configuration**: Essential settings only
- **Minimal Dependencies**: Reduced package requirements

## 🚀 Quick Start

### Live Run (Cloud)

For real drone control with AirSim on cloud:

```bash
# Start GCP VM and connect
gcloud compute instances start airsim-gpu --zone=us-central1-a
gcloud compute ssh airsim-gpu --zone=us-central1-a

# Setup VNC and AirSim (see docs/QUICKSTART_CLOUD.md)
vncserver :1 -localhost yes -geometry 1600x900 -depth 24 -xstartup /usr/bin/startxfce4

# Run live simulation
cd ~/sim-drone && git pull
source .venv/bin/activate
RUN_MODE=live scripts/run_live.sh
```

### Demo Mode (Local)

For testing without AirSim:

```bash
# Clone and setup
git clone https://github.com/hollowman010/sim-drone.git
cd sim-drone
make venv  # or: python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
make install  # or: pip install -r requirements.txt

# Run demo (no AirSim needed)
make demo  # or: RUN_MODE=demo python -m src.main
```

### Prerequisites

- **Cloud**: GCP account with GPU quota
- **Local**: Python 3.8+, for demo mode only
- **Live**: AirSim running on target system

### Quick Commands

```bash
make help     # Show available commands
make demo     # Run demo mode
make live     # Run live mode (needs AirSim)
make venv     # Setup virtual environment
```

## 📁 Project Structure

```
src/
├── main.py              # Main entry point
├── flight_control.py    # Drone control and sensors
├── mission_logic.py     # Mission planning
├── vision_targeting.py  # Computer vision
└── utils/
    └── config.py        # Configuration management

config/
└── settings.json        # Configuration file

requirements.txt         # Python dependencies
```

## 🔧 Configuration

Edit `config/settings.json` to customize:

- **AirSim Connection**: Host, port, timeout
- **Drone Control**: Speed limits, safety distances
- **Vision Processing**: Object detection parameters
- **Mission Settings**: Duration, waypoints, thresholds

## 🎮 Usage

### Basic Patrol Mission

The system automatically:
1. Connects to AirSim
2. Takes off to specified altitude
3. Follows predefined waypoints
4. Detects objects using computer vision
5. Lands when mission completes

### Custom Waypoints

Modify the waypoint list in `main.py`:

```python
patrol_waypoints = [
    (0, 0, 20),    # Start position
    (50, 0, 20),   # Forward
    (50, 50, 20),  # Right
    (0, 50, 20),   # Back
    (0, 0, 20),    # Return to start
]
```

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/
```

## 📊 Performance Improvements

### Before Refactoring
- Complex state machine (8 states)
- Multiple image processing pipelines
- Heavy ML dependencies
- Redundant logging systems
- Over-engineered configuration

### After Refactoring
- Simple patrol logic
- Single RGB image processing
- Minimal dependencies
- Streamlined logging
- Essential configuration only

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Microsoft AirSim team for the excellent simulation platform
- OpenCV community for computer vision tools
- Contributors and maintainers
