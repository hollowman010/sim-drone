"""
Mission Logic module for high-level mission strategy and decisions.
Handles patrol logic, target detection behavior, and mission state management.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import numpy as np


class MissionState(Enum):
    """Mission states for the drone."""
    IDLE = "idle"
    TAKEOFF = "takeoff"
    PATROL = "patrol"
    TARGET_DETECTED = "target_detected"
    TRACKING = "tracking"
    RETURN_HOME = "return_home"
    LANDING = "landing"
    COMPLETED = "completed"
    EMERGENCY = "emergency"


@dataclass
class Waypoint:
    """Represents a navigation waypoint."""
    x: float
    y: float
    z: float
    speed: float = 5.0
    tolerance: float = 2.0


@dataclass
class TargetInfo:
    """Information about a detected target."""
    position: tuple  # (x, y, z) in world coordinates
    confidence: float
    timestamp: float
    bbox: Optional[tuple] = None  # (x, y, width, height) in image coordinates


class MissionLogic:
    """High-level mission logic and decision making."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the mission logic.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Mission state
        self.current_state = MissionState.IDLE
        self.mission_start_time = None
        self.target_detected = False
        self.target_info: Optional[TargetInfo] = None
        
        # Patrol configuration
        self.patrol_waypoints = []
        self.current_patrol_index = 0
        self.patrol_completed = False
        
        # Target tracking
        self.tracking_start_time = None
        self.max_tracking_duration = config.get("max_tracking_duration", 300)  # 5 minutes
        
        # Mission parameters
        self.max_mission_duration = config.get("max_mission_duration", 1800)  # 30 minutes
        self.target_detection_threshold = config.get("target_detection_threshold", 0.7)
        self.patrol_altitude = config.get("patrol_altitude", 20.0)
        
        # Navigation parameters
        self.safety_distance = config.get("safety_distance", 5.0)
        self.max_speed = config.get("max_speed", 10.0)
        self.obstacle_avoidance_enabled = config.get("obstacle_avoidance", True)
        
    def start_mission(self, patrol_waypoints: List[tuple]):
        """Start the mission with patrol waypoints.
        
        Args:
            patrol_waypoints: List of (x, y, z) waypoints for patrol
        """
        self.patrol_waypoints = patrol_waypoints
        self.current_patrol_index = 0
        self.patrol_completed = False
        self.mission_start_time = time.time()
        self.current_state = MissionState.TAKEOFF
        self.logger.info(f"Mission started with {len(patrol_waypoints)} patrol waypoints")
        
    def update(self, vision_results: Dict[str, Any], drone_position: tuple) -> Dict[str, Any]:
        """Update mission logic and return next action.
        
        Args:
            vision_results: Results from vision processing
            drone_position: Current drone position (x, y, z)
            
        Returns:
            Dictionary containing mission commands
        """
        try:
            # Check mission timeout
            if self._is_mission_timeout():
                return self._handle_mission_timeout()
                
            # Update target detection
            self._update_target_detection(vision_results)
            
            # State machine logic
            if self.current_state == MissionState.IDLE:
                return self._handle_idle_state()
            elif self.current_state == MissionState.TAKEOFF:
                return self._handle_takeoff_state()
            elif self.current_state == MissionState.PATROL:
                return self._handle_patrol_state(vision_results, drone_position)
            elif self.current_state == MissionState.TARGET_DETECTED:
                return self._handle_target_detected_state()
            elif self.current_state == MissionState.TRACKING:
                return self._handle_tracking_state(vision_results, drone_position)
            elif self.current_state == MissionState.RETURN_HOME:
                return self._handle_return_home_state()
            elif self.current_state == MissionState.LANDING:
                return self._handle_landing_state()
            else:
                return {"action": "hover", "reason": "unknown_state"}
                
        except Exception as e:
            self.logger.error(f"Error in mission logic update: {e}")
            return self._handle_emergency()
            
    def _update_target_detection(self, vision_results: Dict[str, Any]):
        """Update target detection status."""
        objects_detected = vision_results.get("objects_detected", [])
        
        # Check for targets with high confidence
        for obj in objects_detected:
            if obj.get("confidence", 0) > self.target_detection_threshold:
                if not self.target_detected:
                    self.target_detected = True
                    self.target_info = TargetInfo(
                        position=(0, 0, 0),  # Would need to convert from image to world coordinates
                        confidence=obj.get("confidence", 0),
                        timestamp=time.time(),
                        bbox=obj.get("bbox")
                    )
                    self.logger.info(f"Target detected with confidence {obj.get('confidence', 0)}")
                break
        else:
            # No high-confidence targets found
            if self.target_detected and self.current_state == MissionState.PATROL:
                self.target_detected = False
                self.target_info = None
                
    def _handle_idle_state(self) -> Dict[str, Any]:
        """Handle idle state."""
        return {"action": "wait", "reason": "idle_state"}
        
    def _handle_takeoff_state(self) -> Dict[str, Any]:
        """Handle takeoff state."""
        self.current_state = MissionState.PATROL
        return {
            "action": "takeoff",
            "altitude": self.patrol_altitude,
            "reason": "starting_patrol"
        }
        
    def _handle_patrol_state(self, vision_results: Dict[str, Any], drone_position: tuple) -> Dict[str, Any]:
        """Handle patrol state."""
        # Check if target was detected
        if self.target_detected:
            self.current_state = MissionState.TARGET_DETECTED
            return {"action": "hover", "reason": "target_detected"}
            
        # Continue patrol
        if self.current_patrol_index < len(self.patrol_waypoints):
            waypoint = self.patrol_waypoints[self.current_patrol_index]
            return {
                "action": "move_to_position",
                "position": waypoint,
                "speed": 5.0,
                "reason": f"patrol_waypoint_{self.current_patrol_index + 1}"
            }
        else:
            # Patrol completed
            self.patrol_completed = True
            self.current_state = MissionState.RETURN_HOME
            return {"action": "return_home", "reason": "patrol_completed"}
            
    def _handle_target_detected_state(self) -> Dict[str, Any]:
        """Handle target detected state."""
        self.current_state = MissionState.TRACKING
        self.tracking_start_time = time.time()
        return {
            "action": "start_tracking",
            "target_info": self.target_info,
            "reason": "beginning_target_tracking"
        }
        
    def _handle_tracking_state(self, vision_results: Dict[str, Any], drone_position: tuple) -> Dict[str, Any]:
        """Handle tracking state."""
        # Check tracking timeout
        if self._is_tracking_timeout():
            self.current_state = MissionState.RETURN_HOME
            return {"action": "return_home", "reason": "tracking_timeout"}
            
        # Continue tracking if target is still visible
        if self.target_detected and self.target_info:
            return {
                "action": "track_target",
                "target_info": self.target_info,
                "reason": "maintaining_target_track"
            }
        else:
            # Target lost, return to patrol
            self.current_state = MissionState.PATROL
            return {"action": "resume_patrol", "reason": "target_lost"}
            
    def _handle_return_home_state(self) -> Dict[str, Any]:
        """Handle return home state."""
        self.current_state = MissionState.LANDING
        return {
            "action": "land",
            "reason": "mission_completed"
        }
        
    def _handle_landing_state(self) -> Dict[str, Any]:
        """Handle landing state."""
        self.current_state = MissionState.COMPLETED
        return {"action": "complete_mission", "reason": "landing_completed"}
        
    def _handle_emergency(self) -> Dict[str, Any]:
        """Handle emergency state."""
        self.current_state = MissionState.EMERGENCY
        return {"action": "emergency_land", "reason": "emergency_condition"}
        
    def _is_mission_timeout(self) -> bool:
        """Check if mission has timed out."""
        if self.mission_start_time is None:
            return False
        return (time.time() - self.mission_start_time) > self.max_mission_duration
        
    def _is_tracking_timeout(self) -> bool:
        """Check if tracking has timed out."""
        if self.tracking_start_time is None:
            return False
        return (time.time() - self.tracking_start_time) > self.max_tracking_duration
        
    def _handle_mission_timeout(self) -> Dict[str, Any]:
        """Handle mission timeout."""
        self.logger.warning("Mission timeout reached")
        self.current_state = MissionState.RETURN_HOME
        return {"action": "return_home", "reason": "mission_timeout"}
        
    def get_mission_status(self) -> Dict[str, Any]:
        """Get current mission status.
        
        Returns:
            Dictionary containing mission status information
        """
        return {
            "state": self.current_state.value,
            "target_detected": self.target_detected,
            "patrol_completed": self.patrol_completed,
            "current_patrol_index": self.current_patrol_index,
            "total_patrol_waypoints": len(self.patrol_waypoints),
            "mission_duration": time.time() - self.mission_start_time if self.mission_start_time else 0,
            "target_info": self.target_info
        }
        
    def add_patrol_waypoint(self, x: float, y: float, z: float):
        """Add a waypoint to the patrol route.
        
        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate
        """
        self.patrol_waypoints.append((x, y, z))
        self.logger.info(f"Added patrol waypoint at ({x}, {y}, {z})")
        
    def clear_patrol_waypoints(self):
        """Clear all patrol waypoints."""
        self.patrol_waypoints.clear()
        self.current_patrol_index = 0
        self.patrol_completed = False
        self.logger.info("Cleared all patrol waypoints")
        
    def _handle_obstacle_avoidance(self, vision_results: Dict[str, Any]) -> Dict[str, Any]:
        """Handle obstacle avoidance when obstacles are detected.
        
        Args:
            vision_results: Results from vision processing
            
        Returns:
            Dictionary containing avoidance commands
        """
        obstacles = vision_results.get("obstacles", [])
        
        if not obstacles:
            return {"action": "hover", "parameters": {}}
            
        # Find the best avoidance direction
        avoidance_direction = self._calculate_avoidance_direction(obstacles)
        
        if avoidance_direction:
            return {
                "action": "move_by_velocity",
                "parameters": {
                    "vx": avoidance_direction[0] * self.max_speed * 0.5,
                    "vy": avoidance_direction[1] * self.max_speed * 0.5,
                    "vz": avoidance_direction[2] * self.max_speed * 0.3,
                    "duration": 2.0
                }
            }
        else:
            # If no clear avoidance direction, hover and wait
            return {"action": "hover", "parameters": {}}
            
    def _calculate_avoidance_direction(self, obstacles: List[Dict[str, Any]]) -> Optional[Tuple[float, float, float]]:
        """Calculate the best direction to avoid obstacles.
        
        Args:
            obstacles: List of detected obstacles
            
        Returns:
            Tuple of (x, y, z) direction vector, or None if no clear direction
        """
        if not obstacles:
            return None
            
        # Simple avoidance: move away from the closest obstacle
        closest_obstacle = min(obstacles, key=lambda obs: obs.get("area", float('inf')))
        
        # Get obstacle position (assuming it's in the center of the image)
        image_center_x = 320  # Assuming 640x480 image
        image_center_y = 240
        
        if "centroid" in closest_obstacle:
            obs_x, obs_y = closest_obstacle["centroid"]
            
            # Calculate direction away from obstacle
            dx = image_center_x - obs_x
            dy = image_center_y - obs_y
            
            # Normalize direction
            magnitude = np.sqrt(dx**2 + dy**2)
            if magnitude > 0:
                dx /= magnitude
                dy /= magnitude
                
            # Add some upward movement for safety
            dz = 0.3
                
            return (dx, dy, dz)
            
        return None
