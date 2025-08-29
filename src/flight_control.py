"""
Flight control module for drone operations using AirSim.
Clean, minimal implementation focused on essential flight operations.
"""

from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Dict, Any
import airsim


@dataclass
class FlightConfig:
    host: str = "127.0.0.1"
    port: int = 41451
    vehicle: str = "Drone1"
    takeoff_alt_m: float = 5.0
    speed_mps: float = 3.0


class FlightController:
    """Clean, minimal flight controller for AirSim drone operations."""
    
    def __init__(self, config: Dict[str, Any] | FlightConfig):
        """Initialize flight controller with config dict or FlightConfig."""
        if isinstance(config, dict):
            # Convert dict config to FlightConfig for compatibility
            airsim_cfg = config.get("airsim", {})
            drone_cfg = config.get("drone", {})
            self.cfg = FlightConfig(
                host=airsim_cfg.get("host", "127.0.0.1"),
                port=airsim_cfg.get("port", 41451),
                vehicle=airsim_cfg.get("vehicle_name", "Drone1"),
                takeoff_alt_m=drone_cfg.get("takeoff_height", 5.0),
                speed_mps=drone_cfg.get("cruise_speed", 3.0)
            )
        else:
            self.cfg = config
            
        self.client = None
        self.connected = False

    def connect(self) -> bool:
        """Connect to AirSim and enable API control."""
        try:
            print(f"🔗 Connecting to AirSim at {self.cfg.host}:{self.cfg.port}")
            self.client = airsim.MultirotorClient(ip=self.cfg.host, port=self.cfg.port)
            self.client.confirmConnection()
            self.client.enableApiControl(True, vehicle_name=self.cfg.vehicle)
            self.client.armDisarm(True, vehicle_name=self.cfg.vehicle)
            self.connected = True
            print(f"✅ Connected and armed {self.cfg.vehicle}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def takeoff(self) -> bool:
        """Take off and move to configured altitude."""
        if not self.connected:
            print("❌ Not connected to AirSim")
            return False
            
        try:
            print(f"🚀 Taking off to {self.cfg.takeoff_alt_m}m...")
            self.client.takeoffAsync(vehicle_name=self.cfg.vehicle).join()
            self.client.moveToZAsync(-self.cfg.takeoff_alt_m, 2.0, vehicle_name=self.cfg.vehicle).join()
            print(f"✅ Takeoff to {self.cfg.takeoff_alt_m}m complete")
            return True
        except Exception as e:
            print(f"❌ Takeoff failed: {e}")
            return False

    def goto(self, x: float, y: float, z: float | None = None, vel: float | None = None) -> bool:
        """Move to specified position."""
        if not self.connected:
            print("❌ Not connected to AirSim")
            return False
            
        if z is None:
            z = -self.cfg.takeoff_alt_m  # maintain current altitude
        if vel is None:
            vel = self.cfg.speed_mps
            
        try:
            print(f"📍 Moving to ({x:.1f}, {y:.1f}, {z:.1f}) at {vel:.1f} m/s")
            self.client.moveToPositionAsync(x, y, z, vel, vehicle_name=self.cfg.vehicle).join()
            print(f"✅ Reached position ({x:.1f}, {y:.1f}, {z:.1f})")
            return True
        except Exception as e:
            print(f"❌ Move failed: {e}")
            return False

    def hover(self, secs: float = 1.0) -> bool:
        """Hover in place for specified duration."""
        if not self.connected:
            print("❌ Not connected to AirSim")
            return False
            
        try:
            print(f"🚁 Hovering for {secs:.1f} seconds...")
            self.client.hoverAsync(vehicle_name=self.cfg.vehicle).join()
            time.sleep(secs)
            return True
        except Exception as e:
            print(f"❌ Hover failed: {e}")
            return False

    def fly_square(self, side_m: float = 5.0) -> bool:
        """Fly a square pattern."""
        if not self.connected:
            print("❌ Not connected to AirSim")
            return False
            
        print(f"🔲 Flying {side_m}m square pattern...")
        
        # Square waypoints relative to current position
        waypoints = [
            (0, 0),           # Start
            (side_m, 0),      # Forward
            (side_m, side_m), # Right
            (0, side_m),      # Back
            (0, 0),           # Return to start
        ]
        
        for i, (x, y) in enumerate(waypoints):
            if not self.goto(x, y):
                print(f"❌ Square pattern failed at waypoint {i+1}")
                return False
                
        print("✅ Square pattern completed")
        return True

    def land_and_shutdown(self) -> bool:
        """Land the drone and disable API control."""
        if not self.connected:
            print("❌ Not connected to AirSim")
            return False
            
        try:
            print("🛬 Landing...")
            self.client.landAsync(vehicle_name=self.cfg.vehicle).join()
            self.client.armDisarm(False, vehicle_name=self.cfg.vehicle)
            self.client.enableApiControl(False, vehicle_name=self.cfg.vehicle)
            self.connected = False
            print("✅ Landed and shutdown complete")
            return True
        except Exception as e:
            print(f"❌ Landing failed: {e}")
            return False

    def disconnect(self):
        """Clean disconnect."""
        if self.connected:
            self.land_and_shutdown()


# Legacy compatibility wrapper
class DroneController:
    """Legacy wrapper for backward compatibility."""
    
    def __init__(self, config: Dict[str, Any]):
        self.flight_controller = FlightController(config)
        
    def connect(self) -> bool:
        return self.flight_controller.connect()
        
    def disconnect(self):
        self.flight_controller.disconnect()
        
    def get_sensor_data(self) -> Dict[str, Any]:
        # Simplified sensor data for compatibility
        return {"rgb_image": None, "processing_success": True}