#!/usr/bin/env python3
"""
Main entry point for the Drone Vision AirSim simulation project.
"""

import logging
import sys
from pathlib import Path

from flight_control import DroneController
from mission_logic import MissionLogic
from utils.config import load_config
from utils.logger import setup_logging
from vision_targeting import VisionProcessor

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))


def setup_logging_config():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("drone_vision.log"), logging.StreamHandler()],
    )


def main():
    """Main application function."""
    import sys
    
    setup_logging_config()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting Drone Vision AirSim Simulation")

        # Load configuration
        config_path = sys.argv[1] if len(sys.argv) > 1 else None
        config = load_config(config_path)
        logger.info("Configuration loaded successfully")

        # Setup logging
        drone_logger = setup_logging(config)

        # Initialize components
        drone_controller = DroneController(config)
        vision_processor = VisionProcessor(config)
        mission_logic = MissionLogic(config)

        logger.info("All components initialized")

        # Main simulation loop
        logger.info("Starting simulation loop")
        run_simulation(drone_controller, vision_processor, mission_logic, drone_logger)

    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    except Exception as e:
        logger.error(f"Error in main application: {e}")
        raise
    finally:
        logger.info("Shutting down Drone Vision system")


def run_simulation(drone_controller, vision_processor, mission_logic, drone_logger):
    """Run the main simulation loop."""
    logger = logging.getLogger(__name__)

    try:
        # Connect to AirSim
        drone_controller.connect()
        logger.info("Connected to AirSim")

        # Define patrol waypoints (example)
        patrol_waypoints = [
            (0, 0, 20),  # Start position
            (50, 0, 20),  # Forward
            (50, 50, 20),  # Right
            (0, 50, 20),  # Back
            (0, 0, 20),  # Return to start
        ]

        # Start mission
        mission_logic.start_mission(patrol_waypoints)
        drone_logger.log_mission_event("mission_started", patrol_waypoints[0])

        # Take off
        drone_controller.takeoff()
        logger.info("Drone took off successfully")

        # Main simulation loop
        while True:
            # Get sensor data
            sensor_data = drone_controller.get_sensor_data()
            drone_logger.log_sensor_data(
                "drone_state",
                {
                    "position": str(sensor_data.get("position", "unknown")),
                    "velocity": str(sensor_data.get("velocity", "unknown")),
                },
            )

            # Process vision data
            vision_results = vision_processor.process(sensor_data)
            drone_logger.log_vision_result(
                vision_results.get("objects_detected", []),
                vision_results.get("obstacles", []),
                vision_results.get("path_clearance", True),
            )

            # Get current position for mission logic
            current_position = drone_controller.get_position()
            if current_position:
                position_tuple = (
                    current_position.x_val,
                    current_position.y_val,
                    current_position.z_val,
                )
            else:
                position_tuple = (0, 0, 0)

            # Update mission logic
            mission_commands = mission_logic.update(vision_results, position_tuple)

            # Execute mission commands
            drone_controller.execute_commands(mission_commands)

            # Log mission status
            mission_status = mission_logic.get_mission_status()
            if mission_status["state"] == "completed":
                logger.info("Mission completed successfully")
                break

    except Exception as e:
        logger.error(f"Error in simulation loop: {e}")
        raise
    finally:
        # Land and disconnect
        drone_controller.land()
        drone_controller.disconnect()
        logger.info("Disconnected from AirSim")


if __name__ == "__main__":
    main()
