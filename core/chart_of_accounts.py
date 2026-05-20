#!/usr/bin/env python3
"""
RIGEL Business Chart of Accounts Integration
Loads COA from CSV and provides dropdown integration throughout the application
"""

import csv
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

# ─────────────────────────────────────────────────────────────────────────────
#  CHART OF ACCOUNTS DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Account:
    """Account data structure"""
    code: str
    name: str
    category: str
    sub_category: str
    account_type: str  # Asset, Liability, Equity, Income, Expense
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "sub_category": self.sub_category,
            "account_type": self.account_type,
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Account':
        return cls(
            code=data["code"],
            name=data["name"],
            category=data["category"],
            sub_category=data["sub_category"],
            account_type=data["account_type"],
            is_active=data.get("is_active", True)
        )

class ChartOfAccounts:
    """Complete Chart of Accounts management"""

    def __init__(self):
        self.accounts: Dict[str, Account] = {}
        self.categories: Dict[str, List[str]] = {
            "Revenue": [],
            "Expenditure": [],
            "Assets": [],
            "Liabilities": [],
            "Equity": []
        }
        self.db_path = Path("data/coa.db")

    def load_from_csv(self, csv_path: str) -> bool:
        """Load COA from CSV file"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                # Skip first 3 empty lines (;;;;;)
                for _ in range(3):
                    f.readline()
                
                # Read the header line (line 4)
                header_line = f.readline().strip()
                
                # Split header by semicolons, then strip whitespace and empty strings
                headers = [h.strip() for h in header_line.split(';') if h.strip()]
                print(f"COA headers: {headers}")
                
                # Clear existing data
                self.accounts.clear()
                for category in self.categories:
                    self.categories[category].clear()

                # Read the rest of the lines as data
                for line_num, line in enumerate(f, start=5):
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Split line by semicolons
                    parts = [p.strip() for p in line.split(';') if p.strip()]
                    
                    if len(parts) < 4:
                        continue  # Skip incomplete rows
                        
                    # Extract fields: [Account Code, Category, Sub-Category, Account]
                    code = parts[0]
                    category = parts[1]
                    sub_category = parts[2]
                    name = parts[3]
                    
                    # Skip if no code or name
                    if not code or not name:
                        continue

                    account = Account(
                        code=code,
                        name=name,
                        category=category,
                        sub_category=sub_category,
                        account_type=self._map_category_to_type(category)
                    )

                    if account.code and account.name:
                        self.accounts[account.code] = account

                        # Add to category list
                        if account.category in self.categories:
                            self.categories[account.category].append(account.code)

                # Sort categories
                for category in self.categories:
                    self.categories[category].sort()

                self.save_to_database()
                return True

        except Exception as e:
            print(f"Error loading COA from CSV: {e}")
            return False

    def _map_category_to_type(self, category: str) -> str:
        """Map category to account type"""
        mapping = {
            "Revenue": "Income",
            "Expenditure": "Expense",
            "Assets": "Asset",
            "Liabilities": "Liability",
            "Equity": "Equity"
        }
        return mapping.get(category, "Asset")

    def save_to_database(self):
        """Save COA to SQLite database"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Create table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    sub_category TEXT,
                    account_type TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            ''')

            # Clear existing data
            cursor.execute('DELETE FROM accounts')

            # Insert accounts
            for account in self.accounts.values():
                cursor.execute('''
                    INSERT INTO accounts (code, name, category, sub_category, account_type, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    account.code,
                    account.name,
                    account.category,
                    account.sub_category,
                    account.account_type,
                    1 if account.is_active else 0
                ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error saving COA to database: {e}")

    def load_from_database(self) -> bool:
        """Load COA from SQLite database"""
        try:
            if not self.db_path.exists():
                return False

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM accounts')
            rows = cursor.fetchall()

            # Clear existing data
            self.accounts.clear()
            for category in self.categories:
                self.categories[category].clear()

            for row in rows:
                account = Account(
                    code=row[0],
                    name=row[1],
                    category=row[2],
                    sub_category=row[3],
                    account_type=row[4],
                    is_active=bool(row[5])
                )

                self.accounts[account.code] = account

                # Add to category list
                if account.category in self.categories:
                    self.categories[account.category].append(account.code)

            # Sort categories
            for category in self.categories:
                self.categories[category].sort()

            conn.close()
            return True

        except Exception as e:
            print(f"Error loading COA from database: {e}")
            return False

    def get_accounts_by_category(self, category: str) -> List[Account]:
        """Get all accounts in a specific category"""
        if category not in self.categories:
            return []

        return [self.accounts[code] for code in self.categories[category] if code in self.accounts]

    def get_account_by_code(self, code: str) -> Optional[Account]:
        """Get account by code"""
        return self.accounts.get(code)

    def get_all_accounts(self) -> List[Account]:
        """Get all accounts"""
        return list(self.accounts.values())

    def search_accounts(self, query: str) -> List[Account]:
        """Search accounts by name or code"""
        query = query.lower()
        results = []

        for account in self.accounts.values():
            if (query in account.code.lower() or
                query in account.name.lower() or
                query in account.category.lower() or
                query in account.sub_category.lower()):
                results.append(account)

        return results

    def get_dropdown_data(self, category: Optional[str] = None) -> List[Tuple[str, str]]:
        """Get data formatted for dropdowns (code, display_name)"""
        accounts = self.get_accounts_by_category(category) if category else self.get_all_accounts()

        return [(acc.code, f"{acc.code} - {acc.name}") for acc in accounts if acc.is_active]

# ─────────────────────────────────────────────────────────────────────────────
#  COA INTEGRATION MANAGER
# ─────────────────────────────────────────────────────────────────────────────
class COAIntegrationManager:
    """Manages COA integration throughout the application"""

    def __init__(self):
        self.coa = ChartOfAccounts()
        self.load_coa()

    def load_coa(self):
        """Load COA from database or create default"""
        if not self.coa.load_from_database():
            # Load default COA if database doesn't exist
            self.create_default_coa()

    def create_default_coa(self):
        """Create default Chart of Accounts from RIGEL DEVELOPMENT.csv"""
        # Try to load from the official CSV file first
        csv_path = Path("RIGEL DEVELOPMENT.csv")
        if csv_path.exists():
            if self.coa.load_from_csv(str(csv_path)):
                print(f"Successfully loaded {len(self.coa.accounts)} accounts from RIGEL DEVELOPMENT.csv")
                return
        
        # Fallback to default accounts if CSV not found
        default_accounts = [
            # Assets
            Account("1000", "Bank — FNB Cheque", "Assets", "Bank", "Asset"),
            Account("1001", "Bank — FNB Savings", "Assets", "Bank", "Asset"),
            Account("1100", "Accounts Receivable", "Assets", "Current Asset", "Asset"),
            Account("1200", "Inventory", "Assets", "Current Asset", "Asset"),
            Account("1300", "Fixed Assets", "Assets", "Non-Current", "Asset"),
            Account("1400", "Investments", "Assets", "Non-Current", "Asset"),
            Account("1500", "VAT Input", "Assets", "Current Asset", "Asset"),

            # Liabilities
            Account("2000", "Accounts Payable", "Liabilities", "Current", "Liability"),
            Account("2100", "Loan Payables", "Liabilities", "Non-Current", "Liability"),
            Account("2200", "VAT Output", "Liabilities", "Current", "Liability"),
            Account("2300", "Accrued Expenses", "Liabilities", "Current", "Liability"),

            # Equity
            Account("3000", "Share Capital", "Equity", "Share Capital", "Equity"),
            Account("3100", "Retained Earnings", "Equity", "Retained Earnings", "Equity"),

            # Revenue
            Account("4000", "Sales Revenue", "Revenue", "Trading Revenue", "Income"),
            Account("4100", "Other Income", "Revenue", "Other Income", "Income"),
            Account("4200", "Investment Income", "Revenue", "Investment", "Income"),

            # Expenditure
            Account("5000", "Cost of Sales", "Expenditure", "Cost of Sales", "Expense"),
            Account("5100", "Operating Expenses", "Expenditure", "Operating", "Expense"),
            Account("5200", "Interest Expense", "Expenditure", "Financing", "Expense"),
            Account("5300", "Depreciation", "Expenditure", "Depreciation", "Expense"),
            Account("5400", "Administrative Expenses", "Expenditure", "Admin", "Expense"),
        ]

        for account in default_accounts:
            self.coa.accounts[account.code] = account
            if account.category in self.coa.categories:
                self.coa.categories[account.category].append(account.code)

        # Sort categories
        for category in self.coa.categories:
            self.coa.categories[category].sort()

        self.coa.save_to_database()

    def import_from_csv(self, csv_path: str) -> bool:
        """Import COA from CSV file"""
        success = self.coa.load_from_csv(csv_path)
        if success:
            print(f"Successfully imported {len(self.coa.accounts)} accounts from {csv_path}")
        return success

    def get_accounts_for_dropdown(self, category: Optional[str] = None,
                                include_code: bool = True) -> List[Tuple[str, str]]:
        """Get accounts formatted for dropdown widgets"""
        return self.coa.get_dropdown_data(category)

    def populate_combobox(self, combobox, category: Optional[str] = None,
                         include_code: bool = True, placeholder: str = "Select Account"):
        """Populate a QComboBox with accounts"""
        from PyQt6.QtWidgets import QComboBox

        if not isinstance(combobox, QComboBox):
            return

        combobox.clear()
        combobox.addItem(placeholder, "")

        accounts = self.get_accounts_for_dropdown(category, include_code)
        for code, display_name in accounts:
            combobox.addItem(display_name, code)

    def get_account_name(self, code: str) -> str:
        """Get account name by code"""
        account = self.coa.get_account_by_code(code)
        return account.name if account else ""

    def get_account_category(self, code: str) -> str:
        """Get account category by code"""
        account = self.coa.get_account_by_code(code)
        return account.category if account else ""

    def validate_account_code(self, code: str) -> bool:
        """Validate if account code exists"""
        return code in self.coa.accounts

    def get_accounts_by_type(self, account_type: str) -> List[Account]:
        """Get accounts by type (Asset, Liability, Equity, Income, Expense)"""
        return [acc for acc in self.coa.accounts.values()
                if acc.account_type.lower() == account_type.lower()]

# ─────────────────────────────────────────────────────────────────────────────
#  PYQT6 WIDGET INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────
class COAComboBox:
    """Enhanced QComboBox with COA integration"""

    def __init__(self, category: Optional[str] = None, include_code: bool = True,
                 placeholder: str = "Select Account"):
        from PyQt6.QtWidgets import QComboBox
        super().__init__()
        self.category = category
        self.include_code = include_code
        self.placeholder = placeholder
        self.coa_manager = coa_manager

        self.populate_accounts()

    def populate_accounts(self):
        """Populate combobox with accounts"""
        self.clear()
        self.addItem(self.placeholder, "")

        accounts = self.coa_manager.get_accounts_for_dropdown(self.category, self.include_code)
        for code, display_name in accounts:
            self.addItem(display_name, code)

    def get_selected_code(self) -> str:
        """Get selected account code"""
        return self.currentData() or ""

    def get_selected_name(self) -> str:
        """Get selected account name"""
        code = self.get_selected_code()
        return self.coa_manager.get_account_name(code) if code else ""

    def set_selected_code(self, code: str):
        """Set selected account by code"""
        for i in range(self.count()):
            if self.itemData(i) == code:
                self.setCurrentIndex(i)
                break

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL COA MANAGER INSTANCE
# ─────────────────────────────────────────────────────────────────────────────
coa_manager = COAIntegrationManager()

# ─────────────────────────────────────────────────────────────────────────────
#  UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def initialize_coa():
    """Initialize COA system"""
    global coa_manager
    coa_manager = COAIntegrationManager()
    return coa_manager

def load_coa_from_csv(csv_path: str) -> bool:
    """Load COA from CSV file"""
    return coa_manager.import_from_csv(csv_path)

def get_accounts_for_category(category: str) -> List[Tuple[str, str]]:
    """Get accounts for specific category"""
    return coa_manager.get_accounts_for_dropdown(category)

def populate_account_dropdown(combobox, category: Optional[str] = None):
    """Populate combobox with accounts"""
    coa_manager.populate_combobox(combobox, category)

# ─────────────────────────────────────────────────────────────────────────────
#  DEFAULT CSV CONTENT (FOR TESTING)
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_COA_CSV = """Account Code,Category,Sub-Category,Account Name
1000,Assets,Bank,Bank — FNB Cheque
1001,Assets,Bank,Bank — FNB Savings
1100,Assets,Current Asset,Accounts Receivable
1200,Assets,Current Asset,Inventory
1300,Assets,Non-Current,Fixed Assets
1400,Assets,Non-Current,Investments
1500,Assets,Current Asset,VAT Input
1600,Assets,Current Asset,Prepaid Expenses
2000,Liabilities,Current,Accounts Payable
2100,Liabilities,Non-Current,Loan Payables
2200,Liabilities,Current,VAT Output
2300,Liabilities,Current,Accrued Expenses
3000,Equity,Share Capital,Share Capital
3100,Equity,Retained Earnings,Retained Earnings
4000,Revenue,Trading Revenue,Sales Revenue
4100,Revenue,Other Income,Other Income
4200,Revenue,Investment,Investment Income
4300,Revenue,Gains,Gain on Investment Disposal
5000,Expenditure,Cost of Sales,Cost of Sales
5100,Expenditure,Operating,Operating Expenses
5200,Expenditure,Financing,Interest Expense
5300,Expenditure,Depreciation,Depreciation
5400,Expenditure,Admin,Administrative Expenses"""

if __name__ == "__main__":
    # Test COA loading
    coa = ChartOfAccounts()

    # Create test CSV file
    test_csv = Path("test_coa.csv")
    with open(test_csv, 'w', newline='', encoding='utf-8') as f:
        f.write(DEFAULT_COA_CSV)

    # Load from CSV
    if coa.load_from_csv(str(test_csv)):
        print(f"Loaded {len(coa.accounts)} accounts")

        # Test category filtering
        assets = coa.get_accounts_by_category("Assets")
        print(f"Assets: {len(assets)} accounts")

        # Test search
        results = coa.search_accounts("bank")
        print(f"Bank accounts: {len(results)}")

    # Cleanup
    test_csv.unlink(missing_ok=True)