"""
Configuration settings for the Drone Vision AirSim project.
Streamlined configuration management with dataclass structure.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

# Runtime configuration from environment
RUN_MODE = os.getenv("RUN_MODE", "live")  # "live" or "demo"
AIRSIM_HOST = os.getenv("AIRSIM_HOST", "127.0.0.1")
AIRSIM_PORT = int(os.getenv("AIRSIM_PORT", "41451"))
TAKEOFF_ALT = float(os.getenv("TAKEOFF_ALT", "5.0"))

# AirSim Documents directory
DOCS_AIRSIM = Path.home() / "Documents" / "AirSim"


@dataclass
class AppConfig:
    """Application configuration dataclass."""
    airsim_host: str = AIRSIM_HOST
    airsim_port: int = AIRSIM_PORT
    vehicle_name: str = os.getenv("AIRSIM_VEHICLE", "Drone1")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    takeoff_altitude: float = TAKEOFF_ALT
    max_speed: float = 10.0
    safety_distance: float = 5.0


def write_settings_json(settings: dict, folder: Optional[Path] = None) -> Path:
    """Write AirSim settings.json file.
    
    Args:
        settings: Settings dictionary
        folder: Target folder (defaults to ~/Documents/AirSim)
        
    Returns:
        Path to written settings file
    """
    folder = folder or DOCS_AIRSIM
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "settings.json"
    path.write_text(json.dumps(settings, indent=2))
    return path


def default_airsim_settings() -> dict:
    """Get default AirSim settings.
    
    Returns:
        Default settings dictionary
    """
    return {
        "SettingsVersion": 1.2,
        "SimMode": "Multirotor",
        "RpcEnabled": True,
        "ViewMode": "NoDisplay",
        "ApiServerPort": AIRSIM_PORT,
        "LocalHostIp": "0.0.0.0",
        "Vehicles": {
            "Drone1": {
                "VehicleType": "SimpleFlight", 
                "AutoCreate": True
            }
        }
    }


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
            "host": AIRSIM_HOST, 
            "port": AIRSIM_PORT, 
            "timeout": 10.0
        },
        
        # Drone control settings
        "drone": {
            "max_speed": 10.0,
            "takeoff_height": TAKEOFF_ALT,
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