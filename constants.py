#!/usr/bin/env python3
"""
RIGEL Business Constants
"""

# RIGEL Business Colors
RIGEL_TXT = '#00B050'
RIGEL_BG = '#F5F5F5'
RIGEL_ACCENT = '#00B050'
WHITE = '#FFFFFF'
BLACK = '#000000'
GRAY = '#808080'
LIGHT_GRAY = '#F0F0F0'
DARK_GRAY = '#404040'
RED = '#FF0000'
GREEN = '#00FF00'
BLUE = '#0000FF'
YELLOW = '#FFFF00'
ORANGE = '#FFA500'
PURPLE = '#800080'
CYAN = '#00FFFF'
MAGENTA = '#FF00FF'

# Application Info
APP_NAME = 'RIGEL Business'
APP_VERSION = '1.0.0'
COMPANY_NAME = 'Stella Lumen'
WEBSITE = 'www.stella-lumen.com'

# Database Paths
DB_PATH = 'data/rigel_business.db'
BACKUP_PATH = 'backups/'
LICENSE_PATH = 'license/'

# UI Settings
WINDOW_WIDTH = 1380
WINDOW_HEIGHT = 820
MIN_WIDTH = 1100
MIN_HEIGHT = 680

# Business Settings
TRIAL_DAYS = 30
LICENSE_KEY_LENGTH = 16

# Create objects for backward compatibility
class C:
    """Constants object for backward compatibility"""
    RIGEL_TXT = RIGEL_TXT
    RIGEL_BG = RIGEL_BG
    RIGEL_ACCENT = RIGEL_ACCENT
    WHITE = WHITE
    BLACK = BLACK
    GRAY = GRAY
    LIGHT_GRAY = LIGHT_GRAY
    DARK_GRAY = DARK_GRAY
    RED = RED
    GREEN = GREEN
    BLUE = BLUE
    YELLOW = YELLOW
    ORANGE = ORANGE
    PURPLE = PURPLE
    CYAN = CYAN
    MAGENTA = MAGENTA
    APP_NAME = APP_NAME
    APP_VERSION = APP_VERSION
    COMPANY_NAME = COMPANY_NAME
    WEBSITE = WEBSITE
    DB_PATH = DB_PATH
    BACKUP_PATH = BACKUP_PATH
    LICENSE_PATH = LICENSE_PATH
    WINDOW_WIDTH = WINDOW_WIDTH
    WINDOW_HEIGHT = WINDOW_HEIGHT
    MIN_WIDTH = MIN_WIDTH
    MIN_HEIGHT = MIN_HEIGHT
    TRIAL_DAYS = TRIAL_DAYS
    LICENSE_KEY_LENGTH = LICENSE_KEY_LENGTH

class F:
    """Styles object for backward compatibility"""
    @staticmethod
    def get_stylesheet():
        """Get main application stylesheet"""
        return "QMainWindow { background-color: #F5F5F5; } QPushButton { background-color: #00B050; color: white; }"
    
    @staticmethod
    def get_dialog_style():
        """Get dialog stylesheet"""
        return "QDialog { background-color: #F5F5F5; }"
