"""
RIGEL Business — macOS Full Version
Entry point for macOS .dmg (full build).
"""
import platform

if platform.system() == "Darwin":
    import os
    os.environ.setdefault("QT_MAC_WANTS_LAYER", "1")

from rigel_core import launch

if __name__ == "__main__":
    launch(build_mode="FULL")
