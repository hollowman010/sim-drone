"""
Entry point for sim_drone package.
Allows running as: python -m sim_drone or via simdrone command
"""

from __future__ import annotations
import sys
from .main import main as main_func


def main():
    """Entry point for console script."""
    return main_func()


if __name__ == "__main__":
    sys.exit(main())
