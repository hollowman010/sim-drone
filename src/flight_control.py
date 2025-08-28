"""
Drone Controller module for AirSim integration.
Streamlined and efficient drone control implementation.
"""

import logging
from typing import Dict, Any, Optional
import numpy as np

# Try to import AirSim, fallback to mock if not available
try:
    import airsim
    AIRSIM_AVAILABLE = True
except ImportError:
    AIRSIM_AVAILABLE = False
    print("Warning: AirSim not available. Using mock client for testing.")
    
    # Create a mock airsim module for testing
    class MockVector3r:
        def __init__(self, x=0, y=0, z=0):
            self.x_val = x
            self.y_val = y
            self.z_val = z
    
    class MockAirSimClient:
        def __init__(self):
            self.position = MockVector3r(0, 0, 20)
            self.velocity = MockVector3r(0, 0, 0)
            self.orientation = MockVector3r(0, 0, 0)
        
        def confirmConnection(self):
            return True
        
        def enableApiControl(self, enabled):
            return True
        
        def armDisarm(self, armed):
            return True
        
        def takeoffAsync(self):
            return MockAsyncTask()
        
        def landAsync(self):
            return MockAsyncTask()
        
        def hoverAsync(self):
            return MockAsyncTask()
        
        def moveToPositionAsync(self, x, y, z, speed):
            self.position = MockVector3r(x, y, z)
            return MockAsyncTask()
        
        def moveByVelocityAsync(self, vx, vy, vz, duration):
            self.velocity = MockVector3r(vx, vy, vz)
            return MockAsyncTask()
        
        def getMultirotorState(self):
            return MockMultirotorState(self.position, self.velocity, self.orientation)
        
        def simGetImages(self, requests):
            # Return mock image data
            mock_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            return [MockImageResponse(mock_image)]
    
    class MockAsyncTask:
        def join(self):
            return True
    
    class MockMultirotorState:
        def __init__(self, position, velocity, orientation):
            self.kinematics_estimated = MockKinematics(position, velocity, orientation)
            self.gps_location = MockGPS()
            self.collision = MockCollision()
    
    class MockKinematics:
        def __init__(self, position, velocity, orientation):
            self.position = position
            self.linear_velocity = velocity
            self.orientation = orientation
    
    class MockGPS:
        def __init__(self):
            self.latitude = 0
            self.longitude = 0
            self.altitude = 0
    
    class MockCollision:
        def __init__(self):
            self.has_collided = False
    
    class MockImageResponse:
        def __init__(self, image_data):
            self.image_data_uint8 = image_data.tobytes()
            self.height = image_data.shape[0]
            self.width = image_data.shape[1]
            self.pixels_as_float = False
    
    # Create mock airsim module
    class MockImageRequest:
        def __init__(self, name, img_type):
            self.name = name
            self.img_type = img_type
    
    airsim = type('MockAirSim', (), {
        'MultirotorClient': MockAirSimClient,
        'Vector3r': MockVector3r,
        'ImageRequest': MockImageRequest,
        'ImageType': type('MockImageType', (), {'Scene': 0})()
    })()


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

            # Get camera images (only RGB for efficiency) - request uncompressed data
            responses = self.client.simGetImages([
                airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)  # pixels_as_float=False, compress=False
            ])

            # Process RGB image
            images = {}
            if responses and responses[0].image_data_uint8:
                try:
                    # Calculate expected size based on actual dimensions
                    expected_size = responses[0].height * responses[0].width * 3
                    actual_size = len(responses[0].image_data_uint8)
                    
                    if actual_size == expected_size:
                        image_data = np.frombuffer(
                            responses[0].image_data_uint8, dtype=np.uint8
                        ).reshape(responses[0].height, responses[0].width, 3)
                        images["rgb"] = image_data
                    else:
                        # Handle compressed or different format images
                        self.logger.warning(f"Image size mismatch: expected {expected_size}, got {actual_size}")
                        # Create a placeholder image
                        images["rgb"] = np.zeros((responses[0].height, responses[0].width, 3), dtype=np.uint8)
                except Exception as img_error:
                    self.logger.warning(f"Image processing failed: {img_error}")
                    # Create a placeholder image
                    images["rgb"] = np.zeros((responses[0].height, responses[0].width, 3), dtype=np.uint8)

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
