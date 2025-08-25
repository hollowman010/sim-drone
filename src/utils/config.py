"""
Configuration settings for the Drone Vision AirSim project.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
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
        "airsim": {"host": "127.0.0.1", "port": 41451, "timeout": 10.0},
        # Drone control settings
        "drone": {
            "max_speed": 10.0,
            "takeoff_height": 5.0,
            "safety_distance": 5.0,
            "emergency_landing_height": 2.0,
        },
        # Vision processing settings
        "vision": {
            "min_object_area": 100,
            "obstacle_threshold": 0.3,
            "min_landing_area": 1000,
            "detection_model_path": None,
            "segmentation_model_path": None,
        },
        # Navigation settings
        "navigation": {
            "obstacle_avoidance": True,
            "safety_distance": 5.0,
            "max_speed": 10.0,
            "waypoint_tolerance": 2.0,
        },
        # Logging settings
        "logging": {
            "level": "INFO",
            "file": "drone_vision.log",
            "max_size": "10MB",
            "backup_count": 5,
        },
        # Data collection settings
        "data_collection": {
            "enabled": True,
            "save_images": True,
            "save_sensor_data": True,
            "output_dir": "data/collected",
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


def update_config(updates: Dict[str, Any], config_path: str = "config/settings.json"):
    """Update configuration with new values.

    Args:
        updates: Dictionary containing configuration updates
        config_path: Path to configuration file
    """
    config = load_config(config_path)

    # Recursively update nested dictionaries
    def update_nested(base_dict, update_dict):
        for key, value in update_dict.items():
            if (
                key in base_dict
                and isinstance(base_dict[key], dict)
                and isinstance(value, dict)
            ):
                update_nested(base_dict[key], value)
            else:
                base_dict[key] = value

    update_nested(config, updates)
    save_config(config, config_path)
