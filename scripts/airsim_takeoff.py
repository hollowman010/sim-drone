#!/usr/bin/env python3
"""
Simple AirSim takeoff and flight test script.
Direct AirSim calls for quick smoke testing.
"""

import os
import sys
import time
import airsim

HOST = os.getenv("AIRSIM_HOST", "127.0.0.1")
PORT = int(os.getenv("AIRSIM_PORT", "41451"))
VEHICLE = os.getenv("AIRSIM_VEHICLE", "Drone1")

def main():
    print(f"🚁 Connecting to AirSim at {HOST}:{PORT} …")
    
    try:
        client = airsim.MultirotorClient(ip=HOST, port=PORT)
        client.confirmConnection()
        client.enableApiControl(True, vehicle_name=VEHICLE)
        client.armDisarm(True, vehicle_name=VEHICLE)

        print("🚀 Taking off …")
        client.takeoffAsync(vehicle_name=VEHICLE).join()
        # Fly to 5 m above home; z is negative up in NED
        client.moveToZAsync(-5, 2, vehicle_name=VEHICLE).join()
        time.sleep(1)

        print("🚁 Hovering, then landing …")
        client.hoverAsync(vehicle_name=VEHICLE).join()
        client.landAsync(vehicle_name=VEHICLE).join()
        client.armDisarm(False, vehicle_name=VEHICLE)
        client.enableApiControl(False, vehicle_name=VEHICLE)
        print("✅ Takeoff test complete")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)