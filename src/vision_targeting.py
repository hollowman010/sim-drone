"""
Vision Processor module for computer vision tasks.
Handles image processing, object detection, and visual analysis.
"""

import cv2
import numpy as np
import logging
from typing import Dict, Any, List
from pathlib import Path


class VisionProcessor:
    """Processes visual data from drone cameras."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the vision processor.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.detection_model = None
        self.segmentation_model = None

        # Initialize models if specified in config
        self._load_models()

    def _load_models(self):
        """Load computer vision models."""
        try:
            # Load object detection model (example with OpenCV DNN)
            if "detection_model_path" in self.config:
                model_path = self.config["detection_model_path"]
                if Path(model_path).exists():
                    self.detection_model = cv2.dnn.readNetFromTensorflow(model_path)
                    self.logger.info("Detection model loaded successfully")

            # Load segmentation model
            if "segmentation_model_path" in self.config:
                model_path = self.config["segmentation_model_path"]
                if Path(model_path).exists():
                    self.segmentation_model = cv2.dnn.readNetFromTensorflow(model_path)
                    self.logger.info("Segmentation model loaded successfully")

        except Exception as e:
            self.logger.warning(f"Failed to load models: {e}")

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
                "obstacles": [],
                "landing_zones": [],
                "path_clearance": True,
                "image_processed": False,
            }

            # Process RGB image
            if "image_0" in sensor_data["images"]:
                rgb_image = sensor_data["images"]["image_0"]
                results.update(self._process_rgb_image(rgb_image))

            # Process depth image
            if "image_1" in sensor_data["images"]:
                depth_image = sensor_data["images"]["image_1"]
                results.update(self._process_depth_image(depth_image))

            # Process segmentation image
            if "image_2" in sensor_data["images"]:
                seg_image = sensor_data["images"]["image_2"]
                results.update(self._process_segmentation_image(seg_image))

            return results

        except Exception as e:
            self.logger.error(f"Error processing vision data: {e}")
            return {"error": str(e)}

    def _process_rgb_image(self, image: np.ndarray) -> Dict[str, Any]:
        """Process RGB image for object detection.

        Args:
            image: RGB image array

        Returns:
            Dictionary containing detection results
        """
        results = {"objects_detected": [], "image_processed": True}

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
            min_area = self.config.get("min_object_area", 100)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
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

    def _process_depth_image(self, depth_image: np.ndarray) -> Dict[str, Any]:
        """Process depth image for obstacle detection.

        Args:
            depth_image: Depth image array

        Returns:
            Dictionary containing obstacle detection results
        """
        results = {"obstacles": [], "path_clearance": True}

        try:
            # Normalize depth image
            if depth_image.dtype != np.float32:
                depth_image = depth_image.astype(np.float32) / 255.0

            # Threshold for obstacle detection
            obstacle_threshold = self.config.get("obstacle_threshold", 0.3)

            # Find obstacles (close objects)
            obstacles = depth_image < obstacle_threshold

            if np.any(obstacles):
                results["path_clearance"] = False

                # Find obstacle regions
                obstacle_regions = self._find_obstacle_regions(obstacles)
                results["obstacles"] = obstacle_regions

        except Exception as e:
            self.logger.error(f"Error processing depth image: {e}")

        return results

    def _process_segmentation_image(self, seg_image: np.ndarray) -> Dict[str, Any]:
        """Process segmentation image for scene understanding.

        Args:
            seg_image: Segmentation image array

        Returns:
            Dictionary containing segmentation results
        """
        results = {"landing_zones": [], "scene_analysis": {}}

        try:
            # Analyze segmentation for different object types
            unique_labels = np.unique(seg_image)

            for label in unique_labels:
                if label > 0:  # Skip background
                    mask = seg_image == label
                    area = np.sum(mask)

                    # Check if this could be a landing zone (flat surface)
                    if area > self.config.get("min_landing_area", 1000):
                        # Calculate properties of the region
                        properties = self._analyze_region(mask)

                        if (
                            properties["flatness"] > 0.8
                        ):  # High flatness indicates good landing zone
                            results["landing_zones"].append(
                                {
                                    "label": int(label),
                                    "area": area,
                                    "properties": properties,
                                }
                            )

        except Exception as e:
            self.logger.error(f"Error processing segmentation image: {e}")

        return results

    def _find_obstacle_regions(self, obstacle_mask: np.ndarray) -> List[Dict[str, Any]]:
        """Find regions of obstacles in the depth image.

        Args:
            obstacle_mask: Boolean mask of obstacles

        Returns:
            List of obstacle regions with properties
        """
        regions = []

        try:
            # Find connected components
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
                obstacle_mask.astype(np.uint8), connectivity=8
            )

            # Process each component
            for i in range(1, num_labels):  # Skip background
                x, y, w, h, area = stats[i]
                centroid = centroids[i]

                regions.append(
                    {
                        "bbox": [x, y, w, h],
                        "area": area,
                        "centroid": centroid.tolist(),
                        "distance": "close",  # Could be refined with actual depth
                        # values
                    }
                )

        except Exception as e:
            self.logger.error(f"Error finding obstacle regions: {e}")

        return regions

    def _analyze_region(self, mask: np.ndarray) -> Dict[str, float]:
        """Analyze properties of a segmented region.

        Args:
            mask: Boolean mask of the region

        Returns:
            Dictionary containing region properties
        """
        properties = {"flatness": 0.0, "compactness": 0.0, "area": np.sum(mask)}

        try:
            # Calculate compactness (area / perimeter^2)
            contours, _ = cv2.findContours(
                mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if contours:
                contour = contours[0]
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    properties["compactness"] = properties["area"] / (perimeter**2)

                # Estimate flatness based on contour shape
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0:
                    properties["flatness"] = properties["area"] / hull_area

        except Exception as e:
            self.logger.error(f"Error analyzing region: {e}")

        return properties
