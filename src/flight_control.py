"""
Flight control module for drone operations using AirSim.
Handles drone connection, movement, and sensor data collection.
"""

from __future__ import annotations
import time
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from utils.logger import get_logger

try:
    import airsim
except ImportError:
    # Mock for development/testing without AirSim installed
    class MockAirSim:
        class MultirotorClient:
            def __init__(self, ip="127.0.0.1", port=41451):
                self.connected = False
                
            def confirmConnection(self):
                self.connected = True
                
            def enableApiControl(self, enable: bool, vehicle_name: str = ""):
                pass
                
            def armDisarm(self, arm: bool, vehicle_name: str = ""):
                pass
                
            def takeoffAsync(self, timeout_sec: float = 20, vehicle_name: str = ""):
                class MockTask:
                    def join(self): pass
                return MockTask()
                
            def moveToPositionAsync(self, x: float, y: float, z: float, velocity: float, vehicle_name: str = ""):
                class MockTask:
                    def join(self): pass
                return MockTask()
                
            def landAsync(self, timeout_sec: float = 60, vehicle_name: str = ""):
                class MockTask:
                    def join(self): pass
                return MockTask()
                
            def simGetImages(self, requests, vehicle_name: str = ""):
                # Return mock image data
                return [MockImageResponse()]
                
        class ImageRequest:
            def __init__(self, camera_name: str, image_type, pixels_as_float: bool, compress: bool):
                self.camera_name = camera_name
                self.image_type = image_type
                self.pixels_as_float = pixels_as_float
                self.compress = compress
                
        class ImageType:
            Scene = 0
            DepthPlanar = 1
            Segmentation = 2
            
    class MockImageResponse:
        def __init__(self):
            self.image_data_uint8 = np.random.randint(0, 255, (144, 256, 3), dtype=np.uint8).tobytes()
            self.height = 144
            self.width = 256
            
    airsim = MockAirSim()


