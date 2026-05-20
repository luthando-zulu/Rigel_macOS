#!/usr/bin/env python3
"""
RIGEL Business Installation Package
Handles installation automation, shortcuts, and system integration
"""

from .shortcut_manager import ShortcutManager, shortcut_manager

__all__ = [
    'ShortcutManager',
    'shortcut_manager'
]

__version__ = '1.0.0'
__author__ = 'Stella Lumen Development Team'
