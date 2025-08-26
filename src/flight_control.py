"""
Drone Controller module for AirSim integration.
Streamlined and efficient drone control implementation.
"""

import airsim
import logging
from typing import Dict, Any, Optional
import numpy as np


class DroneController:
    """Controls the drone in AirSim simulation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the drone controller.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.client = None
        self.logger = logging.getLogger(__name__)
        self.is_connected = False

    def connect(self):
        """Connect to AirSim client."""
        try:
            self.client = airsim.MultirotorClient()
            self.client.confirmConnection()
            self.client.enableApiControl(True)
            self.client.armDisarm(True)
            self.is_connected = True
            self.logger.info("Successfully connected to AirSim")
        except Exception as e:
            self.logger.error(f"Failed to connect to AirSim: {e}")
            raise

    def disconnect(self):
        """Disconnect from AirSim."""
        if self.client:
            self.client.enableApiControl(False)
            self.client = None
            self.is_connected = False
            self.logger.info("Disconnected from AirSim")

    def takeoff(self):
        """Take off the drone."""
        if not self.is_connected:
            raise RuntimeError("Not connected to AirSim")

        try:
            self.client.takeoffAsync().join()
            self.logger.info("Drone took off successfully")
        except Exception as e:
            self.logger.error(f"Takeoff failed: {e}")
            raise

    def land(self):
        """Land the drone."""
        if not self.is_connected:
            return

        try:
            self.client.landAsync().join()
            self.logger.info("Drone landed successfully")
        except Exception as e:
            self.logger.error(f"Landing failed: {e}")

    def get_sensor_data(self) -> Dict[str, Any]:
        """Get sensor data from the drone.

        Returns:
            Dictionary containing sensor data
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to AirSim")

        try:
            # Get drone state
            state = self.client.getMultirotorState()

            # Get camera images (only RGB for efficiency)
            responses = self.client.simGetImages([
                airsim.ImageRequest("0", airsim.ImageType.Scene)
            ])

            # Process RGB image
            images = {}
            if responses and responses[0].image_data_uint8:
                image_data = np.frombuffer(
                    responses[0].image_data_uint8, dtype=np.uint8
                ).reshape(responses[0].height, responses[0].width, 3)
                images["rgb"] = image_data

            return {
                "position": state.kinematics_estimated.position,
                "orientation": state.kinematics_estimated.orientation,
                "velocity": state.kinematics_estimated.linear_velocity,
                "images": images,
                "gps": state.gps_location,
                "collision": state.collision,
            }

        except Exception as e:
            self.logger.error(f"Failed to get sensor data: {e}")
            raise

    def execute_commands(self, commands: Dict[str, Any]):
        """Execute mission commands.

        Args:
            commands: Dictionary containing mission commands
        """
        if not self.is_connected:
            return

        try:
            action = commands.get("action")
            
            if action == "move_to_position":
                pos = commands["position"]
                speed = commands.get("speed", 5.0)
                self.client.moveToPositionAsync(pos[0], pos[1], pos[2], speed)

            elif action == "move_by_velocity":
                vel = commands["parameters"]
                self.client.moveByVelocityAsync(
                    vel["vx"], vel["vy"], vel["vz"], vel["duration"]
                )

            elif action == "hover":
                self.client.hoverAsync()

            elif action == "takeoff":
                self.takeoff()

            elif action == "land":
                self.land()

        except Exception as e:
            self.logger.error(f"Failed to execute commands: {e}")

    def get_position(self) -> Optional[airsim.Vector3r]:
        """Get current drone position."""
        if not self.is_connected:
            return None

        try:
            state = self.client.getMultirotorState()
            return state.kinematics_estimated.position
        except Exception as e:
            self.logger.error(f"Failed to get position: {e}")
            return None
