"""
Mission logic for autonomous drone operations.
Handles waypoint navigation and mission execution.
"""

import time
from typing import List, Tuple, Dict, Any, Optional
from utils.logger import get_logger


class MissionLogic:
    """Handles mission planning and execution logic."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize mission logic.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = get_logger("mission")
        
        # Mission settings
        mission_config = config.get("mission", {})
        self.max_duration = mission_config.get("max_mission_duration", 1800)
        self.waypoint_tolerance = mission_config.get("waypoint_tolerance", 2.0)
        self.target_threshold = mission_config.get("target_detection_threshold", 0.7)
        
        # Mission state
        self.current_waypoint = 0
        self.mission_start_time = None
        self.mission_active = False
        
        # Default patrol pattern (square)
        self.patrol_waypoints = [
            (0, 0, -5),     # Start/Home
            (20, 0, -5),    # Forward
            (20, 20, -5),   # Right  
            (0, 20, -5),    # Back
            (0, 0, -5),     # Return home
        ]
        
    def start_mission(self) -> bool:
        """Start the mission.
        
        Returns:
            True if mission started successfully
        """
        self.logger.info("🚀 Starting patrol mission")
        self.mission_start_time = time.time()
        self.mission_active = True
        self.current_waypoint = 0
        return True
        
    def stop_mission(self) -> bool:
        """Stop the mission.
        
        Returns:
            True if mission stopped successfully
        """
        self.logger.info("🛑 Stopping mission")
        self.mission_active = False
        return True
        
    def get_next_waypoint(self) -> Optional[Tuple[float, float, float]]:
        """Get the next waypoint in the mission.
        
        Returns:
            Next waypoint coordinates (x, y, z) or None if mission complete
        """
        if not self.mission_active:
            return None
            
        if self.current_waypoint >= len(self.patrol_waypoints):
            self.logger.info("✅ All waypoints completed")
            return None
            
        waypoint = self.patrol_waypoints[self.current_waypoint]
        self.logger.info(f"🗺️  Next waypoint {self.current_waypoint + 1}/{len(self.patrol_waypoints)}: {waypoint}")
        return waypoint
        
    def waypoint_reached(self) -> bool:
        """Mark current waypoint as reached and advance to next.
        
        Returns:
            True if more waypoints remaining, False if mission complete
        """
        self.current_waypoint += 1
        self.logger.info(f"✅ Waypoint {self.current_waypoint} reached")
        
        if self.current_waypoint >= len(self.patrol_waypoints):
            self.logger.info("🎯 Mission completed - all waypoints visited")
            self.mission_active = False
            return False
            
        return True
        
    def check_mission_timeout(self) -> bool:
        """Check if mission has exceeded maximum duration.
        
        Returns:
            True if mission should timeout
        """
        if not self.mission_active or not self.mission_start_time:
            return False
            
        elapsed = time.time() - self.mission_start_time
        if elapsed > self.max_duration:
            self.logger.warning(f"⏰ Mission timeout after {elapsed:.1f}s")
            return True
            
        return False
        
    def process_vision_data(self, vision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process vision detection results.
        
        Args:
            vision_result: Vision processing results
            
        Returns:
            Mission command based on vision data
        """
        if not vision_result:
            return {"action": "continue"}
            
        # Check for target detection
        objects_detected = vision_result.get("objects_detected", 0)
        if objects_detected > 0:
            self.logger.info(f"👁️  Detected {objects_detected} objects")
            
            # For now, just log and continue
            # Future: implement target tracking, hovering, etc.
            return {
                "action": "log_detection",
                "objects": objects_detected,
                "message": f"Detected {objects_detected} objects"
            }
            
        return {"action": "continue"}
        
    def get_mission_status(self) -> Dict[str, Any]:
        """Get current mission status.
        
        Returns:
            Mission status dictionary
        """
        if not self.mission_start_time:
            elapsed = 0
        else:
            elapsed = time.time() - self.mission_start_time
            
        return {
            "active": self.mission_active,
            "current_waypoint": self.current_waypoint,
            "total_waypoints": len(self.patrol_waypoints),
            "elapsed_time": elapsed,
            "max_duration": self.max_duration,
            "progress": (self.current_waypoint / len(self.patrol_waypoints)) * 100
        }