"""
Drone Controller module for AirSim integration.
Handles drone control, sensor data collection, and flight commands.
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
            if self.client is None:
                raise RuntimeError("Client not initialized")
            state = self.client.getMultirotorState()

            # Get camera images
            responses = self.client.simGetImages(
                [
                    airsim.ImageRequest("0", airsim.ImageType.Scene),
                    airsim.ImageRequest("1", airsim.ImageType.DepthVis),
                    airsim.ImageRequest("2", airsim.ImageType.Segmentation),
                ]
            )

            # Process images
            images = {}
            for i, response in enumerate(responses):
                if response.pixels_as_float:
                    images[f"image_{i}"] = np.array(response.image_data_float).reshape(
                        response.height, response.width
                    )
                else:
                    images[f"image_{i}"] = (
                        np.frombuffer(response.image_data_uint8, dtype=np.uint8)
                        .reshape(response.height, response.width, 3)
                        .astype(np.uint8)
                    )

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
            if self.client is None:
                self.logger.error("Client not initialized")
                return

            # Handle different command types
            if commands.get("action") == "move_to_position":
                pos = commands["parameters"]
                self.client.moveToPositionAsync(
                    pos["x"], pos["y"], pos["z"], pos["speed"]
                )

            elif commands.get("action") == "move_by_velocity":
                vel = commands["parameters"]
                self.client.moveByVelocityAsync(
                    vel["vx"], vel["vy"], vel["vz"], vel["duration"]
                )

            elif commands.get("action") == "hover":
                self.client.hoverAsync()

            elif commands.get("action") == "takeoff":
                self.takeoff()

            elif commands.get("action") == "land":
                self.land()

        except Exception as e:
            self.logger.error(f"Failed to execute commands: {e}")

    def get_position(self) -> Optional[airsim.Vector3r]:
        """Get current drone position."""
        if not self.is_connected:
            return None

        try:
            if self.client is None:
                return None
            state = self.client.getMultirotorState()
            return state.kinematics_estimated.position
        except Exception as e:
            self.logger.error(f"Failed to get position: {e}")
            return None
