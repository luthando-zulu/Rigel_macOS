"""
RIGEL Business — macOS Trial Version (30-day)
Entry point for macOS .dmg (trial build).
"""
import platform

# macOS: enable high-DPI retina display support
if platform.system() == "Darwin":
    import os
    os.environ.setdefault("QT_MAC_WANTS_LAYER", "1")

from rigel_core import launch

if __name__ == "__main__":
    launch(build_mode="TRIAL")
