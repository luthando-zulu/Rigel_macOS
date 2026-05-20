#!/usr/bin/env python3
"""
Database Initialization Script
Comprehensive database setup for Rigel Business on Windows and macOS
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import platform

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database_manager import DatabaseManager
from database.database_config import DatabaseConfig
from database.backup_manager import BackupManager
from database.migration_manager import MigrationManager

class DatabaseInitializer:
    """Comprehensive database initialization and management"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.system = platform.system()
        
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
        
        # Initialize database components
        self.db_manager = DatabaseManager(self.data_dir)
        self.db_config = DatabaseConfig(self.data_dir)
        self.backup_manager = BackupManager(self.data_dir)
        self.migration_manager = MigrationManager(self.data_dir)
        
        print(f"Database initialized for {self.system}")
        print(f"Data directory: {self.data_dir}")
    
    def create_new_database(self, use_sqlite: bool = True) -> bool:
        """Create a new database with all required tables and initial data"""
        try:
            print("Creating new database...")
            
            # Initialize database structure
            if use_sqlite:
                if not self._create_sqlite_database():
                    return False
                
                # Load initial data
                if not self._load_initial_data():
                    return False
                
                # Optimize for platform
                self.db_config.optimize_for_platform(self.data_dir / "rigel_business.db")
            else:
                if not self._create_json_database():
                    return False
            
            # Setup backup configuration
            self.db_config.setup_auto_backup(self.backup_manager)
            
            # Create initial backup
            initial_backup = self.backup_manager.create_backup("full", "Initial database setup")
            print(f"Initial backup created: {initial_backup}")
            
            print("Database created successfully!")
            return True
            
        except Exception as e:
            print(f"Database creation failed: {e}")
            return False
    
    def _create_sqlite_database(self) -> bool:
        """Create SQLite database with all tables"""
        try:
            sqlite_db = self.data_dir / "rigel_business.db"
            
            with sqlite3.connect(sqlite_db) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                
                # Create all tables
                self._create_entity_tables(conn)
                self._create_accounting_tables(conn)
                self._create_business_tables(conn)
                self._create_system_tables(conn)
                
                # Create indexes for performance
                self._create_indexes(conn)
                
                conn.commit()
            
            return True
            
        except Exception as e:
            print(f"SQLite database creation failed: {e}")
            return False
    
    def _create_json_database(self) -> bool:
        """Create JSON database files"""
        try:
            json_dir = self.data_dir / "json_data"
            json_dir.mkdir(exist_ok=True)
            
            # Create initial JSON files
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
                file_path = json_dir / file_name
                if not file_path.exists():
                    with open(file_path, 'w') as f:
                        json.dump([], f)
            
            return True
            
        except Exception as e:
            print(f"JSON database creation failed: {e}")
            return False
    
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
    
    def _create_indexes(self, conn):
        """Create database indexes for performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_journal_entries_date ON journal_entries(entry_date)",
            "CREATE INDEX IF NOT EXISTS idx_journal_lines_journal ON journal_lines(journal_id)",
            "CREATE INDEX IF NOT EXISTS idx_journal_lines_account ON journal_lines(account_code)",
            "CREATE INDEX IF NOT EXISTS idx_customers_code ON customers(customer_code)",
            "CREATE INDEX IF NOT EXISTS idx_suppliers_code ON suppliers(supplier_code)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_items_code ON inventory_items(item_code)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_transactions_item ON inventory_transactions(item_code)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_transactions_date ON inventory_transactions(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_fixed_assets_code ON fixed_assets(asset_code)",
            "CREATE INDEX IF NOT EXISTS idx_projects_code ON projects(project_code)",
            "CREATE INDEX IF NOT EXISTS idx_project_transactions_project ON project_transactions(project_code)",
            "CREATE INDEX IF NOT EXISTS idx_adjustments_number ON adjustments(adjustment_number)",
            "CREATE INDEX IF NOT EXISTS idx_adjustment_lines_adjustment ON adjustment_lines(adjustment_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_audit_log_table ON audit_log(table_name)",
            "CREATE INDEX IF NOT EXISTS idx_cce_tracking_date ON cce_tracking(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_cce_tracking_account ON cce_tracking(account_code)"
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(index_sql)
            except Exception as e:
                print(f"Index creation warning: {e}")
    
    def _load_initial_data(self) -> bool:
        """Load initial data into database"""
        try:
            sqlite_db = self.data_dir / "rigel_business.db"
            
            with sqlite3.connect(sqlite_db) as conn:
                # Load chart of accounts
                self._load_chart_of_accounts(conn)
                
                # Load system settings
                self._load_system_settings(conn)
                
                # Set database version
                self._set_database_version(conn)
                
                conn.commit()
            
            return True
            
        except Exception as e:
            print(f"Initial data loading failed: {e}")
            return False
    
    def _load_chart_of_accounts(self, conn):
        """Load standard chart of accounts"""
        from accounting import CHART_OF_ACCOUNTS
        
        for account in CHART_OF_ACCOUNTS:
            conn.execute("""
                INSERT OR REPLACE INTO chart_of_accounts 
                (account_code, account_name, account_type, account_category, parent_code, balance_type, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                account['code'],
                account['name'],
                account['type'],
                account['category'],
                account.get('parent'),
                account.get('balance_type', 'debit'),
                datetime.now().isoformat()
            ))
    
    def _load_system_settings(self, conn):
        """Load default system settings"""
        settings = [
            ("company_name", "RIGEL Business", "string", "Company name"),
            ("vat_rate", "15", "decimal", "VAT percentage"),
            ("currency_code", "ZAR", "string", "Currency code"),
            ("currency_symbol", "R", "string", "Currency symbol"),
            ("fiscal_year_start", "2024-03-01", "date", "Fiscal year start date"),
            ("auto_backup", "true", "boolean", "Enable automatic backups"),
            ("backup_frequency", "daily", "string", "Backup frequency"),
            ("max_backups", "30", "integer", "Maximum backup files to keep"),
            ("theme", "default", "string", "UI theme"),
            ("language", "en", "string", "Application language")
        ]
        
        for key, value, setting_type, description in settings:
            conn.execute("""
                INSERT OR REPLACE INTO system_settings 
                (setting_key, setting_value, setting_type, description, modified_date)
                VALUES (?, ?, ?, ?, ?)
            """, (key, value, setting_type, description, datetime.now().isoformat()))
    
    def _set_database_version(self, conn):
        """Set database version"""
        conn.execute("""
            INSERT OR REPLACE INTO database_version 
            (version_number, version_date, description, is_current)
            VALUES (?, ?, ?, ?)
        """, ("1.0.0", datetime.now().isoformat(), "Initial database setup", 1))
    
    def upgrade_database(self, target_version: str = "1.0.0") -> bool:
        """Upgrade database to target version"""
        try:
            print(f"Upgrading database to version {target_version}...")
            
            # Apply pending migrations
            if not self.migration_manager.apply_all_pending_migrations():
                print("Migration failed")
                return False
            
            # Verify data integrity
            integrity_result = self.migration_manager.verify_data_integrity()
            if not integrity_result["is_valid"]:
                print("Data integrity issues found:")
                for error in integrity_result["errors"]:
                    print(f"  - {error}")
                return False
            
            # Create post-upgrade backup
            upgrade_backup = self.backup_manager.create_backup("full", f"Post-upgrade to {target_version}")
            print(f"Post-upgrade backup created: {upgrade_backup}")
            
            print("Database upgrade completed successfully!")
            return True
            
        except Exception as e:
            print(f"Database upgrade failed: {e}")
            return False
    
    def repair_database(self) -> bool:
        """Repair corrupted database"""
        try:
            print("Repairing database...")
            
            # Create backup before repair
            repair_backup = self.backup_manager.create_backup("full", "Before database repair")
            print(f"Pre-repair backup created: {repair_backup}")
            
            # Optimize database
            if not self.db_manager.optimize_database():
                print("Database optimization failed")
                return False
            
            # Verify integrity
            validation_result = self.db_manager.validate_database_integrity()
            if not validation_result["is_valid"]:
                print("Database integrity issues found:")
                for error in validation_result["errors"]:
                    print(f"  - {error}")
                return False
            
            print("Database repair completed successfully!")
            return True
            
        except Exception as e:
            print(f"Database repair failed: {e}")
            return False
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get comprehensive database status"""
        status = {
            "platform": self.system,
            "data_directory": str(self.data_dir),
            "database_info": self.db_manager.get_database_info(),
            "backup_statistics": self.backup_manager.get_backup_statistics(),
            "migration_status": self.migration_manager.get_migration_status(),
            "config_validation": self.db_config.validate_config()
        }
        
        return status
    
    def export_database(self, export_path: Path, format_type: str = "json") -> bool:
        """Export database in specified format"""
        try:
            return self.db_manager.export_data(export_path, format_type)
        except Exception as e:
            print(f"Database export failed: {e}")
            return False
    
    def import_database(self, import_path: Path, format_type: str = "json") -> bool:
        """Import database from specified format"""
        try:
            # Create backup before import
            import_backup = self.backup_manager.create_backup("full", "Before database import")
            print(f"Pre-import backup created: {import_backup}")
            
            # Perform import
            if format_type == "json":
                return self._import_json_database(import_path)
            elif format_type == "sql":
                return self._import_sql_database(import_path)
            else:
                print(f"Unsupported import format: {format_type}")
                return False
                
        except Exception as e:
            print(f"Database import failed: {e}")
            return False
    
    def _import_json_database(self, import_path: Path) -> bool:
        """Import database from JSON format"""
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            sqlite_db = self.data_dir / "rigel_business.db"
            
            with sqlite3.connect(sqlite_db) as conn:
                for table_name, records in import_data.items():
                    if records and isinstance(records, list):
                        # Get table schema
                        schema = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                        columns = [col[1] for col in schema]
                        
                        # Clear existing data
                        conn.execute(f"DELETE FROM {table_name}")
                        
                        # Insert new data
                        for record in records:
                            values = []
                            for col in columns:
                                value = record.get(col)
                                if isinstance(value, (list, dict)):
                                    value = json.dumps(value)
                                values.append(value)
                            
                            placeholders = ', '.join(['?' for _ in columns])
                            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                            conn.execute(sql, values)
                
                conn.commit()
            
            return True
            
        except Exception as e:
            print(f"JSON import failed: {e}")
            return False
    
    def _import_sql_database(self, import_path: Path) -> bool:
        """Import database from SQL format"""
        try:
            sqlite_db = self.data_dir / "rigel_business.db"
            
            with sqlite3.connect(sqlite_db) as conn:
                with open(import_path, 'r') as f:
                    sql_content = f.read()
                
                # Execute SQL statements
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                for statement in statements:
                    if statement:
                        conn.execute(statement)
                
                conn.commit()
            
            return True
            
        except Exception as e:
            print(f"SQL import failed: {e}")
            return False

def main():
    """Main function for database initialization"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rigel Business Database Manager")
    parser.add_argument("--action", choices=["create", "upgrade", "repair", "status", "export", "import"], 
                       required=True, help="Action to perform")
    parser.add_argument("--data-dir", type=Path, help="Data directory path")
    parser.add_argument("--format", choices=["json", "sql", "csv"], default="json", 
                       help="Export/import format")
    parser.add_argument("--file", type=Path, help="File path for export/import")
    parser.add_argument("--version", default="1.0.0", help="Target version for upgrade")
    parser.add_argument("--sqlite", action="store_true", default=True, help="Use SQLite database")
    
    args = parser.parse_args()
    
    # Initialize database
    initializer = DatabaseInitializer(args.data_dir)
    
    if args.action == "create":
        success = initializer.create_new_database(args.sqlite)
    elif args.action == "upgrade":
        success = initializer.upgrade_database(args.version)
    elif args.action == "repair":
        success = initializer.repair_database()
    elif args.action == "status":
        status = initializer.get_database_status()
        print(json.dumps(status, indent=2))
        success = True
    elif args.action == "export":
        if not args.file:
            print("Export file path required")
            success = False
        else:
            success = initializer.export_database(args.file, args.format)
    elif args.action == "import":
        if not args.file:
            print("Import file path required")
            success = False
        else:
            success = initializer.import_database(args.file, args.format)
    else:
        print(f"Unknown action: {args.action}")
        success = False
    
    if success:
        print("Operation completed successfully!")
        sys.exit(0)
    else:
        print("Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
