"""
Entry point for sim_drone package.
Allows running as: python -m sim_drone
"""

from __future__ import annotations
import sys
from .main import main

if __name__ == "__main__":
    sys.exit(main())
