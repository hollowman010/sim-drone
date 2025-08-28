#!/usr/bin/env python3
"""
Simple AirSim takeoff and flight test script.
Tests connectivity and basic drone control with real AirSim.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from flight_control import FlightController
from utils.config import get_default_config
from utils.logger import setup_logging, get_logger


def main():
    """Test basic AirSim connectivity and drone control."""
    setup_logging("INFO")
    logger = get_logger("takeoff_test")
    
    logger.info("🚁 Starting AirSim takeoff test...")
    
    # Load configuration
    config = get_default_config()
    
    # Create flight controller
    fc = FlightController(config)
    
    try:
        # Connect to AirSim
        logger.info("📡 Connecting to AirSim...")
        if not fc.connect():
            logger.error("❌ Failed to connect to AirSim")
            return False
        
        logger.info("✅ Connected to AirSim!")
        
        # Arm the drone
        logger.info("🔧 Arming drone...")
        if not fc.arm():
            logger.error("❌ Failed to arm drone")
            return False
        
        logger.info("✅ Drone armed and ready!")
        
        # Take off
        logger.info("🚀 Taking off...")
        if not fc.takeoff():
            logger.error("❌ Takeoff failed")
            return False
        
        logger.info("✅ Takeoff complete!")
        
        # Fly a small square pattern
        logger.info("🗺️  Flying a small square pattern...")
        if not fc.fly_square(side_m=5.0, alt_m=-5.0, speed=3.0):
            logger.error("❌ Square flight failed")
            return False
        
        logger.info("✅ Square flight complete!")
        
        # Land
        logger.info("🛬 Landing...")
        if not fc.land():
            logger.error("❌ Landing failed")
            return False
        
        logger.info("✅ Landing complete!")
        
        # Disarm
        logger.info("🔧 Disarming...")
        if not fc.disarm():
            logger.warning("⚠️  Failed to disarm drone")
        else:
            logger.info("✅ Drone disarmed")
        
        logger.info("🎉 AirSim takeoff test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during AirSim test: {e}")
        return False
        
    finally:
        # Cleanup
        fc.disconnect()
        logger.info("🔚 Test cleanup completed")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)