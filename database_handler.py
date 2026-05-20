#!/usr/bin/env python3
"""
RIGEL Business Database Handler
SQLite database management for all accounting operations
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid

class DatabaseHandler:
    """
    Comprehensive database handler for RIGEL Business
    Manages all accounting data persistence
    """
    
    def __init__(self, db_path: str = None):
        """Initialize database handler"""
        if db_path is None:
            # Default to app data directory
            app_data_dir = Path.home() / ".rigel_business"
            app_data_dir.mkdir(exist_ok=True)
            db_path = app_data_dir / "rigel_business.db"
        
        self.db_path = Path(db_path)
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_tables(self):
        """Create all necessary database tables"""
        cursor = self.connection.cursor()
        
        # Company Information
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                registration_number TEXT,
                tax_number TEXT,
                vat_number TEXT,
                address TEXT,
                city TEXT,
                province TEXT,
                postal_code TEXT,
                country TEXT DEFAULT 'South Africa',
                phone TEXT,
                email TEXT,
                website TEXT,
                financial_year_end TEXT,
                currency TEXT DEFAULT 'ZAR',
                date_format TEXT DEFAULT 'YYYY/MM/DD',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Chart of Accounts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chart_of_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_code TEXT UNIQUE NOT NULL,
                account_name TEXT NOT NULL,
                category TEXT NOT NULL,
                sub_category TEXT,
                account_type TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Customers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                province TEXT,
                postal_code TEXT,
                tax_number TEXT,
                account_code TEXT,
                opening_balance REAL DEFAULT 0,
                current_balance REAL DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_code) REFERENCES chart_of_accounts(account_code)
            )
        """)
        
        # Suppliers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                province TEXT,
                postal_code TEXT,
                tax_number TEXT,
                account_code TEXT,
                opening_balance REAL DEFAULT 0,
                current_balance REAL DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_code) REFERENCES chart_of_accounts(account_code)
            )
        """)
        
        # Employees
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department TEXT,
                position TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                id_number TEXT,
                tax_number TEXT,
                bank_name TEXT,
                bank_account TEXT,
                salary REAL DEFAULT 0,
                start_date TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Inventory Items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                category TEXT,
                unit_of_measure TEXT,
                cost_price REAL DEFAULT 0,
                selling_price REAL DEFAULT 0,
                quantity_on_hand REAL DEFAULT 0,
                minimum_level REAL DEFAULT 0,
                maximum_level REAL DEFAULT 0,
                account_code TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_code) REFERENCES chart_of_accounts(account_code)
            )
        """)
        
        # Fixed Assets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fixed_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_code TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                category TEXT,
                purchase_date TEXT,
                purchase_cost REAL DEFAULT 0,
                depreciation_rate REAL DEFAULT 0,
                accumulated_depreciation REAL DEFAULT 0,
                net_book_value REAL DEFAULT 0,
                disposal_date TEXT,
                disposal_value REAL DEFAULT 0,
                account_code TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_code) REFERENCES chart_of_accounts(account_code)
            )
        """)
        
        # Projects
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                client TEXT,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                budget REAL DEFAULT 0,
                status TEXT DEFAULT 'Active',
                progress REAL DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Directors
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS directors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                director_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                position TEXT,
                email TEXT,
                phone TEXT,
                shareholding_percentage REAL DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Journal Entries (Transactions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_number TEXT UNIQUE NOT NULL,
                entry_date TEXT NOT NULL,
                reference TEXT,
                description TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                total_debit REAL DEFAULT 0,
                total_credit REAL DEFAULT 0,
                status TEXT DEFAULT 'Posted',
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                posted_at TIMESTAMP
            )
        """)
        
        # Journal Entry Lines
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journal_entry_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                journal_entry_id INTEGER NOT NULL,
                account_code TEXT NOT NULL,
                description TEXT,
                debit REAL DEFAULT 0,
                credit REAL DEFAULT 0,
                line_number INTEGER,
                FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id),
                FOREIGN KEY (account_code) REFERENCES chart_of_accounts(account_code)
            )
        """)
        
        # Settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # License
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS license (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT UNIQUE NOT NULL,
                machine_id TEXT NOT NULL,
                company_name TEXT,
                activation_date TEXT,
                expiry_date TEXT,
                license_type TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
    
    # Company Info Methods
    def save_company_info(self, company_data: Dict) -> bool:
        """Save or update company information"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT id FROM company_info LIMIT 1")
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE company_info SET
                        company_name = ?, registration_number = ?, tax_number = ?,
                        vat_number = ?, address = ?, city = ?, province = ?,
                        postal_code = ?, country = ?, phone = ?, email = ?,
                        website = ?, financial_year_end = ?, currency = ?,
                        date_format = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    company_data.get('company_name'),
                    company_data.get('registration_number'),
                    company_data.get('tax_number'),
                    company_data.get('vat_number'),
                    company_data.get('address'),
                    company_data.get('city'),
                    company_data.get('province'),
                    company_data.get('postal_code'),
                    company_data.get('country', 'South Africa'),
                    company_data.get('phone'),
                    company_data.get('email'),
                    company_data.get('website'),
                    company_data.get('financial_year_end'),
                    company_data.get('currency', 'ZAR'),
                    company_data.get('date_format', 'YYYY/MM/DD'),
                    existing['id']
                ))
            else:
                cursor.execute("""
                    INSERT INTO company_info (
                        company_name, registration_number, tax_number, vat_number,
                        address, city, province, postal_code, country, phone,
                        email, website, financial_year_end, currency, date_format
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_data.get('company_name'),
                    company_data.get('registration_number'),
                    company_data.get('tax_number'),
                    company_data.get('vat_number'),
                    company_data.get('address'),
                    company_data.get('city'),
                    company_data.get('province'),
                    company_data.get('postal_code'),
                    company_data.get('country', 'South Africa'),
                    company_data.get('phone'),
                    company_data.get('email'),
                    company_data.get('website'),
                    company_data.get('financial_year_end'),
                    company_data.get('currency', 'ZAR'),
                    company_data.get('date_format', 'YYYY/MM/DD')
                ))
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving company info: {e}")
            self.connection.rollback()
            return False
    
    def get_company_info(self) -> Optional[Dict]:
        """Get company information"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM company_info LIMIT 1")
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    # Chart of Accounts Methods
    def load_chart_of_accounts_from_csv(self, csv_path: str) -> bool:
        """Load Chart of Accounts from CSV file"""
        import csv
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                cursor = self.connection.cursor()
                
                for row in reader:
                    cursor.execute("""
                        INSERT OR REPLACE INTO chart_of_accounts
                        (account_code, account_name, category, sub_category, account_type, is_active)
                        VALUES (?, ?, ?, ?, ?, 1)
                    """, (
                        row.get('Account Code', ''),
                        row.get('Account Name', ''),
                        row.get('Category', ''),
                        row.get('Sub-Category', ''),
                        self._determine_account_type(row.get('Category', ''))
                    ))
                
                self.connection.commit()
                return True
        except Exception as e:
            print(f"Error loading Chart of Accounts: {e}")
            return False
    
    def _determine_account_type(self, category: str) -> str:
        """Determine account type from category"""
        if category.startswith('I'):
            return 'Revenue'
        elif category.startswith('E'):
            return 'Expenditure'
        elif category.startswith('A'):
            return 'Asset'
        elif category.startswith('L'):
            return 'Liability'
        elif category.startswith('E'):
            return 'Equity'
        return 'Other'
    
    def get_chart_of_accounts(self, account_type: str = None) -> List[Dict]:
        """Get Chart of Accounts, optionally filtered by type"""
        cursor = self.connection.cursor()
        if account_type:
            cursor.execute("SELECT * FROM chart_of_accounts WHERE account_type = ? AND is_active = 1", (account_type,))
        else:
            cursor.execute("SELECT * FROM chart_of_accounts WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]
    
    def get_account_names(self) -> List[str]:
        """Get list of account names for dropdowns"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT account_code, account_name FROM chart_of_accounts WHERE is_active = 1 ORDER BY account_code")
        return [f"{row['account_code']} - {row['account_name']}" for row in cursor.fetchall()]
    
    # Customer Methods
    def add_customer(self, customer_data: Dict) -> bool:
        """Add a new customer"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO customers (
                    customer_code, name, contact_person, email, phone,
                    address, city, province, postal_code, tax_number,
                    account_code, opening_balance, current_balance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer_data.get('customer_code'),
                customer_data.get('name'),
                customer_data.get('contact_person'),
                customer_data.get('email'),
                customer_data.get('phone'),
                customer_data.get('address'),
                customer_data.get('city'),
                customer_data.get('province'),
                customer_data.get('postal_code'),
                customer_data.get('tax_number'),
                customer_data.get('account_code'),
                customer_data.get('opening_balance', 0),
                customer_data.get('opening_balance', 0)
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding customer: {e}")
            self.connection.rollback()
            return False
    
    def get_customers(self) -> List[Dict]:
        """Get all customers"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_customer(self, customer_id: int, customer_data: Dict) -> bool:
        """Update customer information"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE customers SET
                    name = ?, contact_person = ?, email = ?, phone = ?,
                    address = ?, city = ?, province = ?, postal_code = ?,
                    tax_number = ?, account_code = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                customer_data.get('name'),
                customer_data.get('contact_person'),
                customer_data.get('email'),
                customer_data.get('phone'),
                customer_data.get('address'),
                customer_data.get('city'),
                customer_data.get('province'),
                customer_data.get('postal_code'),
                customer_data.get('tax_number'),
                customer_data.get('account_code'),
                customer_id
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating customer: {e}")
            self.connection.rollback()
            return False
    
    def delete_customer(self, customer_id: int) -> bool:
        """Soft delete customer"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE customers SET is_active = 0 WHERE id = ?", (customer_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting customer: {e}")
            return False
    
    # Supplier Methods
    def add_supplier(self, supplier_data: Dict) -> bool:
        """Add a new supplier"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO suppliers (
                    supplier_code, name, contact_person, email, phone,
                    address, city, province, postal_code, tax_number,
                    account_code, opening_balance, current_balance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                supplier_data.get('supplier_code'),
                supplier_data.get('name'),
                supplier_data.get('contact_person'),
                supplier_data.get('email'),
                supplier_data.get('phone'),
                supplier_data.get('address'),
                supplier_data.get('city'),
                supplier_data.get('province'),
                supplier_data.get('postal_code'),
                supplier_data.get('tax_number'),
                supplier_data.get('account_code'),
                supplier_data.get('opening_balance', 0),
                supplier_data.get('opening_balance', 0)
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding supplier: {e}")
            self.connection.rollback()
            return False
    
    def get_suppliers(self) -> List[Dict]:
        """Get all suppliers"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_supplier(self, supplier_id: int, supplier_data: Dict) -> bool:
        """Update supplier information"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE suppliers SET
                    name = ?, contact_person = ?, email = ?, phone = ?,
                    address = ?, city = ?, province = ?, postal_code = ?,
                    tax_number = ?, account_code = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                supplier_data.get('name'),
                supplier_data.get('contact_person'),
                supplier_data.get('email'),
                supplier_data.get('phone'),
                supplier_data.get('address'),
                supplier_data.get('city'),
                supplier_data.get('province'),
                supplier_data.get('postal_code'),
                supplier_data.get('tax_number'),
                supplier_data.get('account_code'),
                supplier_id
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating supplier: {e}")
            self.connection.rollback()
            return False
    
    def delete_supplier(self, supplier_id: int) -> bool:
        """Soft delete supplier"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE suppliers SET is_active = 0 WHERE id = ?", (supplier_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting supplier: {e}")
            return False
    
    # Employee Methods
    def add_employee(self, employee_data: Dict) -> bool:
        """Add a new employee"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO employees (
                    employee_code, name, department, position, email, phone,
                    address, id_number, tax_number, bank_name, bank_account,
                    salary, start_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                employee_data.get('employee_code'),
                employee_data.get('name'),
                employee_data.get('department'),
                employee_data.get('position'),
                employee_data.get('email'),
                employee_data.get('phone'),
                employee_data.get('address'),
                employee_data.get('id_number'),
                employee_data.get('tax_number'),
                employee_data.get('bank_name'),
                employee_data.get('bank_account'),
                employee_data.get('salary', 0),
                employee_data.get('start_date')
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding employee: {e}")
            self.connection.rollback()
            return False
    
    def get_employees(self) -> List[Dict]:
        """Get all employees"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM employees WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_employee(self, employee_id: int, employee_data: Dict) -> bool:
        """Update employee information"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE employees SET
                    name = ?, department = ?, position = ?, email = ?, phone = ?,
                    address = ?, id_number = ?, tax_number = ?, bank_name = ?,
                    bank_account = ?, salary = ?, start_date = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                employee_data.get('name'),
                employee_data.get('department'),
                employee_data.get('position'),
                employee_data.get('email'),
                employee_data.get('phone'),
                employee_data.get('address'),
                employee_data.get('id_number'),
                employee_data.get('tax_number'),
                employee_data.get('bank_name'),
                employee_data.get('bank_account'),
                employee_data.get('salary'),
                employee_data.get('start_date'),
                employee_id
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating employee: {e}")
            self.connection.rollback()
            return False
    
    def delete_employee(self, employee_id: int) -> bool:
        """Soft delete employee"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE employees SET is_active = 0 WHERE id = ?", (employee_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting employee: {e}")
            return False
    
    # Inventory Methods
    def add_inventory_item(self, item_data: Dict) -> bool:
        """Add a new inventory item"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO inventory (
                    item_code, description, category, unit_of_measure,
                    cost_price, selling_price, quantity_on_hand,
                    minimum_level, maximum_level, account_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_data.get('item_code'),
                item_data.get('description'),
                item_data.get('category'),
                item_data.get('unit_of_measure'),
                item_data.get('cost_price', 0),
                item_data.get('selling_price', 0),
                item_data.get('quantity_on_hand', 0),
                item_data.get('minimum_level', 0),
                item_data.get('maximum_level', 0),
                item_data.get('account_code')
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding inventory item: {e}")
            self.connection.rollback()
            return False
    
    def get_inventory_items(self) -> List[Dict]:
        """Get all inventory items"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM inventory WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_inventory_item(self, item_id: int, item_data: Dict) -> bool:
        """Update inventory item"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE inventory SET
                    description = ?, category = ?, unit_of_measure = ?,
                    cost_price = ?, selling_price = ?, quantity_on_hand = ?,
                    minimum_level = ?, maximum_level = ?, account_code = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                item_data.get('description'),
                item_data.get('category'),
                item_data.get('unit_of_measure'),
                item_data.get('cost_price'),
                item_data.get('selling_price'),
                item_data.get('quantity_on_hand'),
                item_data.get('minimum_level'),
                item_data.get('maximum_level'),
                item_data.get('account_code'),
                item_id
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating inventory item: {e}")
            self.connection.rollback()
            return False
    
    def delete_inventory_item(self, item_id: int) -> bool:
        """Soft delete inventory item"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE inventory SET is_active = 0 WHERE id = ?", (item_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting inventory item: {e}")
            return False
    
    # Fixed Asset Methods
    def add_fixed_asset(self, asset_data: Dict) -> bool:
        """Add a new fixed asset"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO fixed_assets (
                    asset_code, description, category, purchase_date,
                    purchase_cost, depreciation_rate, accumulated_depreciation,
                    net_book_value, account_code
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                asset_data.get('asset_code'),
                asset_data.get('description'),
                asset_data.get('category'),
                asset_data.get('purchase_date'),
                asset_data.get('purchase_cost', 0),
                asset_data.get('depreciation_rate', 0),
                asset_data.get('accumulated_depreciation', 0),
                asset_data.get('purchase_cost', 0),
                asset_data.get('account_code')
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding fixed asset: {e}")
            self.connection.rollback()
            return False
    
    def get_fixed_assets(self) -> List[Dict]:
        """Get all fixed assets"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM fixed_assets WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_fixed_asset(self, asset_id: int, asset_data: Dict) -> bool:
        """Update fixed asset"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE fixed_assets SET
                    description = ?, category = ?, purchase_date = ?,
                    purchase_cost = ?, depreciation_rate = ?,
                    accumulated_depreciation = ?, net_book_value = ?,
                    account_code = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                asset_data.get('description'),
                asset_data.get('category'),
                asset_data.get('purchase_date'),
                asset_data.get('purchase_cost'),
                asset_data.get('depreciation_rate'),
                asset_data.get('accumulated_depreciation'),
                asset_data.get('net_book_value'),
                asset_data.get('account_code'),
                asset_id
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating fixed asset: {e}")
            self.connection.rollback()
            return False
    
    def delete_fixed_asset(self, asset_id: int) -> bool:
        """Soft delete fixed asset"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE fixed_assets SET is_active = 0 WHERE id = ?", (asset_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting fixed asset: {e}")
            return False
    
    # Project Methods
    def add_project(self, project_data: Dict) -> bool:
        """Add a new project"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO projects (
                    project_code, name, client, description,
                    start_date, end_date, budget, status, progress
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_data.get('project_code'),
                project_data.get('name'),
                project_data.get('client'),
                project_data.get('description'),
                project_data.get('start_date'),
                project_data.get('end_date'),
                project_data.get('budget', 0),
                project_data.get('status', 'Active'),
                project_data.get('progress', 0)
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding project: {e}")
            self.connection.rollback()
            return False
    
    def get_projects(self) -> List[Dict]:
        """Get all projects"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM projects WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_project(self, project_id: int, project_data: Dict) -> bool:
        """Update project"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE projects SET
                    name = ?, client = ?, description = ?,
                    start_date = ?, end_date = ?, budget = ?,
                    status = ?, progress = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                project_data.get('name'),
                project_data.get('client'),
                project_data.get('description'),
                project_data.get('start_date'),
                project_data.get('end_date'),
                project_data.get('budget'),
                project_data.get('status'),
                project_data.get('progress'),
                project_id
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating project: {e}")
            self.connection.rollback()
            return False
    
    def delete_project(self, project_id: int) -> bool:
        """Soft delete project"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE projects SET is_active = 0 WHERE id = ?", (project_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting project: {e}")
            return False
    
    # Director Methods
    def add_director(self, director_data: Dict) -> bool:
        """Add a new director"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO directors (
                    director_code, name, position, email, phone,
                    shareholding_percentage
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                director_data.get('director_code'),
                director_data.get('name'),
                director_data.get('position'),
                director_data.get('email'),
                director_data.get('phone'),
                director_data.get('shareholding_percentage', 0)
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error adding director: {e}")
            self.connection.rollback()
            return False
    
    def get_directors(self) -> List[Dict]:
        """Get all directors"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM directors WHERE is_active = 1")
        return [dict(row) for row in cursor.fetchall()]
    
    def update_director(self, director_id: int, director_data: Dict) -> bool:
        """Update director"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE directors SET
                    name = ?, position = ?, email = ?, phone = ?,
                    shareholding_percentage = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                director_data.get('name'),
                director_data.get('position'),
                director_data.get('email'),
                director_data.get('phone'),
                director_data.get('shareholding_percentage'),
                director_id
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating director: {e}")
            self.connection.rollback()
            return False
    
    def delete_director(self, director_id: int) -> bool:
        """Soft delete director"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE directors SET is_active = 0 WHERE id = ?", (director_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting director: {e}")
            return False
    
    # Settings Methods
    def save_setting(self, key: str, value: str, description: str = None) -> bool:
        """Save a setting"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, description, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, description))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving setting: {e}")
            return False
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else None
    
    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT key, value FROM settings")
        return {row['key']: row['value'] for row in cursor.fetchall()}
    
    # License Methods
    def save_license(self, license_data: Dict) -> bool:
        """Save license information"""
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO license (
                    license_key, machine_id, company_name, activation_date,
                    expiry_date, license_type, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                license_data.get('license_key'),
                license_data.get('machine_id'),
                license_data.get('company_name'),
                license_data.get('activation_date'),
                license_data.get('expiry_date'),
                license_data.get('license_type'),
                license_data.get('is_active', True)
            ))
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving license: {e}")
            return False
    
    def get_license(self) -> Optional[Dict]:
        """Get license information"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM license WHERE is_active = 1 LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def validate_license(self, license_key: str, machine_id: str) -> bool:
        """Validate license key"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM license 
            WHERE license_key = ? AND machine_id = ? AND is_active = 1
        """, (license_key, machine_id))
        row = cursor.fetchone()
        if row:
            # Check expiry date
            expiry_date = row.get('expiry_date')
            if expiry_date:
                expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
                if datetime.now() > expiry:
                    return False
            return True
        return False

# Global database instance
db = DatabaseHandler()
