"""
RIGEL Business — Windows Full Version
Entry point for Windows .exe (full build).
"""
import sys
import os

# PyInstaller creates a temp folder and stores its path in _MEIPASS
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    base_dir = sys._MEIPASS
    sys.path.insert(0, base_dir)

from rigel_core import launch

if __name__ == "__main__":
    launch(build_mode="FULL")
