#!/usr/bin/env python3
"""
Simple test script to verify AirSim connection on GPU VM.
This will test if AirSim server is running and accessible.
"""

import airsim
import time

def test_airsim_connection():
    """Test connection to AirSim server."""
    print("Testing AirSim connection...")
    
    try:
        # Create client
        client = airsim.MultirotorClient()
        print("✓ AirSim client created")
        
        # Try to connect
        client.confirmConnection()
        print("✓ Successfully connected to AirSim server!")
        
        # Get drone state
        state = client.getMultirotorState()
        print(f"✓ Drone position: {state.kinematics_estimated.position}")
        
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nThis means:")
        print("1. AirSim server is not running")
        print("2. Need to start Unreal Engine with AirSim plugin")
        print("3. Or use a pre-built AirSim binary")
        return False

if __name__ == "__main__":
    test_airsim_connection()
