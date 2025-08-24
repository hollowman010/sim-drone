#!/usr/bin/env python3
"""
Demo script for the Drone Vision AirSim project.
This script demonstrates the project structure and components without requiring AirSim.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import load_config, get_default_config
from src.utils.logger import setup_logging, DroneVisionLogger
from src.vision_targeting import VisionProcessor
from src.mission_logic import MissionLogic, Waypoint


def demo_configuration():
    """Demonstrate configuration loading."""
    print("🔧 Configuration Demo")
    print("=" * 50)
    
    # Load default configuration
    config = get_default_config()
    
    print(f"AirSim Host: {config['airsim']['host']}")
    print(f"AirSim Port: {config['airsim']['port']}")
    print(f"Max Drone Speed: {config['drone']['max_speed']} m/s")
    print(f"Patrol Altitude: {config['drone']['takeoff_height']} m")
    print(f"Obstacle Avoidance: {config['navigation']['obstacle_avoidance']}")
    print()


def demo_logging():
    """Demonstrate logging functionality."""
    print("📝 Logging Demo")
    print("=" * 50)
    
    # Setup logger
    config = get_default_config()
    logger = setup_logging(config)
    
    # Log various events
    logger.info("Demo started successfully")
    logger.log_mission_event("demo_mission_started", (0, 0, 10))
    logger.log_sensor_data("demo_sensor", {"temperature": 25.5, "humidity": 60})
    logger.log_vision_result([{"type": "car", "confidence": 0.8}], [], True)
    
    print("✅ Logging demo completed - check drone_vision.log for details")
    print()


def demo_vision_processing():
    """Demonstrate vision processing."""
    print("👁️ Vision Processing Demo")
    print("=" * 50)
    
    config = get_default_config()
    vision_processor = VisionProcessor(config)
    
    # Simulate sensor data
    import numpy as np
    
    # Create dummy images
    rgb_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    depth_image = np.random.random((480, 640)).astype(np.float32)
    seg_image = np.random.randint(0, 10, (480, 640), dtype=np.uint8)
    
    sensor_data = {
        "position": None,
        "orientation": None,
        "velocity": None,
        "images": {
            "image_0": rgb_image,
            "image_1": depth_image,
            "image_2": seg_image
        },
        "gps": None,
        "collision": None
    }
    
    # Process vision data
    results = vision_processor.process(sensor_data)
    
    print(f"Objects Detected: {len(results['objects_detected'])}")
    print(f"Obstacles Found: {len(results['obstacles'])}")
    print(f"Landing Zones: {len(results['landing_zones'])}")
    print(f"Path Clear: {results['path_clearance']}")
    print()


def demo_navigation():
    """Demonstrate navigation system."""
    print("🧭 Navigation Demo")
    print("=" * 50)
    
    config = get_default_config()
    mission_logic = MissionLogic(config)
    
    # Add waypoints
    waypoints = [
        Waypoint(0, 0, 20),
        Waypoint(50, 0, 20),
        Waypoint(50, 50, 20),
        Waypoint(0, 50, 20),
        Waypoint(0, 0, 20)
    ]
    
    # Start mission
    patrol_waypoints = [(wp.x, wp.y, wp.z) for wp in waypoints]
    mission_logic.start_mission(patrol_waypoints)
    
    # Simulate vision results
    vision_results = {
        "objects_detected": [],
        "obstacles": [],
        "landing_zones": [],
        "path_clearance": True,
        "image_processed": True
    }
    
    # Get navigation commands
    commands = mission_logic.update(vision_results, (0, 0, 20))
    
    print(f"Mission Action: {commands['action']}")
    print(f"Reason: {commands['reason']}")
    
    # Get mission status
    status = mission_logic.get_mission_status()
    print(f"Current Waypoint: {status['current_patrol_index']}/{status['total_patrol_waypoints']}")
    print(f"Mission Complete: {status['patrol_completed']}")
    print()


def demo_mission_logic():
    """Demonstrate mission logic."""
    print("🎯 Mission Logic Demo")
    print("=" * 50)
    
    config = get_default_config()
    mission_logic = MissionLogic(config)
    
    # Define patrol waypoints
    patrol_waypoints = [
        (0, 0, 20),
        (50, 0, 20),
        (50, 50, 20),
        (0, 50, 20)
    ]
    
    # Start mission
    mission_logic.start_mission(patrol_waypoints)
    
    # Simulate different scenarios
    scenarios = [
        {
            "name": "Normal Patrol",
            "vision_results": {"objects_detected": [], "obstacles": [], "path_clearance": True},
            "position": (0, 0, 20)
        },
        {
            "name": "Target Detected",
            "vision_results": {
                "objects_detected": [{"type": "target", "confidence": 0.9, "bbox": [100, 100, 50, 50]}],
                "obstacles": [],
                "path_clearance": True
            },
            "position": (25, 0, 20)
        },
        {
            "name": "Obstacle Ahead",
            "vision_results": {
                "objects_detected": [],
                "obstacles": [{"area": 1000, "centroid": [320, 240]}],
                "path_clearance": False
            },
            "position": (50, 0, 20)
        }
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        commands = mission_logic.update(scenario['vision_results'], scenario['position'])
        print(f"  Action: {commands['action']}")
        print(f"  Reason: {commands['reason']}")
        
        status = mission_logic.get_mission_status()
        print(f"  State: {status['state']}")
        print(f"  Target Detected: {status['target_detected']}")
    
    print()


def main():
    """Run all demos."""
    print("🚁 Drone Vision AirSim Project Demo")
    print("=" * 60)
    print("This demo shows the project structure and components working together.")
    print("Note: This is a simulation - AirSim is not required for this demo.\n")
    
    try:
        demo_configuration()
        demo_logging()
        demo_vision_processing()
        demo_navigation()
        demo_mission_logic()
        
        print("🎉 All demos completed successfully!")
        print("\nNext steps:")
        print("1. Install AirSim (Windows 10/11 with Unreal Engine)")
        print("2. Copy settings.json to your AirSim Documents folder")
        print("3. Run: python3 src/main.py")
        print("\nFor more information, see the README.md file.")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
