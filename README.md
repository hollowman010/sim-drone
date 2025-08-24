# Drone Vision - AirSim Simulation Project

A drone simulation project using Microsoft AirSim for autonomous drone development and computer vision applications.

## Overview

This project provides a framework for developing and testing drone control algorithms, computer vision applications, and autonomous navigation using Microsoft AirSim simulation environment.

## Features

- AirSim integration for realistic drone simulation
- Computer vision processing pipeline
- Autonomous navigation algorithms
- Flight control systems
- Data collection and analysis tools

## Prerequisites

- Python 3.8+
- Microsoft AirSim (Windows 10/11)
- Unreal Engine 4.27+ (for AirSim)
- Git

## Installation

### 1. Install AirSim

Download and install AirSim from the official repository:
- Visit: https://github.com/microsoft/AirSim
- Follow the installation guide for your platform

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment

```bash
# Copy environment configuration
cp config/settings.example.json config/settings.json
# Edit settings.json with your configuration
```

## Usage

### Starting AirSim

1. Launch Unreal Engine with AirSim
2. Load your desired environment
3. Start the simulation

### Running the Drone Vision System

```bash
python src/main.py
```

### Running Tests

```bash
python -m pytest tests/
```

## Project Structure

```
UAV-Sim-Project/
├── README.md                       # Overview of the project and instructions
├── settings.json                   # AirSim settings for the simulation (UAV, sensors, environment)
├── requirements.txt                # Python dependencies (AirSim API, ML libs, etc.)
├── src/
│   ├── main.py                     # Main script to run the simulation
│   ├── flight_control.py           # Drone control functions (wraps AirSim API)
│   ├── vision_targeting.py         # Computer vision model and image processing
│   ├── mission_logic.py            # High-level mission strategy and decisions
│   └── utils/
│       ├── logger.py               # Logging utility
│       └── config.py               # Config parsing (if needed)
├── models/                         # (Optional) pre-trained models or data for the vision system
├── tests/                          # (Optional) test scripts for CI (unit tests or small integration tests)
├── docker/                         # (Optional) Dockerfile and related scripts if containerizing
└── docs/                           # (Optional) documentation, design notes, etc.
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Microsoft AirSim team for the simulation platform
- Open source computer vision community
# CI/CD Pipeline Test
