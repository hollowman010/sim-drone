"""
Configuration settings for the Drone Vision AirSim project.
Streamlined configuration management.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or return defaults.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = "config/settings.json"

    # Try to load from file
    if Path(config_path).exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")

    # Return default configuration
    return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """Get default configuration settings.

    Returns:
        Default configuration dictionary
    """
    return {
        # AirSim connection settings
        "airsim": {
            "host": "127.0.0.1", 
            "port": 41451, 
            "timeout": 10.0
        },
        
        # Drone control settings
        "drone": {
            "max_speed": 10.0,
            "takeoff_height": 5.0,
            "safety_distance": 5.0,
        },
        
        # Vision processing settings
        "vision": {
            "min_object_area": 100,
        },
        
        # Mission settings
        "mission": {
            "max_mission_duration": 1800,  # 30 minutes
            "target_detection_threshold": 0.7,
            "waypoint_tolerance": 2.0,
        },
        
        # Logging settings
        "logging": {
            "level": "INFO",
            "file": "drone_vision.log",
        },
    }


def save_config(config: Dict[str, Any], config_path: str = "config/settings.json"):
    """Save configuration to file.

    Args:
        config: Configuration dictionary
        config_path: Path to save configuration file
    """
    try:
        # Ensure directory exists
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"Configuration saved to {config_path}")

    except Exception as e:
        print(f"Error saving configuration: {e}")