class FlightController:
    """Controls drone flight operations and sensor data collection."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize flight controller.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = get_logger("flight_control")
        
        # AirSim connection settings
        airsim_config = config.get("airsim", {})
        self.host = airsim_config.get("host", "127.0.0.1")
        self.port = airsim_config.get("port", 41451)
        self.timeout = airsim_config.get("timeout", 10.0)
        self.vehicle_name = "Drone1"
        
        # Drone settings
        drone_config = config.get("drone", {})
        self.max_speed = drone_config.get("max_speed", 10.0)
        self.takeoff_height = drone_config.get("takeoff_height", 5.0)
        self.safety_distance = drone_config.get("safety_distance", 5.0)
        
        self.client: Optional[airsim.MultirotorClient] = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to AirSim.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to AirSim at {self.host}:{self.port}")
            self.client = airsim.MultirotorClient(ip=self.host, port=self.port)
            self.client.confirmConnection()
            self.client.enableApiControl(True, vehicle_name=self.vehicle_name)
            self.connected = True
            self.logger.info("Successfully connected to AirSim")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to AirSim: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from AirSim."""
        if self.client and self.connected:
            try:
                self.client.enableApiControl(False, vehicle_name=self.vehicle_name)
                self.connected = False
                self.logger.info("Disconnected from AirSim")
            except Exception as e:
                self.logger.error(f"Error during disconnect: {e}")
    
    def arm(self) -> bool:
        """Arm the drone.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to AirSim")
            return False
            
        try:
            self.client.armDisarm(True, vehicle_name=self.vehicle_name)
            self.logger.info("Drone armed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to arm drone: {e}")
            return False
    
    def disarm(self) -> bool:
        """Disarm the drone.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to AirSim")
            return False
            
        try:
            self.client.armDisarm(False, vehicle_name=self.vehicle_name)
            self.logger.info("Drone disarmed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disarm drone: {e}")
            return False
    
    def takeoff(self, timeout_sec: float = 15.0) -> bool:
        """Take off the drone.
        
        Args:
            timeout_sec: Timeout for takeoff operation
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to AirSim")
            return False
            
        try:
            self.logger.info("Taking off...")
            self.client.takeoffAsync(timeout_sec=timeout_sec, vehicle_name=self.vehicle_name).join()
            # Small settle time
            time.sleep(1.0)
            self.logger.info("Takeoff completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Takeoff failed: {e}")
            return False
    
    def land(self, timeout_sec: float = 60.0) -> bool:
        """Land the drone.
        
        Args:
            timeout_sec: Timeout for landing operation
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to AirSim")
            return False
            
        try:
            self.logger.info("Landing...")
            self.client.landAsync(timeout_sec=timeout_sec, vehicle_name=self.vehicle_name).join()
            time.sleep(1.0)
            self.logger.info("Landing completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Landing failed: {e}")
            return False
    
    def move_to_position(self, x: float, y: float, z: float, velocity: float = None) -> bool:
        """Move drone to specific position.
        
        Args:
            x: X coordinate (NED frame)
            y: Y coordinate (NED frame) 
            z: Z coordinate (NED frame, negative is up)
            velocity: Movement velocity (m/s)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to AirSim")
            return False
            
        if velocity is None:
            velocity = self.max_speed
            
        try:
            self.logger.info(f"Moving to position ({x:.1f}, {y:.1f}, {z:.1f}) at {velocity:.1f} m/s")
            self.client.moveToPositionAsync(
                x, y, z, velocity, vehicle_name=self.vehicle_name
            ).join()
            return True
        except Exception as e:
            self.logger.error(f"Move to position failed: {e}")
            return False
    
    def fly_square(self, side_m: float = 5.0, alt_m: float = -5.0, speed: float = 2.0) -> bool:
        """Fly a square pattern.
        
        Args:
            side_m: Side length of square in meters
            alt_m: Altitude (negative Z in NED)
            speed: Flight speed
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            self.logger.error("Not connected to AirSim")
            return False
            
        try:
            self.logger.info(f"Flying square pattern: {side_m}m sides at {alt_m}m altitude")
            
            # Square waypoints in NED coordinates
            waypoints = [
                (0, 0, alt_m),           # Start
                (side_m, 0, alt_m),      # Forward
                (side_m, side_m, alt_m), # Right
                (0, side_m, alt_m),      # Back
                (0, 0, alt_m),           # Return to start
            ]
            
            for i, (x, y, z) in enumerate(waypoints):
                self.logger.info(f"Moving to waypoint {i+1}/5: ({x}, {y}, {z})")
                success = self.move_to_position(x, y, z, speed)
                if not success:
                    self.logger.error(f"Failed to reach waypoint {i+1}")
                    return False
                    
            self.logger.info("Square pattern completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Square flight pattern failed: {e}")
            return False
    
    def get_sensor_data(self) -> Dict[str, Any]:
        """Get sensor data from drone.
        
        Returns:
            Dictionary containing sensor data
        """
        if not self.connected or not self.client:
            self.logger.warning("Not connected to AirSim, returning empty sensor data")
            return {}
            
        try:
            # Request RGB camera image (uncompressed)
            responses = self.client.simGetImages([
                airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
            ], vehicle_name=self.vehicle_name)
            
            sensor_data = {}
            
            if responses and len(responses) > 0:
                response = responses[0]
                try:
                    # Convert image data to numpy array
                    img_1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
                    img_rgb = img_1d.reshape(response.height, response.width, 3)
                    sensor_data["rgb_image"] = img_rgb
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process image data: {e}")
                    # Provide placeholder image
                    sensor_data["rgb_image"] = np.zeros((144, 256, 3), dtype=np.uint8)
            else:
                self.logger.warning("No image response received")
                sensor_data["rgb_image"] = np.zeros((144, 256, 3), dtype=np.uint8)
                
            return sensor_data
            
        except Exception as e:
            self.logger.error(f"Failed to get sensor data: {e}")
            return {"rgb_image": np.zeros((144, 256, 3), dtype=np.uint8)}


class DroneController:
    """Legacy wrapper for compatibility."""
    
    def __init__(self, config: Dict[str, Any]):
        self.flight_controller = FlightController(config)
        
    def connect(self) -> bool:
        return self.flight_controller.connect()
        
    def disconnect(self):
        self.flight_controller.disconnect()
        
    def get_sensor_data(self) -> Dict[str, Any]:
        return self.flight_controller.get_sensor_data()