#!/usr/bin/env python3
"""
RIGEL Business v4.1.0 - Main Launcher
Launches the application with installation wizard if needed
"""

import sys
import os
from pathlib import Path

# Ensure workspace root is on the path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Now launch the app
if __name__ == "__main__":
    try:
        from rigel_pyqt6.rigel_core import launch_application
        sys.exit(launch_application())
    except ImportError as e:
        print(f"Error importing application: {e}")
        print("Trying alternate import path...")
        try:
            from rigel_core import launch_application
            sys.exit(launch_application())
        except Exception as e2:
            print(f"Failed to launch application: {e2}")
            sys.exit(1)
