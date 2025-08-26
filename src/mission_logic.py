"""
Mission Logic module for high-level mission strategy and decisions.
Streamlined and efficient mission control implementation.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import time


@dataclass
class Waypoint:
    """Represents a navigation waypoint."""
    x: float
    y: float
    z: float
    speed: float = 5.0


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
        self.mission_start_time: Optional[float] = None
        self.target_detected = False
        self.mission_completed = False

        # Patrol configuration
        self.patrol_waypoints: List[Tuple[float, float, float]] = []
        self.current_waypoint_index = 0
        self.waypoint_tolerance = config.get("waypoint_tolerance", 2.0)

        # Mission parameters
        self.max_mission_duration = config.get("max_mission_duration", 1800)  # 30 minutes
        self.target_detection_threshold = config.get("target_detection_threshold", 0.7)

    def start_mission(self, patrol_waypoints: List[tuple]):
        """Start the mission with patrol waypoints.

        Args:
            patrol_waypoints: List of (x, y, z) waypoints for patrol
        """
        self.patrol_waypoints = patrol_waypoints
        self.current_waypoint_index = 0
        self.mission_completed = False
        self.mission_start_time = time.time()
        self.logger.info(f"Mission started with {len(patrol_waypoints)} patrol waypoints")

    def update(
        self, vision_results: Dict[str, Any], drone_position: tuple
    ) -> Dict[str, Any]:
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
                return {"action": "land", "reason": "mission_timeout"}

            # Update target detection
            self._update_target_detection(vision_results)

            # If target detected, hover and track
            if self.target_detected:
                return {"action": "hover", "reason": "target_detected"}

            # Continue patrol
            if self.current_waypoint_index < len(self.patrol_waypoints):
                waypoint = self.patrol_waypoints[self.current_waypoint_index]
                
                # Check if we've reached the current waypoint
                if self._is_at_waypoint(drone_position, waypoint):
                    self.current_waypoint_index += 1
                    self.logger.info(f"Reached waypoint {self.current_waypoint_index}")
                
                # Move to next waypoint
                if self.current_waypoint_index < len(self.patrol_waypoints):
                    next_waypoint = self.patrol_waypoints[self.current_waypoint_index]
                    return {
                        "action": "move_to_position",
                        "position": next_waypoint,
                        "speed": 5.0,
                        "reason": f"patrol_waypoint_{self.current_waypoint_index + 1}",
                    }
                else:
                    # Patrol completed
                    self.mission_completed = True
                    return {"action": "land", "reason": "patrol_completed"}

            return {"action": "hover", "reason": "waiting"}

        except Exception as e:
            self.logger.error(f"Error in mission logic update: {e}")
            return {"action": "land", "reason": "error"}

    def _update_target_detection(self, vision_results: Dict[str, Any]):
        """Update target detection status."""
        objects_detected = vision_results.get("objects_detected", [])

        # Check for targets with high confidence
        for obj in objects_detected:
            if obj.get("confidence", 0) > self.target_detection_threshold:
                if not self.target_detected:
                    self.target_detected = True
                    self.logger.info(f"Target detected with confidence {obj.get('confidence', 0)}")
                break
        else:
            # No high-confidence targets found
            if self.target_detected:
                self.target_detected = False

    def _is_at_waypoint(self, drone_position: tuple, waypoint: tuple) -> bool:
        """Check if drone is at the specified waypoint.

        Args:
            drone_position: Current drone position (x, y, z)
            waypoint: Target waypoint (x, y, z)

        Returns:
            True if drone is at waypoint within tolerance
        """
        if len(drone_position) != 3 or len(waypoint) != 3:
            return False

        distance = ((drone_position[0] - waypoint[0]) ** 2 + 
                   (drone_position[1] - waypoint[1]) ** 2 + 
                   (drone_position[2] - waypoint[2]) ** 2) ** 0.5
        
        return distance <= self.waypoint_tolerance

    def _is_mission_timeout(self) -> bool:
        """Check if mission has timed out."""
        if self.mission_start_time is None:
            return False
        return (time.time() - self.mission_start_time) > self.max_mission_duration

    def get_mission_status(self) -> Dict[str, Any]:
        """Get current mission status.

        Returns:
            Dictionary containing mission status information
        """
        return {
            "state": "completed" if self.mission_completed else "active",
            "target_detected": self.target_detected,
            "current_waypoint_index": self.current_waypoint_index,
            "total_waypoints": len(self.patrol_waypoints),
            "mission_duration": (
                time.time() - self.mission_start_time if self.mission_start_time else 0
            ),
        }
