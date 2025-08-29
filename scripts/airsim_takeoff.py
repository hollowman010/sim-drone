#!/usr/bin/env python3
import argparse, sys, time
from loguru import logger

try:
    import airsim
except Exception:
    logger.error("airsim package not installed")
    sys.exit(2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=20)
    args = ap.parse_args()

    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)

    logger.info("Taking off…")
    client.takeoffAsync(timeout_sec=args.timeout).join()
    time.sleep(1)
    state = client.getMultirotorState()
    z = state.kinematics_estimated.position.z_val
    logger.info(f"Altitude: {-z:.2f} m")
    client.hoverAsync().join()
    logger.info("✅ preflight OK")

if __name__ == "__main__":
    main()