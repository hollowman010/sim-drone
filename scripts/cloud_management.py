#!/usr/bin/env python3
"""
Cloud Management Script for Drone Simulation
Automatically manages GCP instance lifecycle to optimize costs
"""

import os
import time
import subprocess
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class CloudManager:
    def __init__(self, project_id: str, instance_name: str, zone: str):
        self.project_id = project_id
        self.instance_name = instance_name
        self.zone = zone
        self.logger = self._setup_logging()

        # Configuration
        self.idle_timeout = 30 * 60  # 30 minutes of inactivity
        self.simulation_running = False
        self.last_activity = time.time()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the cloud manager"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("/tmp/cloud_manager.log"),
                logging.StreamHandler(),
            ],
        )
        return logging.getLogger(__name__)

    def check_simulation_status(self) -> bool:
        """Check if the drone simulation is currently running"""
        try:
            # Check for Python processes running our simulation
            result = subprocess.run(
                ["pgrep", "-f", "main.py"], capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Error checking simulation status: {e}")
            return False

    def check_user_activity(self) -> bool:
        """Check if there's recent user activity (SSH sessions, etc.)"""
        try:
            # Check for active SSH sessions
            result = subprocess.run(["who"], capture_output=True, text=True)
            if result.stdout.strip():
                return True

            # Check for recent file modifications in project directory
            # Get project directory relative to this script
            project_dir = str(Path(__file__).resolve().parents[1])
            if os.path.exists(project_dir):
                # Check if any files were modified in the last 10 minutes
                recent_files = subprocess.run(
                    ["find", project_dir, "-type", "f", "-mmin", "-10"],
                    capture_output=True,
                    text=True,
                )
                if recent_files.stdout.strip():
                    return True

            return False
        except Exception as e:
            self.logger.error(f"Error checking user activity: {e}")
            return True  # Assume activity if we can't check

    def check_system_load(self) -> float:
        """Check current system load"""
        try:
            with open("/proc/loadavg", "r") as f:
                load = float(f.read().split()[0])
            return load
        except Exception as e:
            self.logger.error(f"Error checking system load: {e}")
            return 0.0

    def should_shutdown(self) -> bool:
        """Determine if the instance should be shut down"""
        # Don't shutdown if simulation is running
        if self.check_simulation_status():
            self.logger.info("Simulation is running - keeping instance alive")
            return False

        # Don't shutdown if there's user activity
        if self.check_user_activity():
            self.logger.info("User activity detected - keeping instance alive")
            return False

        # Don't shutdown if system load is high
        load = self.check_system_load()
        if load > 1.0:
            self.logger.info(f"High system load ({load}) - keeping instance alive")
            return False

        # Check if we've been idle for too long
        idle_time = time.time() - self.last_activity
        if idle_time > self.idle_timeout:
            self.logger.info(
                f"Instance idle for {idle_time/60:.1f} minutes - scheduling shutdown"
            )
            return True

        return False

    def shutdown_instance(self):
        """Safely shutdown the instance"""
        try:
            self.logger.info("Initiating safe shutdown...")

            # Stop any running simulations gracefully
            if self.check_simulation_status():
                self.logger.info("Stopping running simulation...")
                subprocess.run(["pkill", "-f", "main.py"], timeout=30)
                time.sleep(5)  # Give processes time to clean up

            # Create a shutdown marker file
            with open("/tmp/shutdown_requested", "w") as f:
                f.write(f"Shutdown requested at {datetime.now()}\n")

            # Shutdown the instance
            subprocess.run(
                [
                    "gcloud",
                    "compute",
                    "instances",
                    "stop",
                    self.instance_name,
                    "--zone",
                    self.zone,
                    "--project",
                    self.project_id,
                ]
            )

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    def start_instance(self):
        """Start the instance"""
        try:
            self.logger.info("Starting instance...")
            subprocess.run(
                [
                    "gcloud",
                    "compute",
                    "instances",
                    "start",
                    self.instance_name,
                    "--zone",
                    self.zone,
                    "--project",
                    self.project_id,
                ]
            )
        except Exception as e:
            self.logger.error(f"Error starting instance: {e}")

    def get_instance_status(self) -> Dict:
        """Get current instance status"""
        try:
            result = subprocess.run(
                [
                    "gcloud",
                    "compute",
                    "instances",
                    "describe",
                    self.instance_name,
                    "--zone",
                    self.zone,
                    "--project",
                    self.project_id,
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Error getting instance status: {e}")
            return {}

    def run_monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting cloud management monitoring...")

        while True:
            try:
                # Update activity timestamp if there's activity
                if self.check_user_activity() or self.check_simulation_status():
                    self.last_activity = time.time()

                # Check if we should shutdown
                if self.should_shutdown():
                    self.shutdown_instance()
                    break

                # Log status every 5 minutes
                if int(time.time()) % 300 == 0:
                    status = self.get_instance_status()
                    self.logger.info(
                        f"Instance status: {status.get('status', 'unknown')}"
                    )

                time.sleep(60)  # Check every minute

            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)


def main():
    """Main function"""
    # Configuration with environment variable overrides
    PROJECT_ID = os.getenv("GCP_PROJECT", "drone-sim-project")
    INSTANCE_NAME = os.getenv("GCP_INSTANCE", "airsim-gpu") 
    ZONE = os.getenv("GCP_ZONE", "us-central1-a")

    manager = CloudManager(PROJECT_ID, INSTANCE_NAME, ZONE)

    # Check command line arguments
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            manager.start_instance()
        elif sys.argv[1] == "stop":
            manager.shutdown_instance()
        elif sys.argv[1] == "status":
            status = manager.get_instance_status()
            print(json.dumps(status, indent=2))
        elif sys.argv[1] == "monitor":
            manager.run_monitoring_loop()
    else:
        print("Usage:")
        print("  python cloud_management.py start   - Start instance")
        print("  python cloud_management.py stop    - Stop instance")
        print("  python cloud_management.py status  - Show instance status")
        print("  python cloud_management.py monitor - Run monitoring loop")


if __name__ == "__main__":
    main()
