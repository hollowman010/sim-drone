#!/usr/bin/env python3
"""
Simple AirSim takeoff and flight test script.
Tests connectivity and basic drone control with real AirSim.
"""

import time
import airsim

IP = "127.0.0.1"
PORT = 41451  # AirSim default

def main():
    print("🚁 Starting AirSim takeoff test...")
    
    try:
        # Connect to AirSim
        print("Connecting to AirSim...")
        client = airsim.MultirotorClient(ip=IP, port=PORT)
        client.confirmConnection()
        print("✅ Connected to AirSim!")
        
        # Enable API control and arm the drone
        print("Enabling API control...")
        client.enableApiControl(True)
        client.armDisarm(True)
        print("✅ Drone armed and ready!")

        # Take off and rise to ~5m (Z is negative up in NED)
        print("Taking off...")
        client.takeoffAsync(timeout_sec=20).join()
        print("✅ Takeoff complete!")
        
        print("Moving to 5m altitude...")
        client.moveToZAsync(-5.0, velocity=2.0).join()
        print("✅ At 5m altitude!")

        # Small square to prove movement
        print("Flying a small square pattern...")
        client.moveByVelocityZAsync(3, 0, -5, 3).join()  # Forward
        print("✅ Forward movement complete")
        
        client.moveByVelocityZAsync(0, 3, -5, 3).join()  # Right
        print("✅ Right movement complete")
        
        client.moveByVelocityZAsync(-3, 0, -5, 3).join()  # Backward
        print("✅ Backward movement complete")
        
        client.moveByVelocityZAsync(0, -3, -5, 3).join()  # Left
        print("✅ Left movement complete")

        # Land
        print("Landing...")
        client.landAsync(timeout_sec=30).join()
        print("✅ Landing complete!")
        
        # Disarm and disable API control
        client.armDisarm(False)
        client.enableApiControl(False)
        print("✅ Drone disarmed and API control disabled")
        
        print("🎉 AirSim takeoff test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during AirSim test: {e}")
        raise

if __name__ == "__main__":
    main()
