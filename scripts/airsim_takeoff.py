#!/usr/bin/env python3
"""
Simple AirSim takeoff and flight test script.
Tests connectivity and basic drone control with real AirSim.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from flight_control import FlightController
from utils.config import load_config
from utils.logger import setup_logging, get_logger


def main():
    """Test basic AirSim connectivity and drone control."""
    setup_logging("INFO")
    logger = get_logger("takeoff_test")
    
    logger.info("🚁 Starting AirSim smoke test...")
    
    # Load configuration (picks up config/settings.json if present)
    config = load_config()
    
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
        takeoff_height = config.get("drone", {}).get("takeoff_height", 3.5)
        if not fc.takeoff():
            logger.error("❌ Takeoff failed")
            return False
        
        logger.info("✅ Takeoff complete!")
        
        # Move to takeoff height
        logger.info(f"📏 Moving to {takeoff_height}m altitude...")
        if not fc.move_to_position(0, 0, -takeoff_height, 2.0):
            logger.error("❌ Failed to reach altitude")
            return False
            
        # Hover for a few seconds
        logger.info("🚁 Hovering for 3 seconds...")
        time.sleep(3)
        
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
        
        logger.info("✅ AirSim smoke test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during AirSim test: {e}")
        return False
        
    finally:
        # Cleanup
        fc.disconnect()
        logger.info("🔚 Smoke test cleanup completed")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)