"""
Simple drone flight mission - validates AirSim connection and basic flight.
Clean implementation focused on core flight operations.
"""

from __future__ import annotations
import os
import sys
from flight_control import FlightController, FlightConfig


def main() -> int:
    """Simple drone flight mission - forward, right, back home."""
    
    cfg = FlightConfig(
        host=os.getenv("AIRSIM_HOST", "127.0.0.1"),
        port=int(os.getenv("AIRSIM_PORT", "41451")),
        vehicle=os.getenv("AIRSIM_VEHICLE", "Drone1"),
        takeoff_alt_m=float(os.getenv("AIRSIM_TAKEOFF_ALT", "5")),
        speed_mps=float(os.getenv("AIRSIM_SPEED", "3")),
    )

    print(f"🚁 Starting drone mission at {cfg.host}:{cfg.port}")
    print(f"Vehicle: {cfg.vehicle}, Altitude: {cfg.takeoff_alt_m}m, Speed: {cfg.speed_mps}m/s")
    
    try:
        fc = FlightController(cfg)
        
        print("🔗 Connecting to AirSim...")
        if not fc.connect():
            print("❌ Failed to connect to AirSim")
            return 1
            
        print("🚀 Taking off...")
        if not fc.takeoff():
            print("❌ Takeoff failed")
            return 1
            
        # Simple demo flight pattern: forward 10m, right 5m, back home
        print("🗺️  Executing flight pattern...")
        
        print("   → Moving forward 10m...")
        if not fc.goto(10, 0):
            print("❌ Forward movement failed")
            return 1
            
        print("   → Moving right 5m...")
        if not fc.goto(10, 5):
            print("❌ Right movement failed")
            return 1
            
        print("   → Returning home...")
        if not fc.goto(0, 0):
            print("❌ Return home failed")
            return 1
            
        print("🚁 Hovering briefly...")
        fc.hover(2.0)
        
        print("🛬 Landing...")
        if not fc.land_and_shutdown():
            print("❌ Landing failed")
            return 1
            
        print("✅ Mission completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Mission interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Mission failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())