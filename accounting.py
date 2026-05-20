"""
Accounting Ledger Engine for RIGEL Business
Double-entry bookkeeping with VAT support, Trial Balance, and Financial Statements.
"""

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP

# ─────────────────────────────────────────────────────────────────────────────
#  CHART OF ACCOUNTS
#  Account codes are fixed strings; type determines classification.
# ─────────────────────────────────────────────────────────────────────────────
CHART_OF_ACCOUNTS = {
    # Assets
    "1000": {"name": "Bank — FNB Cheque",          "type": "Asset",        "subtype": "Bank",           "dr": True},
    "1001": {"name": "Bank — FNB Savings",          "type": "Asset",        "subtype": "Bank",           "dr": True},
    "1100": {"name": "Accounts Receivable",         "type": "Asset",        "subtype": "Current Asset",  "dr": True},
    "1200": {"name": "Inventory",                    "type": "Asset",        "subtype": "Current Asset",  "dr": True},
    "1300": {"name": "Fixed Assets",                 "type": "Asset",        "subtype": "Non-Current",    "dr": True},
    "1400": {"name": "Investments",                  "type": "Asset",        "subtype": "Non-Current",    "dr": True},
    "1500": {"name": "VAT Input",                    "type": "Asset",        "subtype": "Current Asset",  "dr": True},
    "1600": {"name": "Prepaid Expenses",             "type": "Asset",        "subtype": "Current Asset",  "dr": True},
    # Liabilities
    "2000": {"name": "Accounts Payable",             "type": "Liability",    "subtype": "Current",        "dr": False},
    "2100": {"name": "Loan Payables",                "type": "Liability",    "subtype": "Non-Current",    "dr": False},
    "2200": {"name": "VAT Output",                   "type": "Liability",    "subtype": "Current",        "dr": False},
    "2300": {"name": "Accrued Expenses",             "type": "Liability",    "subtype": "Current",        "dr": False},
    # Equity
    "3000": {"name": "Share Capital",                "type": "Equity",       "subtype": "Share Capital",  "dr": False},
    "3100": {"name": "Retained Earnings",            "type": "Equity",       "subtype": "Retained Earnings","dr": False},
    # Income
    "4000": {"name": "Sales Revenue",                "type": "Income",       "subtype": "Trading Revenue","dr": False},
    "4100": {"name": "Other Income",                 "type": "Income",       "subtype": "Other Income",   "dr": False},
    "4200": {"name": "Investment Income",            "type": "Income",       "subtype": "Investment",     "dr": False},
    "4300": {"name": "Gain on Investment Disposal",  "type": "Income",       "subtype": "Gains",          "dr": False},
    # Expenses
    "5000": {"name": "Cost of Sales",                "type": "Expense",      "subtype": "Cost of Sales",  "dr": True},
    "5100": {"name": "Operating Expenses",           "type": "Expense",      "subtype": "Operating",      "dr": True},
    "5200": {"name": "Interest Expense",             "type": "Expense",      "subtype": "Financing",      "dr": True},
    "5300": {"name": "Depreciation",                 "type": "Expense",      "subtype": "Depreciation",   "dr": True},
    "5400": {"name": "Administrative Expenses",      "type": "Expense",      "subtype": "Admin",          "dr": True},
}

# VAT rate (South Africa standard)
VAT_RATE = Decimal("0.15")

# ─────────────────────────────────────────────────────────────────────────────
#  UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def _to_decimal(v) -> Decimal:
    """Convert various numeric types to Decimal with 2 decimal places."""
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def _fmt_amount(amount) -> str:
    """Format amount as R 1,234.00"""
    a = _to_decimal(amount)
    return f"R {a:,.2f}"

def _next_code(prefix: str, existing: List[str]) -> str:
    """Generate next code like SUP001, LN002, etc."""
    nums = [int(c[len(prefix):]) for c in existing if c.startswith(prefix) and c[len(prefix):].isdigit()]
    nxt = (max(nums) + 1) if nums else 1
    return f"{prefix}{nxt:03d}"

def _journal_code(existing: List[str]) -> str:
    """Generate unique journal entry code: JRN000001"""
    nums = [int(c[3:]) for c in existing if c.startswith("JRN") and c[3:].isdigit()]
    nxt = (max(nums) + 1) if nums else 1
    return f"JRN{nxt:06d}"

