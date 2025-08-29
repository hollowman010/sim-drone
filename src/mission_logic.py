"""
Mission logic for autonomous drone operations with vision integration.
Handles waypoint navigation, vision processing, and frame capture.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Tuple, Optional
import os
import time
import pathlib

from flight_control import FlightController, FlightConfig

# Lazy import inside methods to avoid hard fail if cv2/airsim not installed
# until we actually run with vision/camera.
def _ensure_dir(p: str) -> None:
    path = pathlib.Path(p).expanduser()
    path.mkdir(parents=True, exist_ok=True)


@dataclass
class MissionConfig:
    waypoints_m: Sequence[Tuple[float, float, float]] = (
        (10, 0, 0), (0, 10, 0), (-10, 0, 0), (0, -10, 0)
    )
    speed_mps: float = 2.0
    hover_s: float = 0.4
    camera_name: str = "0"  # default AirSim camera
    save_frames_dir: Optional[str] = None  # e.g. "~/runs/$(date +...)"
    vision_enabled: bool = bool(int(os.getenv("VISION", "0")))  # set VISION=1 to enable
    compress_camera: bool = True  # request PNG bytes


class MissionPlanner:
    def __init__(self, fc: FlightController, mcfg: Optional[MissionConfig] = None):
        self.fc = fc
        self.cfg = mcfg or MissionConfig()

    def _get_bgr_frame(self):
        import numpy as np
        import cv2
        import airsim  # type: ignore

        assert self.fc.client, "Not connected"
        req = airsim.ImageRequest(
            self.cfg.camera_name,
            airsim.ImageType.Scene,
            pixels_as_float=False,
            compress=self.cfg.compress_camera,
        )
        resp = self.fc.client.simGetImages([req])[0]
        if self.cfg.compress_camera:
            arr = np.frombuffer(resp.image_data_uint8, dtype=np.uint8)
            if arr.size == 0:
                return None
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            return img
        else:
            # uncompressed path
            w = resp.width
            h = resp.height
            if w == 0 or h == 0 or not resp.image_data_uint8:
                return None
            arr = np.frombuffer(resp.image_data_uint8, dtype=np.uint8)
            img = arr.reshape(h, w, 3)
            return img

    def _vision_step(self, step_idx: int):
        if not self.cfg.vision_enabled:
            return
        import cv2
        from vision_targeting import VisionProcessor

        frame = self._get_bgr_frame()
        if frame is None:
            print("⚠️ Vision: no frame")
            return
            
        # Convert BGR to RGB for your VisionProcessor
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Use your existing VisionProcessor
        if not hasattr(self, '_vision_processor'):
            self._vision_processor = VisionProcessor({"vision": {}})
            
        result = self._vision_processor.process_frame(frame_rgb)
        
        if result["objects_detected"] > 0:
            # Get the best detection
            detections = result["detections"]
            best = max(detections, key=lambda d: d["area"])
            x, y, w, h = best["bbox"]
            print(f"🎯 Vision: best bbox=({x},{y},{w},{h}) area={best['area']:.0f}")
        else:
            print("👀 Vision: no targets")

        if self.cfg.save_frames_dir:
            _ensure_dir(self.cfg.save_frames_dir)
            # Draw annotations on original frame
            annotated = frame.copy()
            for det in result.get("detections", []):
                x, y, w, h = det["bbox"]
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(annotated, f"area:{det['area']:.0f}", (x, y - 6),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            
            out_path = os.path.join(self.cfg.save_frames_dir, f"frame_{step_idx:03d}.jpg")
            cv2.imwrite(out_path, annotated)

    def run(self) -> bool:
        if not self.fc.connect():
            return False
        try:
            self.fc.takeoff_if_needed()
            for i, (dx, dy, dz) in enumerate(self.cfg.waypoints_m, start=1):
                print(f"➡️ Move Δ({dx},{dy},{dz}) m …")
                self.fc.goto_relative(dx, dy, dz, speed=self.cfg.speed_mps)
                # Vision capture/annotate at each waypoint
                self._vision_step(i)
                self.fc.hover(self.cfg.hover_s)
            self.fc.land()
            return True
        finally:
            self.fc.disconnect()