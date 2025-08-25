"""
Basic tests for the Drone Vision AirSim project.
"""

import sys
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))
sys.path.append(str(Path(__file__).parent.parent))

# Import src modules after path setup
try:
    from src.utils.config import get_default_config
    from src.utils.logger import DroneVisionLogger
except ImportError:
    # Fallback for when src is not in path
    pass


class TestConfiguration(unittest.TestCase):
    """Test configuration loading and defaults."""

    def test_default_config(self):
        """Test that default configuration is loaded correctly."""
        config = get_default_config()

        # Check that required sections exist
        self.assertIn("airsim", config)
        self.assertIn("drone", config)
        self.assertIn("vision", config)
        self.assertIn("navigation", config)

        # Check some specific values
        self.assertEqual(config["airsim"]["host"], "127.0.0.1")
        self.assertEqual(config["airsim"]["port"], 41451)
        self.assertGreater(config["drone"]["max_speed"], 0)

    def test_config_structure(self):
        """Test configuration structure is valid."""
        config = get_default_config()

        # Test nested structure
        self.assertIsInstance(config["vision"]["min_object_area"], int)
        self.assertIsInstance(config["navigation"]["obstacle_avoidance"], bool)
        self.assertIsInstance(config["logging"]["level"], str)


class TestLogger(unittest.TestCase):
    """Test logging functionality."""

    def test_logger_creation(self):
        """Test that logger can be created."""
        logger = DroneVisionLogger("test_logger")
        self.assertIsNotNone(logger)

    def test_logger_methods(self):
        """Test logger methods work without errors."""
        logger = DroneVisionLogger("test_logger")

        # Test all logging methods
        logger.info("Test info message")
        logger.debug("Test debug message")
        logger.warning("Test warning message")
        logger.error("Test error message")

        # Test structured logging
        logger.log_event("test", {"key": "value"})
        logger.log_mission_event("test_mission", (0, 0, 0))
        logger.log_sensor_data("test_sensor", {"data": "value"})
        logger.log_vision_result([], [], True)


if __name__ == "__main__":
    unittest.main()
