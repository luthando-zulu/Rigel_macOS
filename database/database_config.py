#!/usr/bin/env python3
"""
Database Configuration Manager
Handles database settings, migrations, and version management
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import platform

class DatabaseConfig:
    """Database configuration and migration manager"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.config_file = data_dir / "database_config.json"
        self.migrations_dir = data_dir / "migrations"
        self.migrations_dir.mkdir(exist_ok=True)
        
        self.current_version = "1.0.0"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load database configuration"""
        default_config = {
            "version": self.current_version,
            "storage_type": "sqlite",
            "auto_backup": True,
            "backup_frequency": "daily",
            "max_backups": 30,
            "compression": True,
            "encryption": False,
            "performance": {
                "cache_size": 2000,
                "temp_store": "memory",
                "synchronous": "NORMAL",
                "journal_mode": "WAL"
            },
            "migrations": {
                "last_applied": None,
                "pending": []
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                return {**default_config, **config}
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        else:
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save database configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get configuration setting"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set_setting(self, key: str, value: Any):
        """Set configuration setting"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def create_migration(self, version: str, description: str, sql_statements: List[str]) -> Path:
        """Create a new migration file"""
        migration_data = {
            "version": version,
            "description": description,
            "created_date": datetime.now().isoformat(),
            "applied_date": None,
            "sql_statements": sql_statements
        }
        
        migration_file = self.migrations_dir / f"migration_{version.replace('.', '_')}.json"
        with open(migration_file, 'w') as f:
            json.dump(migration_data, f, indent=2)
        
        # Add to pending migrations
        pending = self.get_setting('migrations.pending', [])
        pending.append(version)
        self.set_setting('migrations.pending', pending)
        
        return migration_file
    
    def apply_migrations(self, db_path: Path) -> bool:
        """Apply pending migrations"""
        try:
            with sqlite3.connect(db_path) as conn:
                pending_migrations = self.get_setting('migrations.pending', [])
                applied_migrations = self.get_setting('migrations.last_applied', [])
                
                for version in pending_migrations:
                    migration_file = self.migrations_dir / f"migration_{version.replace('.', '_')}.json"
                    
                    if migration_file.exists():
                        with open(migration_file, 'r') as f:
                            migration = json.load(f)
                        
                        # Apply SQL statements
                        for sql in migration['sql_statements']:
                            conn.execute(sql)
                        
                        # Mark as applied
                        migration['applied_date'] = datetime.now().isoformat()
                        with open(migration_file, 'w') as f:
                            json.dump(migration, f, indent=2)
                        
                        applied_migrations.append(version)
                
                conn.commit()
                
                # Update config
                self.set_setting('migrations.last_applied', applied_migrations)
                self.set_setting('migrations.pending', [])
                
                return True
                
        except Exception as e:
            print(f"Migration failed: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status"""
        pending = self.get_setting('migrations.pending', [])
        applied = self.get_setting('migrations.last_applied', [])
        
        return {
            "current_version": self.current_version,
            "pending_migrations": pending,
            "applied_migrations": applied,
            "total_migrations": len(list(self.migrations_dir.glob("migration_*.json")))
        }
    
    def optimize_for_platform(self, db_path: Path):
        """Optimize database settings for current platform"""
        system = platform.system()
        
        try:
            with sqlite3.connect(db_path) as conn:
                if system == "Windows":
                    # Windows optimizations
                    conn.execute("PRAGMA page_size = 4096")
                    conn.execute("PRAGMA cache_size = -2000")
                elif system == "Darwin":
                    # macOS optimizations
                    conn.execute("PRAGMA page_size = 4096")
                    conn.execute("PRAGMA cache_size = -4000")
                else:
                    # Linux optimizations
                    conn.execute("PRAGMA page_size = 4096")
                    conn.execute("PRAGMA cache_size = -2000")
                
                # Apply performance settings from config
                perf_settings = self.get_setting('performance', {})
                
                if 'cache_size' in perf_settings:
                    conn.execute(f"PRAGMA cache_size = {perf_settings['cache_size']}")
                
                if 'temp_store' in perf_settings:
                    conn.execute(f"PRAGMA temp_store = {perf_settings['temp_store']}")
                
                if 'synchronous' in perf_settings:
                    conn.execute(f"PRAGMA synchronous = {perf_settings['synchronous']}")
                
                if 'journal_mode' in perf_settings:
                    conn.execute(f"PRAGMA journal_mode = {perf_settings['journal_mode']}")
                
                conn.commit()
                
        except Exception as e:
            print(f"Platform optimization failed: {e}")
    
    def setup_auto_backup(self, backup_manager) -> bool:
        """Setup automatic backup configuration"""
        if not self.get_setting('auto_backup', True):
            return False
        
        try:
            # Create backup schedule based on frequency
            frequency = self.get_setting('backup_frequency', 'daily')
            max_backups = self.get_setting('max_backups', 30)
            
            backup_config = {
                'frequency': frequency,
                'max_backups': max_backups,
                'compression': self.get_setting('compression', True),
                'encryption': self.get_setting('encryption', False)
            }
            
            # Save backup configuration
            backup_config_file = self.data_dir / "backup_config.json"
            with open(backup_config_file, 'w') as f:
                json.dump(backup_config, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Auto backup setup failed: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate database configuration"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check storage type
        storage_type = self.get_setting('storage_type', 'sqlite')
        if storage_type not in ['sqlite', 'json']:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Invalid storage type: {storage_type}")
        
        # Check backup settings
        max_backups = self.get_setting('max_backups', 30)
        if not isinstance(max_backups, int) or max_backups < 1:
            validation_result['is_valid'] = False
            validation_result['errors'].append("max_backups must be a positive integer")
        
        # Check performance settings
        cache_size = self.get_setting('performance.cache_size', 2000)
        if not isinstance(cache_size, int) or cache_size < 100:
            validation_result['warnings'].append("cache_size should be at least 100")
        
        journal_mode = self.get_setting('performance.journal_mode', 'WAL')
        if journal_mode not in ['DELETE', 'TRUNCATE', 'PERSIST', 'MEMORY', 'WAL', 'OFF']:
            validation_result['warnings'].append(f"Unusual journal_mode: {journal_mode}")
        
        return validation_result
    
    def export_config(self, export_path: Path) -> bool:
        """Export configuration to file"""
        try:
            with open(export_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Config export failed: {e}")
            return False
    
    def import_config(self, import_path: Path) -> bool:
        """Import configuration from file"""
        try:
            with open(import_path, 'r') as f:
                imported_config = json.load(f)
            
            # Validate imported config
            self.config = imported_config
            validation = self.validate_config()
            
            if validation['is_valid']:
                self._save_config(self.config)
                return True
            else:
                print("Invalid configuration imported:")
                for error in validation['errors']:
                    print(f"  - {error}")
                return False
                
        except Exception as e:
            print(f"Config import failed: {e}")
            return False
    
    def reset_config(self):
        """Reset configuration to defaults"""
        self.config = {
            "version": self.current_version,
            "storage_type": "sqlite",
            "auto_backup": True,
            "backup_frequency": "daily",
            "max_backups": 30,
            "compression": True,
            "encryption": False,
            "performance": {
                "cache_size": 2000,
                "temp_store": "memory",
                "synchronous": "NORMAL",
                "journal_mode": "WAL"
            },
            "migrations": {
                "last_applied": None,
                "pending": []
            }
        }
        self._save_config(self.config)
