"""
Logging utility for the Drone Vision AirSim project.
Provides standardized logging across all modules.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import json
from datetime import datetime


class DroneVisionLogger:
    """Custom logger for Drone Vision project."""

    def __init__(
        self, name: str, log_file: str = "drone_vision.log", level: str = "INFO"
    ):
        """Initialize the logger.

        Args:
            name: Logger name
            log_file: Log file path
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        simple_formatter = logging.Formatter("%(levelname)s - %(message)s")

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)

        # File handler with rotation
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)

    def log_event(self, event_type: str, data: dict):
        """Log structured event data.

        Args:
            event_type: Type of event
            data: Event data dictionary
        """
        event_log = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data,
        }
        self.logger.info(f"EVENT: {json.dumps(event_log)}")

    def log_mission_event(
        self,
        event: str,
        position: Optional[tuple] = None,
        target_info: Optional[dict] = None,
    ):
        """Log mission-specific events.

        Args:
            event: Mission event description
            position: Drone position (x, y, z)
            target_info: Target information if applicable
        """
        data = {"event": event}
        if position:
            data["position"] = position
        if target_info:
            data["target_info"] = target_info

        self.log_event("mission", data)

    def log_sensor_data(self, sensor_type: str, data: dict):
        """Log sensor data.

        Args:
            sensor_type: Type of sensor
            data: Sensor data
        """
        self.log_event("sensor", {"sensor_type": sensor_type, "data": data})

    def log_vision_result(
        self, objects_detected: list, obstacles: list, path_clearance: bool
    ):
        """Log vision processing results.

        Args:
            objects_detected: List of detected objects
            obstacles: List of detected obstacles
            path_clearance: Whether path is clear
        """
        self.log_event(
            "vision",
            {
                "objects_detected": len(objects_detected),
                "obstacles": len(obstacles),
                "path_clearance": path_clearance,
            },
        )


def setup_logging(config: dict) -> DroneVisionLogger:
    """Setup logging based on configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Configured logger instance
    """
    logging_config = config.get("logging", {})
    log_file = logging_config.get("file", "drone_vision.log")
    log_level = logging_config.get("level", "INFO")

    return DroneVisionLogger("drone_vision", log_file, log_level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance by name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
