"""
Cloud-based drone mission with integrated vision processing.
Runs entirely on GCP VM with AirSim.
"""

from __future__ import annotations
import os, sys

# Make "python src/main.py" work even if not installed
sys.path.append(os.path.dirname(__file__))

from flight_control import FlightController, FlightConfig
from mission_logic import MissionPlanner, MissionConfig


def main() -> int:
    cfg = FlightConfig(
        host=os.getenv("AIRSIM_HOST", "127.0.0.1"),
        port=int(os.getenv("AIRSIM_PORT", "41451")),
        vehicle_name=os.getenv("AIRSIM_VEHICLE") or None,
        takeoff_alt_m=float(os.getenv("AIRSIM_TAKEOFF_ALT", "5.0")),
    )

    save_dir = os.getenv("OUTPUT_DIR")  # e.g. ~/runs/2025-08-27_1230
    mcfg = MissionConfig(
        save_frames_dir=save_dir,
        vision_enabled=bool(int(os.getenv("VISION", "0")))
    )

    print(f"🚁 Starting vision-integrated drone mission")
    print(f"   Host: {cfg.host}:{cfg.port}")
    print(f"   Vision: {'enabled' if mcfg.vision_enabled else 'disabled'}")
    print(f"   Output: {save_dir or 'none'}")

    planner = MissionPlanner(FlightController(cfg), mcfg)
    try:
        ok = planner.run()
        print("✅ Mission completed successfully!" if ok else "❌ Mission failed to start (connection).")
        return 0 if ok else 1
    except KeyboardInterrupt:
        print("\n🛑 Mission interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Mission failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())