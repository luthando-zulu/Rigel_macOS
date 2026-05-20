#!/usr/bin/env python3
"""
RIGEL Business Assets Package
Contains logos, branding, and other visual assets
"""

from .logo.logo_widget import LogoWidget, logo_manager
from .branding.branding_manager import BrandingManager, branding_manager

__all__ = [
    'LogoWidget',
    'logo_manager',
    'BrandingManager',
    'branding_manager'
]

__version__ = '1.0.0'
__author__ = 'Stella Lumen Development Team'
