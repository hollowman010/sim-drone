#!/usr/bin/env python3
"""
Main entry point for the Drone Vision AirSim simulation project.
Streamlined and efficient implementation.
"""

import logging
import sys
from pathlib import Path

from flight_control import DroneController
from mission_logic import MissionLogic
from vision_targeting import VisionProcessor
from utils.config import load_config

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))


def setup_logging():
    """Setup simple logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("drone_vision.log"),
            logging.StreamHandler()
        ],
    )


def main():
    """Main application function."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting Drone Vision AirSim Simulation")

        # Load configuration
        config_path = sys.argv[1] if len(sys.argv) > 1 else None
        config = load_config(config_path)
        logger.info("Configuration loaded successfully")

        # Initialize components
        drone_controller = DroneController(config)
        vision_processor = VisionProcessor(config)
        mission_logic = MissionLogic(config)

        logger.info("All components initialized")

        # Run simulation
        run_simulation(drone_controller, vision_processor, mission_logic, logger)

    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
    except Exception as e:
        logger.error(f"Error in main application: {e}")
        raise
    finally:
        logger.info("Shutting down Drone Vision system")


def run_simulation(drone_controller, vision_processor, mission_logic, logger):
    """Run the main simulation loop."""
    try:
        # Connect to AirSim
        drone_controller.connect()
        logger.info("Connected to AirSim")

        # Define patrol waypoints
        patrol_waypoints = [
            (0, 0, 20),    # Start position
            (50, 0, 20),   # Forward
            (50, 50, 20),  # Right
            (0, 50, 20),   # Back
            (0, 0, 20),    # Return to start
        ]

        # Start mission
        mission_logic.start_mission(patrol_waypoints)
        logger.info("Mission started")

        # Take off
        drone_controller.takeoff()
        logger.info("Drone took off successfully")

        # Main simulation loop
        while True:
            # Get sensor data
            sensor_data = drone_controller.get_sensor_data()
            
            # Process vision data
            vision_results = vision_processor.process(sensor_data)
            
            # Get current position
            current_position = drone_controller.get_position()
            position_tuple = (
                current_position.x_val,
                current_position.y_val,
                current_position.z_val,
            ) if current_position else (0, 0, 0)

            # Update mission logic and execute commands
            mission_commands = mission_logic.update(vision_results, position_tuple)
            drone_controller.execute_commands(mission_commands)

            # Check mission completion
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
