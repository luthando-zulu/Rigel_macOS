#!/usr/bin/env python3
"""
Database Backup Manager
Handles automated backups, compression, and restoration
"""

import os
import json
import shutil
import zipfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import platform
import tempfile

class BackupManager:
    """Database backup and restoration manager"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.backup_dir = data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        self.system = platform.system()
        self.config_file = data_dir / "backup_config.json"
        self.config = self._load_backup_config()
    
    def _load_backup_config(self) -> Dict[str, Any]:
        """Load backup configuration"""
        default_config = {
            "frequency": "daily",
            "max_backups": 30,
            "compression": True,
            "encryption": False,
            "backup_types": ["full", "incremental"],
            "schedule": {
                "daily": {"time": "02:00", "enabled": True},
                "weekly": {"day": "sunday", "time": "02:00", "enabled": False},
                "monthly": {"day": 1, "time": "02:00", "enabled": False}
            },
            "retention": {
                "daily": 7,
                "weekly": 4,
                "monthly": 12
            },
            "last_backup": None,
            "backup_history": []
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                print(f"Error loading backup config: {e}")
                return default_config
        else:
            self._save_backup_config(default_config)
            return default_config
    
    def _save_backup_config(self, config: Dict[str, Any]):
        """Save backup configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving backup config: {e}")
    
    def create_backup(self, backup_type: str = "full", description: str = "") -> Path:
        """Create database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{backup_type}_backup_{timestamp}"
        
        if description:
            backup_name += f"_{description.replace(' ', '_')}"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            if backup_type == "full":
                backup_path = self._create_full_backup(backup_path)
            elif backup_type == "incremental":
                backup_path = self._create_incremental_backup(backup_path)
            else:
                raise ValueError(f"Unknown backup type: {backup_type}")
            
            # Update backup history
            self._update_backup_history(backup_type, backup_path, description)
            
            # Clean old backups
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            print(f"Backup creation failed: {e}")
            raise
    
    def _create_full_backup(self, backup_path: Path) -> Path:
        """Create full database backup"""
        # Backup SQLite database
        sqlite_db = self.data_dir / "rigel_business.db"
        json_dir = self.data_dir / "json_data"
        
        if self.config.get("compression", True):
            backup_path = backup_path.with_suffix('.zip')
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add SQLite database
                if sqlite_db.exists():
                    zipf.write(sqlite_db, "rigel_business.db")
                
                # Add JSON files
                if json_dir.exists():
                    for json_file in json_dir.glob("*.json"):
                        zipf.write(json_file, f"json_data/{json_file.name}")
                
                # Add configuration files
                config_files = [
                    "database_config.json",
                    "backup_config.json"
                ]
                for config_file in config_files:
                    config_path = self.data_dir / config_file
                    if config_path.exists():
                        zipf.write(config_path, config_file)
        else:
            # Uncompressed backup
            backup_path = backup_path.with_suffix('.bak')
            
            # Create backup directory
            backup_path.mkdir(exist_ok=True)
            
            # Copy files
            if sqlite_db.exists():
                shutil.copy2(sqlite_db, backup_path / "rigel_business.db")
            
            if json_dir.exists():
                backup_json_dir = backup_path / "json_data"
                backup_json_dir.mkdir(exist_ok=True)
                for json_file in json_dir.glob("*.json"):
                    shutil.copy2(json_file, backup_json_dir / json_file.name)
            
            # Copy config files
            for config_file in ["database_config.json", "backup_config.json"]:
                config_path = self.data_dir / config_file
                if config_path.exists():
                    shutil.copy2(config_path, backup_path / config_file)
        
        return backup_path
    
    def _create_incremental_backup(self, backup_path: Path) -> Path:
        """Create incremental backup (only changed files)"""
        last_backup_time = self.config.get("last_backup")
        if not last_backup_time:
            # No previous backup, create full backup instead
            return self._create_full_backup(backup_path)
        
        last_backup_dt = datetime.fromisoformat(last_backup_time)
        
        # Check for changed files
        sqlite_db = self.data_dir / "rigel_business.db"
        json_dir = self.data_dir / "json_data"
        
        changed_files = []
        
        # Check SQLite database
        if sqlite_db.exists():
            db_mtime = datetime.fromtimestamp(sqlite_db.stat().st_mtime)
            if db_mtime > last_backup_dt:
                changed_files.append(sqlite_db)
        
        # Check JSON files
        if json_dir.exists():
            for json_file in json_dir.glob("*.json"):
                file_mtime = datetime.fromtimestamp(json_file.stat().st_mtime)
                if file_mtime > last_backup_dt:
                    changed_files.append(json_file)
        
        if not changed_files:
            # No changes, create empty backup marker
            backup_path = backup_path.with_suffix('.empty')
            backup_path.write_text(f"No changes since {last_backup_time}")
            return backup_path
        
        # Create incremental backup with changed files
        if self.config.get("compression", True):
            backup_path = backup_path.with_suffix('.zip')
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in changed_files:
                    if file_path == sqlite_db:
                        zipf.write(file_path, "rigel_business.db")
                    else:
                        zipf.write(file_path, f"json_data/{file_path.name}")
        else:
            backup_path = backup_path.with_suffix('.inc')
            backup_path.mkdir(exist_ok=True)
            
            for file_path in changed_files:
                if file_path == sqlite_db:
                    shutil.copy2(file_path, backup_path / "rigel_business.db")
                else:
                    backup_json_dir = backup_path / "json_data"
                    backup_json_dir.mkdir(exist_ok=True)
                    shutil.copy2(file_path, backup_json_dir / file_path.name)
        
        return backup_path
    
    def restore_backup(self, backup_path: Path) -> bool:
        """Restore database from backup"""
        try:
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Create restore point before restoration
            restore_point = self.create_backup("restore_point", f"Before restoring {backup_path.name}")
            
            if backup_path.suffix == '.zip':
                # Restore from compressed backup
                return self._restore_from_zip(backup_path)
            elif backup_path.suffix == '.bak':
                # Restore from uncompressed backup
                return self._restore_from_directory(backup_path)
            elif backup_path.suffix == '.inc':
                # Restore from incremental backup
                return self._restore_from_incremental(backup_path)
            else:
                raise ValueError(f"Unsupported backup format: {backup_path.suffix}")
                
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def _restore_from_zip(self, backup_path: Path) -> bool:
        """Restore from ZIP backup"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Extract to temporary directory first
                with tempfile.TemporaryDirectory() as temp_dir:
                    zipf.extractall(temp_dir)
                    
                    # Verify backup integrity
                    if not self._verify_backup_integrity(Path(temp_dir)):
                        return False
                    
                    # Restore files
                    self._restore_files_from_directory(Path(temp_dir))
            
            return True
            
        except Exception as e:
            print(f"ZIP restore failed: {e}")
            return False
    
    def _restore_from_directory(self, backup_path: Path) -> bool:
        """Restore from directory backup"""
        try:
            # Verify backup integrity
            if not self._verify_backup_integrity(backup_path):
                return False
            
            # Restore files
            self._restore_files_from_directory(backup_path)
            
            return True
            
        except Exception as e:
            print(f"Directory restore failed: {e}")
            return False
    
    def _restore_from_incremental(self, backup_path: Path) -> bool:
        """Restore from incremental backup"""
        try:
            # Incremental backups only contain changed files
            # We need to apply them on top of the last full backup
            
            # Find the last full backup
            full_backups = list(self.backup_dir.glob("full_backup_*.zip"))
            full_backups.extend(self.backup_dir.glob("full_backup_*.bak"))
            
            if not full_backups:
                print("No full backup found to apply incremental changes")
                return False
            
            # Get the most recent full backup
            latest_full_backup = max(full_backups, key=lambda x: x.stat().st_mtime)
            
            # Restore full backup first
            if not self.restore_backup(latest_full_backup):
                return False
            
            # Then apply incremental changes
            if backup_path.suffix == '.zip':
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        zipf.extractall(temp_dir)
                        self._restore_files_from_directory(Path(temp_dir))
            else:
                self._restore_files_from_directory(backup_path)
            
            return True
            
        except Exception as e:
            print(f"Incremental restore failed: {e}")
            return False
    
    def _verify_backup_integrity(self, backup_dir: Path) -> bool:
        """Verify backup integrity"""
        required_files = ["rigel_business.db"]
        
        for required_file in required_files:
            file_path = backup_dir / required_file
            if not file_path.exists():
                print(f"Required file missing from backup: {required_file}")
                return False
        
        # Verify SQLite database integrity
        db_path = backup_dir / "rigel_business.db"
        if db_path.exists():
            try:
                with sqlite3.connect(db_path) as conn:
                    integrity_result = conn.execute("PRAGMA integrity_check").fetchone()
                    if integrity_result[0] != 'ok':
                        print(f"Database integrity check failed: {integrity_result[0]}")
                        return False
            except Exception as e:
                print(f"Database verification failed: {e}")
                return False
        
        return True
    
    def _restore_files_from_directory(self, source_dir: Path):
        """Restore files from source directory"""
        # Restore SQLite database
        source_db = source_dir / "rigel_business.db"
        if source_db.exists():
            target_db = self.data_dir / "rigel_business.db"
            shutil.copy2(source_db, target_db)
        
        # Restore JSON files
        source_json = source_dir / "json_data"
        if source_json.exists():
            target_json = self.data_dir / "json_data"
            target_json.mkdir(exist_ok=True)
            
            for json_file in source_json.glob("*.json"):
                shutil.copy2(json_file, target_json / json_file.name)
        
        # Restore configuration files
        for config_file in ["database_config.json", "backup_config.json"]:
            source_config = source_dir / config_file
            if source_config.exists():
                target_config = self.data_dir / config_file
                shutil.copy2(source_config, target_config)
    
    def _update_backup_history(self, backup_type: str, backup_path: Path, description: str):
        """Update backup history"""
        backup_info = {
            "timestamp": datetime.now().isoformat(),
            "type": backup_type,
            "path": str(backup_path),
            "description": description,
            "size": backup_path.stat().st_size if backup_path.exists() else 0
        }
        
        history = self.config.get("backup_history", [])
        history.append(backup_info)
        
        # Keep only last 100 backup records
        if len(history) > 100:
            history = history[-100:]
        
        self.config["backup_history"] = history
        self.config["last_backup"] = backup_info["timestamp"]
        self._save_backup_config(self.config)
    
    def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        retention = self.config.get("retention", {})
        max_backups = self.config.get("max_backups", 30)
        
        try:
            # Get all backup files
            backup_files = list(self.backup_dir.glob("*"))
            backup_files = [f for f in backup_files if f.is_file()]
            
            # Sort by creation time (oldest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Remove files older than retention period
            cutoff_date = datetime.now() - timedelta(days=max_backups)
            
            for backup_file in backup_files:
                file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_mtime < cutoff_date:
                    backup_file.unlink()
                    print(f"Removed old backup: {backup_file.name}")
            
            # Also check for empty backup directories
            for backup_dir in self.backup_dir.glob("*/"):
                if backup_dir.is_dir() and not any(backup_dir.iterdir()):
                    backup_dir.rmdir()
                    print(f"Removed empty backup directory: {backup_dir.name}")
                    
        except Exception as e:
            print(f"Backup cleanup failed: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*"):
            if backup_file.is_file():
                backup_info = {
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size": backup_file.stat().st_size,
                    "created": datetime.fromtimestamp(backup_file.stat().st_mtime),
                    "type": self._determine_backup_type(backup_file)
                }
                backups.append(backup_info)
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return backups
    
    def _determine_backup_type(self, backup_path: Path) -> str:
        """Determine backup type from filename"""
        name = backup_path.name.lower()
        
        if "full_backup" in name:
            return "full"
        elif "incremental_backup" in name or name.endswith('.inc'):
            return "incremental"
        elif "restore_point" in name:
            return "restore_point"
        else:
            return "unknown"
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics"""
        backups = self.list_backups()
        
        stats = {
            "total_backups": len(backups),
            "total_size": sum(b["size"] for b in backups),
            "last_backup": self.config.get("last_backup"),
            "backup_types": {},
            "oldest_backup": None,
            "newest_backup": None
        }
        
        if backups:
            stats["oldest_backup"] = min(b["created"] for b in backups).isoformat()
            stats["newest_backup"] = max(b["created"] for b in backups).isoformat()
        
        # Count by type
        for backup in backups:
            backup_type = backup["type"]
            if backup_type not in stats["backup_types"]:
                stats["backup_types"][backup_type] = 0
            stats["backup_types"][backup_type] += 1
        
        return stats
    
    def schedule_backup(self, frequency: str = "daily") -> bool:
        """Schedule automated backup"""
        try:
            schedule_config = self.config.get("schedule", {})
            
            if frequency not in schedule_config:
                return False
            
            schedule_config[frequency]["enabled"] = True
            self.config["schedule"] = schedule_config
            self._save_backup_config(self.config)
            
            # In a real implementation, this would set up a system scheduler
            # For now, we just mark it as enabled in the config
            print(f"Backup scheduled: {frequency}")
            
            return True
            
        except Exception as e:
            print(f"Backup scheduling failed: {e}")
            return False
    
    def test_backup_integrity(self, backup_path: Path) -> Dict[str, Any]:
        """Test backup file integrity"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "file_info": {}
        }
        
        try:
            # Basic file checks
            if not backup_path.exists():
                result["is_valid"] = False
                result["errors"].append("Backup file does not exist")
                return result
            
            # File info
            stat = backup_path.stat()
            result["file_info"] = {
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
            # Format-specific checks
            if backup_path.suffix == '.zip':
                result.update(self._test_zip_integrity(backup_path))
            elif backup_path.suffix == '.db':
                result.update(self._test_sqlite_integrity(backup_path))
            elif backup_path.suffix == '.bak':
                result.update(self._test_directory_integrity(backup_path))
            
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"Integrity test failed: {e}")
        
        return result
    
    def _test_zip_integrity(self, backup_path: Path) -> Dict[str, Any]:
        """Test ZIP file integrity"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Test ZIP file
                bad_file = zipf.testzip()
                if bad_file:
                    result["is_valid"] = False
                    result["errors"].append(f"Corrupted file in ZIP: {bad_file}")
                
                # Check for required files
                required_files = ["rigel_business.db"]
                for required_file in required_files:
                    if required_file not in zipf.namelist():
                        result["warnings"].append(f"Missing required file: {required_file}")
                
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"ZIP test failed: {e}")
        
        return result
    
    def _test_sqlite_integrity(self, backup_path: Path) -> Dict[str, Any]:
        """Test SQLite database integrity"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        try:
            with sqlite3.connect(backup_path) as conn:
                integrity_result = conn.execute("PRAGMA integrity_check").fetchone()
                if integrity_result[0] != 'ok':
                    result["is_valid"] = False
                    result["errors"].append(f"Database integrity check failed: {integrity_result[0]}")
                
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"SQLite test failed: {e}")
        
        return result
    
    def _test_directory_integrity(self, backup_path: Path) -> Dict[str, Any]:
        """Test directory backup integrity"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        try:
            # Check for required files
            required_files = ["rigel_business.db"]
            for required_file in required_files:
                file_path = backup_path / required_file
                if not file_path.exists():
                    result["warnings"].append(f"Missing required file: {required_file}")
                elif file_path.suffix == '.db':
                    # Test SQLite database
                    sqlite_result = self._test_sqlite_integrity(file_path)
                    result["errors"].extend(sqlite_result["errors"])
                    result["warnings"].extend(sqlite_result["warnings"])
                    if not sqlite_result["is_valid"]:
                        result["is_valid"] = False
        
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"Directory test failed: {e}")
        
        return result