# ─────────────────────────────────────────────────────────────────────────────
#  ACCOUNTING LEDGER
# ─────────────────────────────────────────────────────────────────────────────
class AccountingLedger:
    """
    Core accounting engine: persists chart of accounts, all masterfiles,
    and journal entries (double-entry). Provides financial reporting.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # File paths
        self.coa_file       = self.data_dir / "chart_of_accounts.json"
        self.je_file        = self.data_dir / "journal_entries.json"
        self.suppliers_file = self.data_dir / "suppliers.json"
        self.loans_file     = self.data_dir / "loans.json"
        self.investments_file = self.data_dir / "investments.json"
        self.inventory_file = self.data_dir / "inventory.json"
        self.assets_file    = self.data_dir / "fixed_assets.json"
        # Initialize storage
        self._ensure_files()

    # ═══════════════════════════════════════════════════════════════════════
    #  Data persistence & initialization
    # ═══════════════════════════════════════════════════════════════════════
    def _ensure_files(self):
        """Create default files if they don't exist."""
        if not self.coa_file.exists():
            self._write_json(self.coa_file, CHART_OF_ACCOUNTS)
        if not self.je_file.exists():
            self._write_json(self.je_file, [])
        if not self.suppliers_file.exists():
            self._write_json(self.suppliers_file, [])
        if not self.loans_file.exists():
            self._write_json(self.loans_file, [])
        if not self.investments_file.exists():
            self._write_json(self.investments_file, [])
        if not self.inventory_file.exists():
            self._write_json(self.inventory_file, [])
        if not self.assets_file.exists():
            self._write_json(self.assets_file, [])

    def _read_json(self, path: Path, default=None):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return default if default is not None else {}

    def _write_json(self, path: Path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ═══════════════════════════════════════════════════════════════════════
    #  Chart of Accounts
    # ═══════════════════════════════════════════════════════════════════════
    def get_coa(self) -> Dict[str, dict]:
        return self._read_json(self.coa_file, {})

    def get_account(self, code: str) -> Optional[dict]:
        return self.get_coa().get(code)

    # ═══════════════════════════════════════════════════════════════════════
    #  Journal Entries
    # ═══════════════════════════════════════════════════════════════════════
    def _load_jes(self) -> List[dict]:
        return self._read_json(self.je_file, [])

    def _save_jes(self, entries: List[dict]):
        self._write_json(self.je_file, entries)

    def post_journal_entry(self, date_str: str, reference: str, description: str,
                           lines: List[dict], auto_balance: bool = True) -> str:
        """
        Post a journal entry.
        :param date_str: ISO date string (YYYY-MM-DD)
        :param reference: external reference (e.g., invoice number)
        :param description: description
        :param lines: list of {account_code, debit, credit, notes}
        :param auto_balance: if True, automatically balance by adjusting first line's debit
        :return: journal code
        """
        entries = self._load_jes()
        jcode = _journal_code([e.get("code", "") for e in entries])

        total_dr = sum(_to_decimal(l.get("debit", 0)) for l in lines)
        total_cr = sum(_to_decimal(l.get("credit", 0)) for l in lines)

        if auto_balance and total_dr != total_cr:
            # Balance to first line (assumed primary account) by adjusting its debit
            diff = (total_cr - total_dr)
            for i, l in enumerate(lines):
                if i == 0:
                    cur = _to_decimal(l.get("debit", 0))
                    lines[i]["debit"] = float(_to_decimal(cur + diff))
                    break

        # Validate each account exists
        coa = self.get_coa()
        for l in lines:
            acct_code = l.get("account_code")
            if acct_code not in coa:
                raise ValueError(f"Invalid account code: {acct_code}")

        je = {
            "code": jcode,
            "date": date_str,
            "reference": reference,
            "description": description,
            "lines": lines,
            "timestamp": datetime.now().isoformat()
        }
        entries.append(je)
        self._save_jes(entries)
        return jcode

    def get_journal_entries(self, start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            account_code: Optional[str] = None) -> List[dict]:
        """Retrieve journal entries, optionally filtered."""
        entries = self._load_jes()
        if start_date:
            entries = [e for e in entries if e["date"] >= start_date]
        if end_date:
            entries = [e for e in entries if e["date"] <= end_date]
        if account_code:
            entries = [e for e in entries 
                      if any(l.get("account_code") == account_code for l in e["lines"])]
        return entries

    # ═══════════════════════════════════════════════════════════════════════
    #  CCE Cumulative Update - Critical Shared Fix for Phase 2
    # ═══════════════════════════════════════════════════════════════════════
    def update_cce(self, transaction_amount: float, transaction_type: str = "payment") -> float:
        """
        Critical Shared Fix: CCE Cumulative Update
        Ensures Cash & Cash Equivalents updates cumulatively across all modules.
        
        This function must be called by all modules that affect cash:
        - Cash Book (CB-002)
        - Customers (CUS-005, CUS-006) 
        - Directors (DIR-014)
        - Assets (AST-004)
        - Suppliers, Inventories, Investments, Loans
        
        Args:
            transaction_amount: Amount affecting cash (negative for payments, positive for receipts)
            transaction_type: Type of transaction for tracking
            
        Returns:
            New cumulative CCE balance
        """
        try:
            # Get current CCE balance from bank accounts
            cce_accounts = ["1000", "1001"]  # Bank FNB Cheque, Bank FNB Savings
            current_cce = Decimal("0.00")
            
            entries = self.get_journal_entries()
            for entry in entries:
                for line in entry["lines"]:
                    account_code = line.get("account_code", "")
                    if account_code in cce_accounts:
                        debit = Decimal(str(line.get("debit", 0)))
                        credit = Decimal(str(line.get("credit", 0)))
                        current_cce += debit - credit
            
            # Apply cumulative update
            amount_change = Decimal(str(transaction_amount))
            new_cce = current_cce + amount_change
            
            # Log the CCE update for audit trail
            cce_log_file = self.data_dir / "cce_updates.json"
            cce_logs = self._read_json(cce_log_file, [])
            
            cce_log = {
                "timestamp": datetime.now().isoformat(),
                "transaction_type": transaction_type,
                "amount_change": float(amount_change),
                "previous_cce": float(current_cce),
                "new_cce": float(new_cce),
                "cumulative": True
            }
            cce_logs.append(cce_log)
            self._write_json(cce_log_file, cce_logs)
            
            return float(new_cce)
            
        except Exception as e:
            # In case of error, return current CCE without update
            print(f"Error in CCE update: {e}")
            return float(current_cce) if 'current_cce' in locals() else 0.00
    
    def get_cce_balance(self) -> float:
        """
        Get current Cash & Cash Equivalents balance
        """
        try:
            cce_accounts = ["1000", "1001"]  # Bank accounts
            current_cce = Decimal("0.00")
            
            entries = self.get_journal_entries()
            for entry in entries:
                for line in entry["lines"]:
                    account_code = line.get("account_code", "")
                    if account_code in cce_accounts:
                        debit = Decimal(str(line.get("debit", 0)))
                        credit = Decimal(str(line.get("credit", 0)))
                        current_cce += debit - credit
            
            return float(current_cce)
            
        except Exception as e:
            print(f"Error getting CCE balance: {e}")
            return 0.00

    # ═══════════════════════════════════════════════════════════════════════
    #  General Ledger (account-level transaction listing)
    # ═══════════════════════════════════════════════════════════════════════
    def general_ledger(self, account_code: Optional[str] = None,
                       start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[dict]:
        """
        Returns ledger entries. Each entry includes debits and credits for period.
        """
        entries = self.get_journal_entries(start_date=start_date, end_date=end_date)
        ledger_lines = []
        for je in entries:
            for line in je["lines"]:
                if account_code is None or line["account_code"] == account_code:
                    ledger_lines.append({
                        "date": je["date"],
                        "journal_code": je["code"],
                        "reference": je["reference"],
                        "description": je["description"],
                        "account_code": line["account_code"],
                        "account_name": self.get_account(line["account_code"])["name"] if self.get_account(line["account_code"]) else "",
                        "debit": line.get("debit", 0),
                        "credit": line.get("credit", 0),
                        "notes": line.get("notes", "")
                    })
        return ledger_lines
