#!/usr/bin/env python3
"""
Cash Book Module Handler
Implements CB-001 to CB-006 test cases for cash book functionality
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any
from decimal import Decimal

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QTextEdit,
    QGroupBox, QGridLayout, QMessageBox, QDateEdit, QDoubleSpinBox,
    QCheckBox, QHeaderView, QFrame, QScrollArea, QTabWidget
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from accounting import AccountingLedger, CHART_OF_ACCOUNTS, _fmt_amount

class CashBookHandler(QWidget):
    """Cash Book Module Handler - Implements CB-001 to CB-006"""
    
    # Signals for communication with main window
    dashboard_refresh_requested = pyqtSignal()
    navigation_requested = pyqtSignal(str)  # Page name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ledger = getattr(parent, 'ledger', None) if parent else None
        self.cash_book_data = []
        self.editing_index = None
        
        # Data file paths
        self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cashbook_file = self.data_dir / "cashbook.json"
        
        self._load_cashbook_data()
        self._build_ui()

    def _build_ui(self):
        """Build cash book UI - CB-001: Navigation to Cash Book"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Cash Book Management")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Create tabbed interface
        tab_widget = QTabWidget()
        
        # Opening Balance Tab
        opening_balance_tab = self._create_opening_balance_tab()
        tab_widget.addTab(opening_balance_tab, "Opening Balance")
        
        # Transactions Tab
        transactions_tab = self._create_transactions_tab()
        tab_widget.addTab(transactions_tab, "Transactions")
        
        # Bank Reconciliation Tab
        reconciliation_tab = self._create_reconciliation_tab()
        tab_widget.addTab(reconciliation_tab, "Bank Reconciliation")
        
        layout.addWidget(tab_widget)

    def _create_opening_balance_tab(self):
        """Create opening balance tab - CB-001: Opening bank balance entry"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Opening Balance Group
        balance_group = QGroupBox("Opening Bank Balance")
        balance_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        balance_layout = QGridLayout(balance_group)
        balance_layout.setSpacing(10)

        # Bank Account Selection
        balance_layout.addWidget(QLabel("Bank Account:"), 0, 0)
        self.bank_account_combo = QComboBox()
        self.bank_account_combo.addItems([
            "1000 - Bank — FNB Cheque",
            "1001 - Bank — FNB Savings"
        ])
        self.bank_account_combo.currentTextChanged.connect(self._on_bank_account_changed)
        balance_layout.addWidget(self.bank_account_combo, 0, 1)

        # Opening Balance Date
        balance_layout.addWidget(QLabel("Balance Date:"), 1, 0)
        self.opening_balance_date = QDateEdit()
        self.opening_balance_date.setDate(QDate.currentDate())
        self.opening_balance_date.setCalendarPopup(True)
        balance_layout.addWidget(self.opening_balance_date, 1, 1)

        # Opening Balance Amount
        balance_layout.addWidget(QLabel("Opening Balance:"), 2, 0)
        self.opening_balance_amount = QDoubleSpinBox()
        self.opening_balance_amount.setRange(0, 999999999)
        self.opening_balance_amount.setDecimals(2)
        self.opening_balance_amount.setPrefix("R ")
        self.opening_balance_amount.setSingleStep(100.00)
        balance_layout.addWidget(self.opening_balance_amount, 2, 1)

        # Reference
        balance_layout.addWidget(QLabel("Reference:"), 3, 0)
        self.opening_balance_reference = QLineEdit()
        self.opening_balance_reference.setPlaceholderText("Opening balance reference...")
        balance_layout.addWidget(self.opening_balance_reference, 3, 1)

        # Notes
        balance_layout.addWidget(QLabel("Notes:"), 4, 0)
        self.opening_balance_notes = QTextEdit()
        self.opening_balance_notes.setMaximumHeight(80)
        self.opening_balance_notes.setPlaceholderText("Opening balance notes...")
        balance_layout.addWidget(self.opening_balance_notes, 4, 1)

        layout.addWidget(balance_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.post_opening_balance_btn = QPushButton("Post Opening Balance")
        self.post_opening_balance_btn.clicked.connect(self._post_opening_balance)
        self.post_opening_balance_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B050;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00A040;
            }
        """)
        
        self.clear_opening_balance_btn = QPushButton("Clear Form")
        self.clear_opening_balance_btn.clicked.connect(self._clear_opening_balance_form)
        self.clear_opening_balance_btn.setStyleSheet("""
            QPushButton {
                background-color: #6A7575;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5A6565;
            }
        """)
        
        button_layout.addWidget(self.post_opening_balance_btn)
        button_layout.addWidget(self.clear_opening_balance_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Existing Opening Balances Table
        existing_group = QGroupBox("Existing Opening Balances")
        existing_layout = QVBoxLayout(existing_group)
        
        self.opening_balances_table = QTableWidget()
        self.opening_balances_table.setColumnCount(5)
        self.opening_balances_table.setHorizontalHeaderLabels([
            "Bank Account", "Date", "Amount", "Reference", "Actions"
        ])
        
        # Style table
        header = self.opening_balances_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.opening_balances_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.opening_balances_table.verticalHeader().setDefaultSectionSize(40)
        existing_layout.addWidget(self.opening_balances_table)
        
        layout.addWidget(existing_group)
        layout.addStretch()

        return tab

    def _create_transactions_tab(self):
        """Create transactions tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Transaction Entry Group
        trans_group = QGroupBox("Cash Book Transaction Entry")
        trans_layout = QGridLayout(trans_group)
        trans_layout.setSpacing(10)

        # Transaction Type
        trans_layout.addWidget(QLabel("Transaction Type:"), 0, 0)
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.addItems([
            "Receipt", "Payment", "Bank Transfer", "Bank Charge"
        ])
        self.transaction_type_combo.currentTextChanged.connect(self._on_transaction_type_changed)
        trans_layout.addWidget(self.transaction_type_combo, 0, 1)

        # Date
        trans_layout.addWidget(QLabel("Date:"), 1, 0)
        self.transaction_date = QDateEdit()
        self.transaction_date.setDate(QDate.currentDate())
        self.transaction_date.setCalendarPopup(True)
        trans_layout.addWidget(self.transaction_date, 1, 1)

        # Description
        trans_layout.addWidget(QLabel("Description:"), 2, 0)
        self.transaction_description = QLineEdit()
        self.transaction_description.setPlaceholderText("Transaction description...")
        trans_layout.addWidget(self.transaction_description, 2, 1)

        # Amount
        trans_layout.addWidget(QLabel("Amount:"), 3, 0)
        self.transaction_amount = QDoubleSpinBox()
        self.transaction_amount.setRange(0, 999999999)
        self.transaction_amount.setDecimals(2)
        self.transaction_amount.setPrefix("R ")
        self.transaction_amount.setSingleStep(100.00)
        trans_layout.addWidget(self.transaction_amount, 3, 1)

        # Bank Account
        trans_layout.addWidget(QLabel("Bank Account:"), 4, 0)
        self.transaction_bank_combo = QComboBox()
        self.transaction_bank_combo.addItems([
            "1000 - Bank — FNB Cheque",
            "1001 - Bank — FNB Savings"
        ])
        trans_layout.addWidget(self.transaction_bank_combo, 4, 1)

        # Reference
        trans_layout.addWidget(QLabel("Reference:"), 5, 0)
        self.transaction_reference = QLineEdit()
        self.transaction_reference.setPlaceholderText("Transaction reference...")
        trans_layout.addWidget(self.transaction_reference, 5, 1)

        layout.addWidget(trans_group)

        # Transaction Buttons
        trans_button_layout = QHBoxLayout()
        self.post_transaction_btn = QPushButton("Post Transaction")
        self.post_transaction_btn.clicked.connect(self._post_transaction)
        self.post_transaction_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B050;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00A040;
            }
        """)
        
        self.clear_transaction_btn = QPushButton("Clear Form")
        self.clear_transaction_btn.clicked.connect(self._clear_transaction_form)
        self.clear_transaction_btn.setStyleSheet("""
            QPushButton {
                background-color: #6A7575;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5A6565;
            }
        """)
        
        trans_button_layout.addWidget(self.post_transaction_btn)
        trans_button_layout.addWidget(self.clear_transaction_btn)
        trans_button_layout.addStretch()
        layout.addLayout(trans_button_layout)

        # Transactions Table
        trans_table_group = QGroupBox("Cash Book Transactions")
        trans_table_layout = QVBoxLayout(trans_table_group)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Type", "Description", "Amount", "Bank Account", "Reference", "Actions"
        ])
        
        # Style table
        header = self.transactions_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.transactions_table.verticalHeader().setDefaultSectionSize(40)
        trans_table_layout.addWidget(self.transactions_table)
        
        layout.addWidget(trans_table_group)
        layout.addStretch()

        return tab

    def _create_reconciliation_tab(self):
        """Create bank reconciliation tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Reconciliation Group
        recon_group = QGroupBox("Bank Reconciliation")
        recon_layout = QGridLayout(recon_group)
        recon_layout.setSpacing(10)

        # Statement Date
        recon_layout.addWidget(QLabel("Statement Date:"), 0, 0)
        self.statement_date = QDateEdit()
        self.statement_date.setDate(QDate.currentDate())
        self.statement_date.setCalendarPopup(True)
        recon_layout.addWidget(self.statement_date, 0, 1)

        # Statement Balance
        recon_layout.addWidget(QLabel("Statement Balance:"), 1, 0)
        self.statement_balance = QDoubleSpinBox()
        self.statement_balance.setRange(0, 999999999)
        self.statement_balance.setDecimals(2)
        self.statement_balance.setPrefix("R ")
        self.statement_balance.setSingleStep(100.00)
        recon_layout.addWidget(self.statement_balance, 1, 1)

        # Book Balance
        recon_layout.addWidget(QLabel("Book Balance:"), 2, 0)
        self.book_balance_label = QLabel("R 0.00")
        self.book_balance_label.setStyleSheet("font-weight: bold; color: #00B050;")
        recon_layout.addWidget(self.book_balance_label, 2, 1)

        # Difference
        recon_layout.addWidget(QLabel("Difference:"), 3, 0)
        self.difference_label = QLabel("R 0.00")
        self.difference_label.setStyleSheet("font-weight: bold; color: #E07B00;")
        recon_layout.addWidget(self.difference_label, 3, 1)

        layout.addWidget(recon_group)

        # Reconciliation Buttons
        recon_button_layout = QHBoxLayout()
        self.calculate_reconciliation_btn = QPushButton("Calculate Reconciliation")
        self.calculate_reconciliation_btn.clicked.connect(self._calculate_reconciliation)
        self.calculate_reconciliation_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B0F0;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0090E0;
            }
        """)
        
        self.post_reconciliation_btn = QPushButton("Post Reconciliation")
        self.post_reconciliation_btn.clicked.connect(self._post_reconciliation)
        self.post_reconciliation_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B050;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #00A040;
            }
        """)
        
        recon_button_layout.addWidget(self.calculate_reconciliation_btn)
        recon_button_layout.addWidget(self.post_reconciliation_btn)
        recon_button_layout.addStretch()
        layout.addLayout(recon_button_layout)

        layout.addStretch()

        return tab

    def _on_bank_account_changed(self):
        """Handle bank account change"""
        pass

    def _on_transaction_type_changed(self):
        """Handle transaction type change"""
        pass

    def _post_opening_balance(self):
        """Post opening balance - CB-001: Opening bank balance entry"""
        try:
            bank_account = self.bank_account_combo.currentText()
            balance_date = self.opening_balance_date.date().toString("yyyy-MM-dd")
            balance_amount = self.opening_balance_amount.value()
            reference = self.opening_balance_reference.text().strip()
            notes = self.opening_balance_notes.toPlainText().strip()
            
            if balance_amount <= 0:
                QMessageBox.warning(self, "Validation Error", "Opening balance amount must be greater than 0")
                return
            
            # Extract account code
            account_code = bank_account.split(" - ")[0]
            
            # Post to ledger using CCE cumulative update
            if self.ledger:
                # Create journal entry for opening balance
                lines = [
                    {
                        "account_code": account_code,
                        "debit": balance_amount,
                        "credit": 0,
                        "notes": f"Opening balance - {notes}"
                    }
                ]
                
                # Post to general ledger
                journal_code = self.ledger.post_journal_entry(
                    date_str=balance_date,
                    reference=reference or "OB",
                    description="Opening Balance",
                    lines=lines,
                    auto_balance=True
                )
                
                # Apply CCE cumulative update
                self.ledger.update_cce(balance_amount, "opening_balance")
                
                # Store cash book record
                cash_record = {
                    "type": "opening_balance",
                    "date": balance_date,
                    "bank_account": bank_account,
                    "amount": balance_amount,
                    "reference": reference,
                    "notes": notes,
                    "journal_code": journal_code,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.cash_book_data.append(cash_record)
                self._save_cashbook_data()
                self._refresh_opening_balances_table()
                
                # Clear form
                self._clear_opening_balance_form()
                
                # Request dashboard refresh
                self.dashboard_refresh_requested.emit()
                
                QMessageBox.information(self, "Success", 
                                      f"Opening balance of {_fmt_amount(balance_amount)} posted successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to post opening balance: {str(e)}")

    def _post_transaction(self):
        """Post cash book transaction"""
        try:
            trans_type = self.transaction_type_combo.currentText()
            trans_date = self.transaction_date.date().toString("yyyy-MM-dd")
            description = self.transaction_description.text().strip()
            amount = self.transaction_amount.value()
            bank_account = self.transaction_bank_combo.currentText()
            reference = self.transaction_reference.text().strip()
            
            if amount <= 0:
                QMessageBox.warning(self, "Validation Error", "Transaction amount must be greater than 0")
                return
            
            if not description:
                QMessageBox.warning(self, "Validation Error", "Transaction description is required")
                return
            
            # Extract account code
            account_code = bank_account.split(" - ")[0]
            
            # Determine debit/credit based on transaction type
            if trans_type in ["Receipt", "Bank Transfer In"]:
                debit_amount = amount
                credit_amount = 0
            else:
                debit_amount = 0
                credit_amount = amount
            
            # Post to ledger using CCE cumulative update
            if self.ledger:
                # Create journal entry
                lines = [
                    {
                        "account_code": account_code,
                        "debit": debit_amount,
                        "credit": credit_amount,
                        "notes": f"{trans_type} - {description}"
                    }
                ]
                
                # Post to general ledger
                journal_code = self.ledger.post_journal_entry(
                    date_str=trans_date,
                    reference=reference or "CB",
                    description=f"{trans_type}: {description}",
                    lines=lines,
                    auto_balance=True
                )
                
                # Apply CCE cumulative update (negative for payments)
                cce_amount = amount if trans_type in ["Receipt", "Bank Transfer In"] else -amount
                self.ledger.update_cce(cce_amount, f"cash_book_{trans_type.lower()}")
                
                # Store cash book record
                cash_record = {
                    "type": "transaction",
                    "transaction_type": trans_type,
                    "date": trans_date,
                    "description": description,
                    "amount": amount,
                    "bank_account": bank_account,
                    "reference": reference,
                    "journal_code": journal_code,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.cash_book_data.append(cash_record)
                self._save_cashbook_data()
                self._refresh_transactions_table()
                
                # Clear form
                self._clear_transaction_form()
                
                # Request dashboard refresh
                self.dashboard_refresh_requested.emit()
                
                QMessageBox.information(self, "Success", 
                                      "Transaction posted successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to post transaction: {str(e)}")

    def _calculate_reconciliation(self):
        """Calculate bank reconciliation"""
        try:
            statement_balance = self.statement_balance.value()
            
            # Calculate book balance from transactions
            book_balance = 0.0
            for record in self.cash_book_data:
                if record["type"] == "opening_balance":
                    book_balance += record["amount"]
                elif record["type"] == "transaction":
                    trans_type = record.get("transaction_type", "")
                    if trans_type in ["Receipt", "Bank Transfer In"]:
                        book_balance += record["amount"]
                    else:
                        book_balance -= record["amount"]
            
            # Update labels
            self.book_balance_label.setText(_fmt_amount(book_balance))
            difference = statement_balance - book_balance
            self.difference_label.setText(_fmt_amount(difference))
            
            # Color code: difference
            if abs(difference) < 0.01:  # Within 1 cent
                self.difference_label.setStyleSheet("font-weight: bold; color: #00B050;")
            else:
                self.difference_label.setStyleSheet("font-weight: bold; color: #E07B00;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate reconciliation: {str(e)}")

    def _post_reconciliation(self):
        """Post bank reconciliation"""
        try:
            statement_date = self.statement_date.date().toString("yyyy-MM-dd")
            statement_balance = self.statement_balance.value()
            
            # Create reconciliation record
            recon_record = {
                "type": "reconciliation",
                "date": statement_date,
                "statement_balance": statement_balance,
                "book_balance": float(self.book_balance_label.text().replace("R ", "").replace(",", "")),
                "difference": float(self.difference_label.text().replace("R ", "").replace(",", "")),
                "timestamp": datetime.now().isoformat()
            }
            
            self.cash_book_data.append(recon_record)
            self._save_cashbook_data()
            
            QMessageBox.information(self, "Success", "Bank reconciliation posted successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to post reconciliation: {str(e)}")

    def _clear_opening_balance_form(self):
        """Clear opening balance form"""
        self.opening_balance_amount.setValue(0)
        self.opening_balance_reference.clear()
        self.opening_balance_notes.clear()

    def _clear_transaction_form(self):
        """Clear transaction form"""
        self.transaction_description.clear()
        self.transaction_amount.setValue(0)
        self.transaction_reference.clear()

    def _refresh_opening_balances_table(self):
        """Refresh opening balances table"""
        opening_balances = [r for r in self.cash_book_data if r["type"] == "opening_balance"]
        self.opening_balances_table.setRowCount(len(opening_balances))
        
        for row, record in enumerate(opening_balances):
            self.opening_balances_table.setItem(row, 0, QTableWidgetItem(record["bank_account"]))
            self.opening_balances_table.setItem(row, 1, QTableWidgetItem(record["date"]))
            self.opening_balances_table.setItem(row, 2, QTableWidgetItem(_fmt_amount(record["amount"])))
            self.opening_balances_table.setItem(row, 3, QTableWidgetItem(record.get("reference", "")))
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_opening_balance(r))
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: #00B0F0;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #0090E0;
                }
            """)
            self.opening_balances_table.setCellWidget(row, 4, action_btn)

    def _refresh_transactions_table(self):
        """Refresh transactions table"""
        transactions = [r for r in self.cash_book_data if r["type"] == "transaction"]
        self.transactions_table.setRowCount(len(transactions))
        
        for row, record in enumerate(transactions):
            self.transactions_table.setItem(row, 0, QTableWidgetItem(record["date"]))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(record["transaction_type"]))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(record["description"]))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(record["amount"])))
            self.transactions_table.setItem(row, 4, QTableWidgetItem(record["bank_account"]))
            self.transactions_table.setItem(row, 5, QTableWidgetItem(record.get("reference", "")))
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_transaction(r))
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: #00B0F0;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #0090E0;
                }
            """)
            self.transactions_table.setCellWidget(row, 6, action_btn)

    def _select_opening_balance(self, row):
        """Select opening balance row"""
        self.opening_balances_table.selectRow(row)

    def _select_transaction(self, row):
        """Select transaction row"""
        self.transactions_table.selectRow(row)

    def _save_cashbook_data(self):
        """Save cash book data to file"""
        try:
            with open(self.cashbook_file, 'w') as f:
                json.dump(self.cash_book_data, f, indent=2)
        except Exception as e:
            print(f"Error saving cash book data: {e}")

    def _load_cashbook_data(self):
        """Load cash book data from file"""
        try:
            if self.cashbook_file.exists():
                with open(self.cashbook_file, 'r') as f:
                    self.cash_book_data = json.load(f)
        except Exception as e:
            print(f"Error loading cash book data: {e}")
            self.cash_book_data = []

    def get_cash_book_data(self):
        """Get cash book data"""
        return self.cash_book_data.copy()

    def get_bank_balance(self, bank_account_code: str = "1000") -> float:
        """Get current bank balance"""
        balance = 0.0
        for record in self.cash_book_data:
            if record["type"] == "opening_balance" and record["bank_account"].startswith(bank_account_code):
                balance += record["amount"]
            elif record["type"] == "transaction" and record["bank_account"].startswith(bank_account_code):
                trans_type = record.get("transaction_type", "")
                if trans_type in ["Receipt", "Bank Transfer In"]:
                    balance += record["amount"]
                else:
                    balance -= record["amount"]
        return balance
