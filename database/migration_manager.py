#!/usr/bin/env python3
"""
Data Migration Manager
Handles data persistence, version upgrades, and schema migrations
"""

import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib

class MigrationManager:
    """Data migration and upgrade manager"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.migrations_dir = data_dir / "migrations"
        self.migrations_dir.mkdir(exist_ok=True)
        
        self.sqlite_db = data_dir / "rigel_business.db"
        self.json_dir = data_dir / "json_data"
        self.json_dir.mkdir(exist_ok=True)
        
        self.version_file = data_dir / "data_version.json"
        self.current_version = "1.0.0"
        
        self.version_info = self._load_version_info()
    
    def _load_version_info(self) -> Dict[str, Any]:
        """Load data version information"""
        default_version_info = {
            "current_version": self.current_version,
            "schema_version": "1.0.0",
            "data_version": "1.0.0",
            "last_migration": None,
            "migration_history": [],
            "checksums": {}
        }
        
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    version_info = json.load(f)
                return {**default_version_info, **version_info}
            except Exception as e:
                print(f"Error loading version info: {e}")
                return default_version_info
        else:
            self._save_version_info(default_version_info)
            return default_version_info
    
    def _save_version_info(self, version_info: Dict[str, Any]):
        """Save data version information"""
        try:
            with open(self.version_file, 'w') as f:
                json.dump(version_info, f, indent=2)
        except Exception as e:
            print(f"Error saving version info: {e}")
    
    def create_migration(self, from_version: str, to_version: str, description: str, 
                        migration_type: str = "schema") -> Path:
        """Create a new migration"""
        migration_id = f"{from_version}_to_{to_version}"
        migration_data = {
            "migration_id": migration_id,
            "from_version": from_version,
            "to_version": to_version,
            "description": description,
            "type": migration_type,  # schema, data, or both
            "created_date": datetime.now().isoformat(),
            "applied_date": None,
            "rollback_script": None,
            "dependencies": [],
            "pre_checks": [],
            "post_checks": []
        }
        
        migration_file = self.migrations_dir / f"migration_{migration_id}.json"
        with open(migration_file, 'w') as f:
            json.dump(migration_data, f, indent=2)
        
        return migration_file
    
    def apply_migration(self, migration_id: str) -> bool:
        """Apply a specific migration"""
        migration_file = self.migrations_dir / f"migration_{migration_id}.json"
        
        if not migration_file.exists():
            print(f"Migration not found: {migration_id}")
            return False
        
        try:
            with open(migration_file, 'r') as f:
                migration = json.load(f)
            
            # Check dependencies
            if not self._check_dependencies(migration.get("dependencies", [])):
                print(f"Dependencies not satisfied for migration: {migration_id}")
                return False
            
            # Run pre-checks
            if not self._run_checks(migration.get("pre_checks", [])):
                print(f"Pre-checks failed for migration: {migration_id}")
                return False
            
            # Apply migration based on type
            success = False
            if migration["type"] == "schema":
                success = self._apply_schema_migration(migration)
            elif migration["type"] == "data":
                success = self._apply_data_migration(migration)
            elif migration["type"] == "both":
                success = self._apply_schema_migration(migration) and self._apply_data_migration(migration)
            
            if success:
                # Update migration info
                migration["applied_date"] = datetime.now().isoformat()
                with open(migration_file, 'w') as f:
                    json.dump(migration, f, indent=2)
                
                # Update version info
                self.version_info["current_version"] = migration["to_version"]
                self.version_info["last_migration"] = migration_id
                self.version_info["migration_history"].append({
                    "migration_id": migration_id,
                    "applied_date": migration["applied_date"],
                    "description": migration["description"]
                })
                self._save_version_info(self.version_info)
                
                # Run post-checks
                self._run_checks(migration.get("post_checks", []))
                
                print(f"Migration applied successfully: {migration_id}")
                return True
            else:
                print(f"Migration failed: {migration_id}")
                return False
                
        except Exception as e:
            print(f"Migration error: {e}")
            return False
    
    def _apply_schema_migration(self, migration: Dict[str, Any]) -> bool:
        """Apply schema migration"""
        try:
            if not self.sqlite_db.exists():
                return False
            
            with sqlite3.connect(self.sqlite_db) as conn:
                # Enable foreign key support
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Apply schema changes
                sql_file = self.migrations_dir / f"migration_{migration['migration_id']}.sql"
                if sql_file.exists():
                    with open(sql_file, 'r') as f:
                        sql_content = f.read()
                    
                    # Execute SQL statements
                    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                    for statement in statements:
                        if statement:
                            conn.execute(statement)
                    
                    conn.commit()
                    return True
                else:
                    print(f"No SQL file found for migration: {migration['migration_id']}")
                    return False
                    
        except Exception as e:
            print(f"Schema migration failed: {e}")
            return False
    
    def _apply_data_migration(self, migration: Dict[str, Any]) -> bool:
        """Apply data migration"""
        try:
            python_file = self.migrations_dir / f"migration_{migration['migration_id']}.py"
            if python_file.exists():
                # Execute Python migration script
                # In a real implementation, this would import and execute the migration
                print(f"Python migration script found: {python_file}")
                return True
            else:
                # Apply built-in data migrations
                return self._apply_builtin_data_migration(migration)
                
        except Exception as e:
            print(f"Data migration failed: {e}")
            return False
    
    def _apply_builtin_data_migration(self, migration: Dict[str, Any]) -> bool:
        """Apply built-in data migration logic"""
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
                if migration["migration_id"] == "0.9.0_to_1.0.0":
                    # Example migration: Add new columns to existing tables
                    migrations = [
                        "ALTER TABLE customers ADD COLUMN tax_number TEXT",
                        "ALTER TABLE suppliers ADD COLUMN payment_terms TEXT",
                        "ALTER TABLE employees ADD COLUMN department TEXT"
                    ]
                    
                    for sql in migrations:
                        try:
                            conn.execute(sql)
                        except sqlite3.OperationalError as e:
                            if "duplicate column name" not in str(e):
                                raise
                    
                    conn.commit()
                    return True
                
                elif migration["migration_id"] == "1.0.0_to_1.1.0":
                    # Example migration: Migrate JSON data to SQLite
                    return self._migrate_json_to_sqlite(conn)
                
                else:
                    print(f"No built-in migration for: {migration['migration_id']}")
                    return False
                    
        except Exception as e:
            print(f"Built-in data migration failed: {e}")
            return False
    
    def _migrate_json_to_sqlite(self, conn) -> bool:
        """Migrate data from JSON files to SQLite"""
        try:
            json_files = {
                'customers.json': 'customers',
                'suppliers.json': 'suppliers',
                'employees.json': 'employees',
                'directors.json': 'directors',
                'inventory.json': 'inventory_items',
                'fixed_assets.json': 'fixed_assets',
                'projects.json': 'projects',
                'adjustments.json': 'adjustments'
            }
            
            for json_file, table_name in json_files.items():
                json_path = self.json_dir / json_file
                if json_path.exists():
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                    
                    if data:
                        # Get table schema
                        schema = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                        columns = [col[1] for col in schema]
                        
                        # Insert data
                        for record in data:
                            values = []
                            for col in columns:
                                value = record.get(col)
                                if isinstance(value, (list, dict)):
                                    value = json.dumps(value)
                                values.append(value)
                            
                            placeholders = ', '.join(['?' for _ in columns])
                            sql = f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                            conn.execute(sql, values)
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"JSON to SQLite migration failed: {e}")
            return False
    
    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if migration dependencies are satisfied"""
        applied_migrations = [m["migration_id"] for m in self.version_info["migration_history"]]
        
        for dependency in dependencies:
            if dependency not in applied_migrations:
                return False
        
        return True
    
    def _run_checks(self, checks: List[Dict[str, Any]]) -> bool:
        """Run migration checks"""
        for check in checks:
            check_type = check.get("type")
            
            if check_type == "table_exists":
                if not self._check_table_exists(check.get("table")):
                    return False
            
            elif check_type == "column_exists":
                if not self._check_column_exists(check.get("table"), check.get("column")):
                    return False
            
            elif check_type == "data_count":
                if not self._check_data_count(check.get("table"), check.get("expected_count", 0)):
                    return False
        
        return True
    
    def _check_table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
                result = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,)).fetchone()
                return result is not None
        except:
            return False
    
    def _check_column_exists(self, table_name: str, column_name: str) -> bool:
        """Check if column exists in table"""
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
                result = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                return any(col[1] == column_name for col in result)
        except:
            return False
    
    def _check_data_count(self, table_name: str, expected_count: int) -> bool:
        """Check if table has expected number of records"""
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                return count >= expected_count
        except:
            return False
    
    def rollback_migration(self, migration_id: str) -> bool:
        """Rollback a migration"""
        migration_file = self.migrations_dir / f"migration_{migration_id}.json"
        
        if not migration_file.exists():
            print(f"Migration not found: {migration_id}")
            return False
        
        try:
            with open(migration_file, 'r') as f:
                migration = json.load(f)
            
            rollback_script = migration.get("rollback_script")
            if not rollback_script:
                print(f"No rollback script for migration: {migration_id}")
                return False
            
            # Execute rollback
            if rollback_script.endswith('.sql'):
                return self._execute_sql_rollback(rollback_script)
            elif rollback_script.endswith('.py'):
                return self._execute_python_rollback(rollback_script)
            else:
                print(f"Unsupported rollback script type: {rollback_script}")
                return False
                
        except Exception as e:
            print(f"Rollback failed: {e}")
            return False
    
    def _execute_sql_rollback(self, rollback_script: str) -> bool:
        """Execute SQL rollback script"""
        try:
            rollback_file = self.migrations_dir / rollback_script
            if not rollback_file.exists():
                return False
            
            with sqlite3.connect(self.sqlite_db) as conn:
                with open(rollback_file, 'r') as f:
                    sql_content = f.read()
                
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                for statement in statements:
                    if statement:
                        conn.execute(statement)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"SQL rollback failed: {e}")
            return False
    
    def _execute_python_rollback(self, rollback_script: str) -> bool:
        """Execute Python rollback script"""
        # In a real implementation, this would import and execute the rollback script
        print(f"Python rollback script: {rollback_script}")
        return True
    
    def get_pending_migrations(self) -> List[Dict[str, Any]]:
        """Get list of pending migrations"""
        applied_migrations = [m["migration_id"] for m in self.version_info["migration_history"]]
        pending_migrations = []
        
        for migration_file in self.migrations_dir.glob("migration_*.json"):
            with open(migration_file, 'r') as f:
                migration = json.load(f)
            
            if migration["migration_id"] not in applied_migrations:
                pending_migrations.append(migration)
        
        # Sort by version
        pending_migrations.sort(key=lambda x: x["from_version"])
        
        return pending_migrations
    
    def apply_all_pending_migrations(self) -> bool:
        """Apply all pending migrations"""
        pending_migrations = self.get_pending_migrations()
        
        for migration in pending_migrations:
            if not self.apply_migration(migration["migration_id"]):
                print(f"Failed to apply migration: {migration['migration_id']}")
                return False
        
        return True
    
    def verify_data_integrity(self) -> Dict[str, Any]:
        """Verify data integrity after migration"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "checksums": {},
            "table_info": {}
        }
        
        try:
            if self.sqlite_db.exists():
                with sqlite3.connect(self.sqlite_db) as conn:
                    # Check database integrity
                    integrity_result = conn.execute("PRAGMA integrity_check").fetchone()
                    if integrity_result[0] != 'ok':
                        result["is_valid"] = False
                        result["errors"].append(f"Database integrity check failed: {integrity_result[0]}")
                    
                    # Get table information
                    tables = conn.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """).fetchall()
                    
                    for table in tables:
                        table_name = table[0]
                        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                        
                        result["table_info"][table_name] = {
                            "record_count": count,
                            "checksum": self._calculate_table_checksum(conn, table_name)
                        }
            
            # Compare with stored checksums
            stored_checksums = self.version_info.get("checksums", {})
            for table, info in result["table_info"].items():
                if table in stored_checksums:
                    if stored_checksums[table] != info["checksum"]:
                        result["warnings"].append(f"Checksum mismatch for table: {table}")
            
            # Update stored checksums
            self.version_info["checksums"] = result["checksums"]
            self._save_version_info(self.version_info)
            
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"Integrity verification failed: {e}")
        
        return result
    
    def _calculate_table_checksum(self, conn, table_name: str) -> str:
        """Calculate checksum for table data"""
        try:
            # Get all data from table
            rows = conn.execute(f"SELECT * FROM {table_name}").fetchall()
            
            # Create string representation
            data_str = json.dumps(rows, sort_keys=True, default=str)
            
            # Calculate MD5 checksum
            return hashlib.md5(data_str.encode()).hexdigest()
            
        except Exception as e:
            print(f"Checksum calculation failed for {table_name}: {e}")
            return ""
    
    def export_migration_history(self, export_path: Path) -> bool:
        """Export migration history"""
        try:
            export_data = {
                "version_info": self.version_info,
                "applied_migrations": [],
                "pending_migrations": []
            }
            
            # Get applied migrations
            for migration_id in [m["migration_id"] for m in self.version_info["migration_history"]]:
                migration_file = self.migrations_dir / f"migration_{migration_id}.json"
                if migration_file.exists():
                    with open(migration_file, 'r') as f:
                        migration = json.load(f)
                    export_data["applied_migrations"].append(migration)
            
            # Get pending migrations
            export_data["pending_migrations"] = self.get_pending_migrations()
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Export migration history failed: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status"""
        pending_migrations = self.get_pending_migrations()
        
        return {
            "current_version": self.version_info["current_version"],
            "schema_version": self.version_info["schema_version"],
            "data_version": self.version_info["data_version"],
            "last_migration": self.version_info["last_migration"],
            "total_migrations": len(list(self.migrations_dir.glob("migration_*.json"))),
            "applied_migrations": len(self.version_info["migration_history"]),
            "pending_migrations": len(pending_migrations),
            "migration_history": self.version_info["migration_history"]
        }
