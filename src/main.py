"""
Main entry point for the Drone Vision AirSim project.
Orchestrates the drone simulation with configurable live/demo modes.
"""

from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path
from typing import Dict, Any

from flight_control import FlightController
from mission_logic import MissionLogic
from vision_targeting import VisionProcessor
from utils.config import (
    load_config, 
    RUN_MODE, 
    AIRSIM_HOST, 
    AIRSIM_PORT,
    AppConfig,
    default_airsim_settings,
    write_settings_json
)
from utils.logger import setup_logging, get_logger

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Drone Vision AirSim Simulation")
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to configuration file"
    )
    parser.add_argument(
        "--mode", 
        choices=["live", "demo"], 
        default=RUN_MODE,
        help="Run mode: 'live' for real AirSim control, 'demo' for testing"
    )
    parser.add_argument(
        "--host", 
        default=AIRSIM_HOST,
        help="AirSim host address"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=AIRSIM_PORT,
        help="AirSim port number"
    )
    parser.add_argument(
        "--write-settings", 
        action="store_true",
        help="Write default AirSim settings to ~/Documents/AirSim/settings.json"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    return parser.parse_args()


def setup_environment(args) -> AppConfig:
    """Setup application environment and configuration."""
    # Setup logging
    log_dir = Path("logs") if args.mode == "live" else None
    setup_logging(args.log_level, log_dir)
    logger = get_logger("main")
    
    # Create app configuration
    config = AppConfig(
        airsim_host=args.host,
        airsim_port=args.port,
        log_level=args.log_level
    )
    
    logger.info(f"Starting Drone Vision AirSim Simulation")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"AirSim: {config.airsim_host}:{config.airsim_port}")
    
    return config


def write_airsim_settings(args):
    """Write default AirSim settings if requested."""
    if args.write_settings:
        logger = get_logger("main")
        settings = default_airsim_settings()
        settings["ApiServerPort"] = args.port
        path = write_settings_json(settings)
        logger.info(f"✅ Wrote AirSim settings to: {path}")


def run_demo():
    """Run demonstration mode without AirSim."""
    logger = get_logger("main")
    
    logger.info("=== DEMO MODE ===")
    logger.info("This is a demonstration mode for testing project structure.")
    logger.info("The drone will NOT actually move. For real flight, use --mode=live")
    logger.info("AirSim is not required for this demo")
    logger.info("")
    
    logger.info("🚁 Starting demonstration simulation...")
    time.sleep(0.5)
    
    logger.info("📡 Simulating drone connection...")
    time.sleep(0.5)
    
    logger.info("🔧 Simulating drone arming...")
    time.sleep(0.5)
    
    logger.info("🚀 Simulating drone takeoff...")
    time.sleep(1.0)
    
    logger.info("🗺️  Simulating waypoint navigation...")
    waypoints = [
        (50, 0, 20),
        (50, 50, 20), 
        (0, 50, 20),
        (0, 0, 20)
    ]
    
    for i, (x, y, z) in enumerate(waypoints, 1):
        logger.info(f"  → Moving to waypoint {i}: ({x}, {y}, {z})")
        time.sleep(0.8)
    
    logger.info("🛬 Simulating landing...")
    time.sleep(1.0)
    
    logger.info("✅ Demo mission completed successfully!")
    logger.info("")
    logger.info("To control a real drone in AirSim, run with: --mode=live")


def run_live_simulation(config: AppConfig):
    """Run live simulation with real AirSim control."""
    logger = get_logger("main")
    
    logger.info("=== LIVE MODE ===")
    logger.info("Connecting to real AirSim for drone control")
    
    # Load full configuration
    full_config = load_config()
    
    # Override with app config
    full_config["airsim"]["host"] = config.airsim_host
    full_config["airsim"]["port"] = config.airsim_port
    
    # Initialize components
    logger.info("🔧 Initializing flight controller...")
    flight_controller = FlightController(full_config)
    
    logger.info("🔧 Initializing vision processor...")
    vision_processor = VisionProcessor(full_config)
    
    logger.info("🔧 Initializing mission logic...")
    mission_logic = MissionLogic(full_config)
    
    logger.info("✅ All components initialized")
    
    # Run the main simulation
    try:
        run_simulation(flight_controller, vision_processor, mission_logic, logger)
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise
    finally:
        # Cleanup
        flight_controller.disconnect()
        logger.info("🔚 Simulation cleanup completed")


def run_simulation(flight_controller, vision_processor, mission_logic, logger):
    """Run the main simulation loop with real drone control."""
    try:
        # Connect to AirSim
        logger.info("📡 Connecting to AirSim...")
        if not flight_controller.connect():
            raise Exception("Failed to connect to AirSim")
        
        logger.info("✅ Connected to AirSim")
        
        # Arm the drone
        logger.info("🔧 Arming drone...")
        if not flight_controller.arm():
            raise Exception("Failed to arm drone")
        
        logger.info("✅ Drone armed")
        
        # Take off
        logger.info("🚀 Taking off...")
        if not flight_controller.takeoff():
            raise Exception("Failed to takeoff")
        
        logger.info("✅ Takeoff completed")
        
        # Execute flight pattern
        logger.info("🗺️  Executing flight pattern...")
        if not flight_controller.fly_square(side_m=5.0, alt_m=-5.0, speed=3.0):
            raise Exception("Failed to complete flight pattern")
        
        logger.info("✅ Flight pattern completed")
        
        # Optional: Vision processing demonstration
        logger.info("📸 Collecting sensor data...")
        sensor_data = flight_controller.get_sensor_data()
        
        if sensor_data and "rgb_image" in sensor_data:
            logger.info(f"📸 Captured RGB image: {sensor_data['rgb_image'].shape}")
            
            # Process with vision system
            vision_result = vision_processor.process_frame(sensor_data["rgb_image"])
            logger.info(f"👁️  Vision processing result: {vision_result}")
        
        # Land the drone
        logger.info("🛬 Landing...")
        if not flight_controller.land():
            raise Exception("Failed to land")
        
        logger.info("✅ Landing completed")
        
        # Disarm
        logger.info("🔧 Disarming drone...")
        if not flight_controller.disarm():
            logger.warning("Failed to disarm drone")
        else:
            logger.info("✅ Drone disarmed")
        
        logger.info("🎉 Mission completed successfully!")
        
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        
        # Emergency cleanup
        try:
            logger.info("🚨 Attempting emergency landing...")
            flight_controller.land()
            flight_controller.disarm()
        except:
            logger.error("Emergency cleanup failed")
        
        raise


def main():
    """Main application entry point."""
    args = parse_args()
    config = setup_environment(args)
    
    # Write AirSim settings if requested
    write_airsim_settings(args)
    
    try:
        if args.mode == "demo":
            run_demo()
        else:
            run_live_simulation(config)
            
    except KeyboardInterrupt:
        logger = get_logger("main")
        logger.info("🛑 Simulation interrupted by user")
    except Exception as e:
        logger = get_logger("main") 
        logger.error(f"❌ Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()