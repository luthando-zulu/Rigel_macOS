#!/usr/bin/env python3
"""
Database Manager for Rigel Business
Cross-platform database creation and management for Windows and macOS
"""

import os
import json
import sqlite3
import shutil
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
import platform
import tempfile

class DatabaseManager:
    """
    Cross-platform database manager for Rigel Business
    Supports both SQLite (primary) and JSON (fallback) storage
    """
    
    def __init__(self, data_dir: Optional[Path] = None, use_sqlite: bool = True):
        self.system = platform.system()
        self.use_sqlite = use_sqlite
        
        # Set up data directory based on platform
        if data_dir:
            self.data_dir = data_dir
        else:
            if self.system == "Windows":
                self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
            elif self.system == "Darwin":  # macOS
                self.data_dir = Path.home() / "Library" / "Application Support" / "RIGELBusiness"
            else:  # Linux and others
                self.data_dir = Path.home() / ".rigelbusiness"
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Database file paths
        self.sqlite_db = self.data_dir / "rigel_business.db"
        self.json_dir = self.data_dir / "json_data"
        self.json_dir.mkdir(exist_ok=True)
        
        # Backup directory
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Initialize database
        if self.use_sqlite:
            self._init_sqlite_database()
        else:
            self._init_json_files()
    
    def _init_sqlite_database(self):
        """Initialize SQLite database with all required tables"""
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                
                # Create all tables
                self._create_entity_tables(conn)
                self._create_accounting_tables(conn)
                self._create_business_tables(conn)
                self._create_system_tables(conn)
                
                conn.commit()
                
        except Exception as e:
            print(f"SQLite initialization failed: {e}")
            # Fallback to JSON
            self.use_sqlite = False
            self._init_json_files()
    
    def _create_entity_tables(self, conn):
        """Create entity-related tables"""
        # Entity registration
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                registration_number TEXT,
                tax_number TEXT,
                vat_number TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                website TEXT,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        # Chart of accounts
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chart_of_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_code TEXT NOT NULL UNIQUE,
                account_name TEXT NOT NULL,
                account_type TEXT NOT NULL,
                account_category TEXT,
                parent_code TEXT,
                balance_type TEXT DEFAULT 'debit',
                is_active INTEGER DEFAULT 1,
                created_date TEXT NOT NULL
            )
        """)
        
        # Directors
        conn.execute("""
            CREATE TABLE IF NOT EXISTS directors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER,
                director_code TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                id_number TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                appointment_date TEXT,
                resignation_date TEXT,
                is_active INTEGER DEFAULT 1,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL,
                FOREIGN KEY (entity_id) REFERENCES entities (id)
            )
        """)
        
        # Employees
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_code TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                id_number TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                position TEXT,
                department TEXT,
                salary REAL,
                hire_date TEXT,
                termination_date TEXT,
                is_active INTEGER DEFAULT 1,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL
            )
        """)
    
    def _create_accounting_tables(self, conn):
        """Create accounting-related tables"""
        # Journal entries
        conn.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                journal_code TEXT NOT NULL UNIQUE,
                entry_date TEXT NOT NULL,
                reference TEXT,
                description TEXT NOT NULL,
                total_debit REAL NOT NULL,
                total_credit REAL NOT NULL,
                status TEXT DEFAULT 'posted',
                created_date TEXT NOT NULL,
                created_by TEXT
            )
        """)
        
        # Journal entry lines
        conn.execute("""
            CREATE TABLE IF NOT EXISTS journal_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                journal_id INTEGER NOT NULL,
                account_code TEXT NOT NULL,
                debit REAL DEFAULT 0,
                credit REAL DEFAULT 0,
                notes TEXT,
                line_number INTEGER,
                FOREIGN KEY (journal_id) REFERENCES journal_entries (id)
            )
        """)
        
        # Trial balance
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trial_balance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_code TEXT NOT NULL,
                account_name TEXT NOT NULL,
                opening_balance REAL DEFAULT 0,
                debit_total REAL DEFAULT 0,
                credit_total REAL DEFAULT 0,
                closing_balance REAL DEFAULT 0,
                balance_type TEXT,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                generated_date TEXT NOT NULL
            )
        """)
        
        # Cash & Cash Equivalents tracking
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cce_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT NOT NULL,
                account_code TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                reference TEXT,
                description TEXT,
                cumulative_balance REAL NOT NULL,
                created_date TEXT NOT NULL
            )
        """)
    
    def _create_business_tables(self, conn):
        """Create business operation tables"""
        # Customers
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT NOT NULL UNIQUE,
                customer_name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                vat_number TEXT,
                credit_limit REAL DEFAULT 0,
                balance REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL
            )
        """)
        
        # Suppliers
        conn.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_code TEXT NOT NULL UNIQUE,
                supplier_name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                vat_number TEXT,
                payment_terms TEXT,
                balance REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL
            )
        """)
        
        # Inventory items
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT NOT NULL UNIQUE,
                item_name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                unit TEXT,
                cost_price REAL DEFAULT 0,
                selling_price REAL DEFAULT 0,
                current_stock REAL DEFAULT 0,
                minimum_stock REAL DEFAULT 0,
                maximum_stock REAL DEFAULT 0,
                reorder_level REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL
            )
        """)
        
        # Inventory transactions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit_price REAL DEFAULT 0,
                total_amount REAL DEFAULT 0,
                reference TEXT,
                transaction_date TEXT NOT NULL,
                notes TEXT,
                created_date TEXT NOT NULL
            )
        """)
        
        # Fixed assets
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fixed_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_code TEXT NOT NULL UNIQUE,
                asset_name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                location TEXT,
                purchase_date TEXT NOT NULL,
                purchase_cost REAL NOT NULL,
                depreciation_method TEXT,
                useful_life_years INTEGER,
                depreciation_rate REAL,
                accumulated_depreciation REAL DEFAULT 0,
                net_book_value REAL,
                disposal_date TEXT,
                disposal_value REAL DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL
            )
        """)
        
        # Projects
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_code TEXT NOT NULL UNIQUE,
                project_name TEXT NOT NULL,
                client TEXT,
                project_type TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                contract_value REAL NOT NULL,
                budget_allocated REAL NOT NULL,
                actual_cost REAL DEFAULT 0,
                project_manager TEXT,
                status TEXT,
                description TEXT,
                created_date TEXT NOT NULL,
                modified_date TEXT NOT NULL
            )
        """)
        
        # Project transactions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS project_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_code TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_date TEXT NOT NULL,
                description TEXT,
                reference TEXT,
                created_date TEXT NOT NULL
            )
        """)
        
        # Adjustments
        conn.execute("""
            CREATE TABLE IF NOT EXISTS adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adjustment_number TEXT NOT NULL UNIQUE,
                adjustment_date TEXT NOT NULL,
                adjustment_type TEXT NOT NULL,
                description TEXT NOT NULL,
                reference TEXT,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'draft',
                created_date TEXT NOT NULL,
                posted_date TEXT
            )
        """)
        
        # Adjustment lines
        conn.execute("""
            CREATE TABLE IF NOT EXISTS adjustment_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adjustment_id INTEGER NOT NULL,
                account_code TEXT NOT NULL,
                debit REAL DEFAULT 0,
                credit REAL DEFAULT 0,
                notes TEXT,
                line_number INTEGER,
                FOREIGN KEY (adjustment_id) REFERENCES adjustments (id)
            )
        """)
    
    def _create_system_tables(self, conn):
        """Create system management tables"""
        # System settings
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT NOT NULL UNIQUE,
                setting_value TEXT,
                setting_type TEXT,
                description TEXT,
                modified_date TEXT NOT NULL
            )
        """)
        
        # User sessions
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                user_id TEXT,
                login_time TEXT NOT NULL,
                logout_time TEXT,
                activity TEXT,
                ip_address TEXT
            )
        """)
        
        # Audit log
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id TEXT,
                old_values TEXT,
                new_values TEXT,
                description TEXT
            )
        """)
        
        # Database version
        conn.execute("""
            CREATE TABLE IF NOT EXISTS database_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_number TEXT NOT NULL,
                version_date TEXT NOT NULL,
                description TEXT,
                is_current INTEGER DEFAULT 0
            )
        """)
    
    def _init_json_files(self):
        """Initialize JSON files as fallback storage"""
        json_files = [
            'entities.json',
            'chart_of_accounts.json',
            'journal_entries.json',
            'customers.json',
            'suppliers.json',
            'directors.json',
            'employees.json',
            'inventory.json',
            'fixed_assets.json',
            'projects.json',
            'adjustments.json',
            'system_settings.json'
        ]
        
        for file_name in json_files:
            file_path = self.json_dir / file_name
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def backup_database(self, backup_name: Optional[str] = None) -> Path:
        """Create backup of database"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / backup_name
        
        if self.use_sqlite:
            # SQLite backup
            backup_path = backup_path.with_suffix('.db')
            shutil.copy2(self.sqlite_db, backup_path)
        else:
            # JSON backup
            backup_path = backup_path.with_suffix('.zip')
            shutil.make_archive(str(backup_path.with_suffix('')), 'zip', str(self.json_dir))
        
        return backup_path
    
    def restore_database(self, backup_path: Path) -> bool:
        """Restore database from backup"""
        try:
            if backup_path.suffix == '.db':
                # Restore SQLite
                shutil.copy2(backup_path, self.sqlite_db)
            elif backup_path.suffix == '.zip':
                # Restore JSON
                shutil.unpack_archive(str(backup_path), str(self.json_dir))
            else:
                return False
            
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        info = {
            'platform': self.system,
            'data_directory': str(self.data_dir),
            'storage_type': 'SQLite' if self.use_sqlite else 'JSON',
            'database_size': 0,
            'last_backup': None,
            'version': '1.0.0'
        }
        
        if self.use_sqlite and self.sqlite_db.exists():
            info['database_size'] = self.sqlite_db.stat().st_size
        
        # Get last backup
        backups = list(self.backup_dir.glob('*'))
        if backups:
            latest_backup = max(backups, key=lambda x: x.stat().st_mtime)
            info['last_backup'] = datetime.fromtimestamp(latest_backup.stat().st_mtime).isoformat()
        
        return info
    
    def migrate_from_json_to_sqlite(self) -> bool:
        """Migrate data from JSON files to SQLite"""
        if not self.use_sqlite:
            return False
        
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
                # Migrate each JSON file to corresponding table
                migrations = [
                    ('entities.json', 'entities'),
                    ('chart_of_accounts.json', 'chart_of_accounts'),
                    ('customers.json', 'customers'),
                    ('suppliers.json', 'suppliers'),
                    ('directors.json', 'directors'),
                    ('employees.json', 'employees'),
                    ('inventory.json', 'inventory_items'),
                    ('fixed_assets.json', 'fixed_assets'),
                    ('projects.json', 'projects'),
                    ('adjustments.json', 'adjustments')
                ]
                
                for json_file, table_name in migrations:
                    json_path = self.json_dir / json_file
                    if json_path.exists():
                        with open(json_path, 'r') as f:
                            data = json.load(f)
                        
                        if data:
                            # Convert JSON data to table format and insert
                            self._insert_json_data(conn, data, table_name)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Migration failed: {e}")
            return False
    
    def _insert_json_data(self, conn, data: List[Dict], table_name: str):
        """Insert JSON data into SQLite table"""
        if not data:
            return
        
        # Get column names from first record
        columns = list(data[0].keys())
        
        # Create INSERT statement
        placeholders = ', '.join(['?' for _ in columns])
        columns_str = ', '.join(columns)
        insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # Insert all records
        for record in data:
            values = [record.get(col) for col in columns]
            conn.execute(insert_sql, values)
    
    def optimize_database(self) -> bool:
        """Optimize database performance"""
        if not self.use_sqlite:
            return False
        
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
                conn.execute("VACUUM")
                conn.execute("ANALYZE")
                conn.commit()
                return True
        except Exception as e:
            print(f"Optimization failed: {e}")
            return False
    
    def validate_database_integrity(self) -> Dict[str, Any]:
        """Validate database integrity"""
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'table_counts': {}
        }
        
        if self.use_sqlite:
            try:
                with sqlite3.connect(self.sqlite_db) as conn:
                    # Check integrity
                    integrity_result = conn.execute("PRAGMA integrity_check").fetchone()
                    if integrity_result[0] != 'ok':
                        result['is_valid'] = False
                        result['errors'].append(f"Integrity check failed: {integrity_result[0]}")
                    
                    # Check foreign key constraints
                    fk_check = conn.execute("PRAGMA foreign_key_check").fetchall()
                    if fk_check:
                        result['is_valid'] = False
                        result['errors'].extend([f"Foreign key violation: {row}" for row in fk_check])
                    
                    # Get table counts
                    tables = conn.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """).fetchall()
                    
                    for table in tables:
                        count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
                        result['table_counts'][table[0]] = count
                        
            except Exception as e:
                result['is_valid'] = False
                result['errors'].append(f"Database validation error: {e}")
        
        return result
    
    def export_data(self, export_path: Path, format_type: str = 'json') -> bool:
        """Export data from database"""
        try:
            if format_type == 'json':
                return self._export_json(export_path)
            elif format_type == 'csv':
                return self._export_csv(export_path)
            elif format_type == 'sql':
                return self._export_sql(export_path)
            else:
                return False
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def _export_json(self, export_path: Path) -> bool:
        """Export data to JSON format"""
        if not self.use_sqlite:
            # Copy JSON files
            shutil.copytree(self.json_dir, export_path)
            return True
        
        try:
            with sqlite3.connect(self.sqlite_db) as conn:
                tables = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """).fetchall()
                
                export_data = {}
                for table in tables:
                    table_name = table[0]
                    rows = conn.execute(f"SELECT * FROM {table_name}").fetchall()
                    columns = [desc[0] for desc in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]
                    
                    export_data[table_name] = []
                    for row in rows:
                        export_data[table_name].append(dict(zip(columns, row)))
                
                with open(export_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                return True
                
        except Exception as e:
            print(f"JSON export failed: {e}")
            return False
    
    def _export_csv(self, export_path: Path) -> bool:
        """Export data to CSV format"""
        import csv
        
        if not self.use_sqlite:
            return False
        
        try:
            export_path.mkdir(exist_ok=True)
            
            with sqlite3.connect(self.sqlite_db) as conn:
                tables = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """).fetchall()
                
                for table in tables:
                    table_name = table[0]
                    csv_path = export_path / f"{table_name}.csv"
                    
                    with open(csv_path, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        
                        # Write headers
                        columns = [desc[0] for desc in conn.execute(f"PRAGMA table_info({table_name})").fetchall()]
                        writer.writerow(columns)
                        
                        # Write data
                        rows = conn.execute(f"SELECT * FROM {table_name}").fetchall()
                        writer.writerows(rows)
                
                return True
                
        except Exception as e:
            print(f"CSV export failed: {e}")
            return False
    
    def _export_sql(self, export_path: Path) -> bool:
        """Export data to SQL format"""
        if not self.use_sqlite:
            return False
        
        try:
            with open(export_path, 'w') as f:
                with sqlite3.connect(self.sqlite_db) as conn:
                    for line in conn.iterdump():
                        f.write(f"{line}\n")
            
            return True
            
        except Exception as e:
            print(f"SQL export failed: {e}")
            return False
    
    def close(self):
        """Close database connections"""
        # SQLite connections are automatically closed with context managers
        pass
