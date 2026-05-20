#!/usr/bin/env python3
"""
Database Package for Rigel Business
Cross-platform database management system
"""

from .database_manager import DatabaseManager
from .database_config import DatabaseConfig
from .backup_manager import BackupManager
from .migration_manager import MigrationManager
from .database_init import DatabaseInitializer

__all__ = [
    'DatabaseManager',
    'DatabaseConfig', 
    'BackupManager',
    'MigrationManager',
    'DatabaseInitializer'
]

__version__ = '1.0.0'
__author__ = 'RIGEL Business Development Team'
