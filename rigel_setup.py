#!/usr/bin/env python3
"""
RIGEL Business Setup and Installation Wizard
Entry point for first-time installation
"""

import sys
from PyQt6.QtWidgets import QApplication
from installation.installation_wizard import run_installation_wizard

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if run_installation_wizard(app):
        print("RIGEL Business installed successfully!")
        sys.exit(0)
    else:
        print("Installation cancelled")
        sys.exit(1)
