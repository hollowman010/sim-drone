"""
Vision Processor module for computer vision tasks.
Streamlined and efficient vision processing implementation.
"""

import cv2
import numpy as np
import logging
from typing import Dict, Any, List


class VisionProcessor:
    """Processes visual data from drone cameras."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the vision processor.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.min_object_area = config.get("min_object_area", 100)

    def process(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process sensor data and extract visual information.

        Args:
            sensor_data: Dictionary containing sensor data including images

        Returns:
            Dictionary containing processed vision results
        """
        try:
            results = {
                "objects_detected": [],
                "image_processed": False,
            }

            # Process RGB image
            if "rgb" in sensor_data.get("images", {}):
                rgb_image = sensor_data["images"]["rgb"]
                results.update(self._process_rgb_image(rgb_image))

            return results

        except Exception as e:
            self.logger.error(f"Error processing vision data: {e}")
            return {"objects_detected": [], "image_processed": False}

    def _process_rgb_image(self, image: np.ndarray) -> Dict[str, Any]:
        """Process RGB image for object detection.

        Args:
            image: RGB image array

        Returns:
            Dictionary containing detection results
        """
        results: Dict[str, Any] = {"objects_detected": [], "image_processed": True}

        try:
            # Convert to BGR for OpenCV
            if len(image.shape) == 3 and image.shape[2] == 3:
                bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                bgr_image = image

            # Basic object detection using contours
            gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)

            # Find contours
            contours, _ = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Filter contours by area
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.min_object_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    results["objects_detected"].append(
                        {
                            "type": "unknown",
                            "bbox": [x, y, w, h],
                            "area": area,
                            "confidence": 0.5,
                        }
                    )

        except Exception as e:
            self.logger.error(f"Error processing RGB image: {e}")

        return results
