"""
Vision processing module for object detection and targeting.
Simplified computer vision for basic object detection.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
from sim_drone.utils.logger import get_logger


class VisionProcessor:
    """Handles computer vision processing for object detection."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize vision processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = get_logger("vision")
        
        # Vision settings
        vision_config = config.get("vision", {})
        self.min_object_area = vision_config.get("min_object_area", 100)
        
        # Object detection parameters
        self.color_lower = np.array([0, 50, 50])    # Lower HSV threshold
        self.color_upper = np.array([179, 255, 255])  # Upper HSV threshold
        
        self.logger.info("🔧 Vision processor initialized")
        
    def process_frame(self, image: np.ndarray) -> Dict[str, Any]:
        """Process a single frame for object detection.
        
        Args:
            image: RGB image array
            
        Returns:
            Dictionary containing detection results
        """
        if image is None or image.size == 0:
            self.logger.warning("⚠️  Received empty image")
            return {"objects_detected": 0, "detections": []}
            
        try:
            # Convert RGB to HSV for color-based detection
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            # Create mask for color detection
            mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area
            valid_contours = [c for c in contours if cv2.contourArea(c) > self.min_object_area]
            
            # Extract detection information
            detections = []
            for contour in valid_contours:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                
                # Calculate center point
                center_x = x + w // 2
                center_y = y + h // 2
                
                detection = {
                    "bbox": (x, y, w, h),
                    "center": (center_x, center_y),
                    "area": area,
                    "confidence": min(1.0, area / 1000.0)  # Simple confidence based on size
                }
                detections.append(detection)
                
            result = {
                "objects_detected": len(detections),
                "detections": detections,
                "image_shape": image.shape,
                "processing_success": True
            }
            
            if len(detections) > 0:
                self.logger.info(f"👁️  Detected {len(detections)} objects")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Vision processing error: {e}")
            return {
                "objects_detected": 0,
                "detections": [],
                "processing_success": False,
                "error": str(e)
            }
            
    def detect_targets(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect specific targets in the image.
        
        Args:
            image: RGB image array
            
        Returns:
            List of target detection dictionaries
        """
        result = self.process_frame(image)
        
        # Filter detections for targets (simple area-based filtering)
        targets = []
        for detection in result.get("detections", []):
            if detection["area"] > self.min_object_area * 2:  # Larger objects are targets
                targets.append({
                    "type": "large_object",
                    "position": detection["center"],
                    "bbox": detection["bbox"],
                    "confidence": detection["confidence"]
                })
                
        return targets
        
    def get_image_center(self, image: np.ndarray) -> Tuple[int, int]:
        """Get the center coordinates of an image.
        
        Args:
            image: Input image
            
        Returns:
            Center coordinates (x, y)
        """
        if image is None or len(image.shape) < 2:
            return (0, 0)
            
        height, width = image.shape[:2]
        return (width // 2, height // 2)
        
    def calculate_offset(self, target_position: Tuple[int, int], image_center: Tuple[int, int]) -> Tuple[float, float]:
        """Calculate offset from image center to target.
        
        Args:
            target_position: Target (x, y) coordinates
            image_center: Image center (x, y) coordinates
            
        Returns:
            Normalized offset (-1 to 1) in (x, y)
        """
        dx = target_position[0] - image_center[0]
        dy = target_position[1] - image_center[1]
        
        # Normalize to image dimensions
        norm_dx = dx / image_center[0] if image_center[0] > 0 else 0
        norm_dy = dy / image_center[1] if image_center[1] > 0 else 0
        
        return (norm_dx, norm_dy)
        
    def set_detection_parameters(self, min_area: int = None, color_range: Tuple[np.ndarray, np.ndarray] = None):
        """Update detection parameters.
        
        Args:
            min_area: Minimum object area for detection
            color_range: Tuple of (lower_hsv, upper_hsv) color thresholds
        """
        if min_area is not None:
            self.min_object_area = min_area
            self.logger.info(f"🔧 Updated min object area to {min_area}")
            
        if color_range is not None:
            self.color_lower, self.color_upper = color_range
            self.logger.info(f"🔧 Updated color detection range")
            
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get vision processing statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "min_object_area": self.min_object_area,
            "color_lower": self.color_lower.tolist(),
            "color_upper": self.color_upper.tolist(),
            "processor_ready": True
        }