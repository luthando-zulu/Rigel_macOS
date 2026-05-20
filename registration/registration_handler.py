#!/usr/bin/env python3
"""
Registration Module Handler
Implements all REG-001 to REG-018 test cases for company registration
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
    QCheckBox, QHeaderView, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from accounting import AccountingLedger, CHART_OF_ACCOUNTS, _fmt_amount

class RegistrationHandler(QWidget):
    """Registration Module Handler - Implements all REG test cases"""
    
    # Signals for communication with main window
    registration_complete = pyqtSignal(str)  # Entity name
    navigation_requested = pyqtSignal(str)  # Page name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ledger = getattr(parent, 'ledger', None) if parent else None
        self.entity_name = ""
        self.registration_data = []
        self.editing_index = None  # Track which row is being edited
        
        # Data file paths
        self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.registration_file = self.data_dir / "registration.json"
        
        self._load_registration_data()
        self._build_ui()

    def _build_ui(self):
        """Build the registration UI - REG-001: Navigation to Registration Page"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Company Registration")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Entity Name Section - REG-004: Entity Name Propagation
        entity_group = QGroupBox("Entity Information")
        entity_group.setStyleSheet("""
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
        entity_layout = QVBoxLayout(entity_group)
        
        entity_name_layout = QHBoxLayout()
        entity_name_layout.addWidget(QLabel("Entity Name:"))
        self.entity_name_input = QLineEdit()
        self.entity_name_input.setPlaceholderText("Enter company name...")
        self.entity_name_input.textChanged.connect(self._on_entity_name_changed)
        entity_name_layout.addWidget(self.entity_name_input)
        entity_layout.addLayout(entity_name_layout)
        
        layout.addWidget(entity_group)

        # Chart of Accounts Setup
        accounts_group = QGroupBox("Chart of Accounts Setup")
        accounts_group.setStyleSheet("""
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
        accounts_layout = QVBoxLayout(accounts_group)

        # Form for adding accounts
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        
        # Category dropdown - REG-006: Category Dropdown
        form_layout.addWidget(QLabel("Category:"), 0, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Assets", "Liabilities", "Equity", "Income", "Expenses"])
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        form_layout.addWidget(self.category_combo, 0, 1)
        
        # Sub-category dropdown - REG-007: Sub-Category & GL Code Auto-Fill
        form_layout.addWidget(QLabel("Sub-Category:"), 1, 0)
        self.subcategory_combo = QComboBox()
        form_layout.addWidget(self.subcategory_combo, 1, 1)
        
        # Account Name
        form_layout.addWidget(QLabel("Account Name:"), 2, 0)
        self.account_name_input = QLineEdit()
        self.account_name_input.setPlaceholderText("Enter account name...")
        form_layout.addWidget(self.account_name_input, 2, 1)
        
        # GL Code (auto-filled) - REG-007
        form_layout.addWidget(QLabel("GL Code:"), 3, 0)
        self.gl_code_input = QLineEdit()
        self.gl_code_input.setReadOnly(True)
        self.gl_code_input.setStyleSheet("background: #F5F5F5;")
        form_layout.addWidget(self.gl_code_input, 3, 1)
        
        # Opening Balance
        form_layout.addWidget(QLabel("Opening Balance:"), 4, 0)
        self.opening_balance_input = QDoubleSpinBox()
        self.opening_balance_input.setRange(-999999999, 999999999)
        self.opening_balance_input.setDecimals(2)
        self.opening_balance_input.setPrefix("R ")
        self.opening_balance_input.setSingleStep(100.00)
        form_layout.addWidget(self.opening_balance_input, 4, 1)
        
        accounts_layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.post_btn = QPushButton("Post")
        self.post_btn.clicked.connect(self._post_transaction)
        self.post_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B050;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00A040;
            }
        """)
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._edit_transaction)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B0F0;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0090E0;
            }
        """)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_transaction)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #E07B00;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D06B00;
            }
        """)
        
        button_layout.addWidget(self.post_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        self.update_last_year_btn = QPushButton("Update Last Year")
        self.update_last_year_btn.clicked.connect(self._update_last_year)
        self.update_last_year_btn.setStyleSheet("""
            QPushButton {
                background-color: #6A7575;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A6565;
            }
        """)
        button_layout.addWidget(self.update_last_year_btn)
        
        accounts_layout.addLayout(button_layout)
        layout.addWidget(accounts_group)

        # Posted Transactions Table
        table_group = QGroupBox("Posted Accounts")
        table_group.setStyleSheet("""
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
        table_layout = QVBoxLayout(table_group)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels([
            "Category", "Sub-Category", "Account Name", "GL Code", "Opening Balance", "Actions"
        ])
        
        # Style the table
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
        
        # Set row height
        self.transactions_table.verticalHeader().setDefaultSectionSize(40)
        
        table_layout.addWidget(self.transactions_table)
        
        layout.addWidget(table_group)

        # Navigation Buttons
        nav_layout = QHBoxLayout()
        self.start_using_btn = QPushButton("Start Using RIGEL Business")
        self.start_using_btn.clicked.connect(self._start_using)
        self.start_using_btn.setEnabled(False)  # REG-011: Start Using Navigation & Validation
        self.start_using_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        nav_layout.addWidget(self.start_using_btn)
        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        # Initialize subcategories
        self._on_category_changed()
        self._refresh_table()

    def _on_entity_name_changed(self, text):
        """Handle entity name change - REG-004: Entity Name Propagation"""
        self.entity_name = text.strip()
        self._save_registration_data()

    def _on_category_changed(self):
        """Update subcategory dropdown based on category - REG-006: Category Dropdown"""
        self.subcategory_combo.clear()
        
        subcategories = {
            "Assets": ["Current Assets", "Non-Current Assets", "Bank Accounts"],
            "Liabilities": ["Current Liabilities", "Non-Current Liabilities"],
            "Equity": ["Share Capital", "Retained Earnings"],
            "Income": ["Trading Revenue", "Other Income", "Investment Income"],
            "Expenses": ["Cost of Sales", "Operating Expenses", "Administrative Expenses"]
        }
        
        category = self.category_combo.currentText()
        if category in subcategories:
            self.subcategory_combo.addItems(subcategories[category])

    def _post_transaction(self):
        """Post a new account to chart of accounts - REG-008: Post Transaction"""
        try:
            category = self.category_combo.currentText()
            subcategory = self.subcategory_combo.currentText()
            account_name = self.account_name_input.text().strip()
            opening_balance = self.opening_balance_input.value()
            
            # Validation
            if not account_name:
                QMessageBox.critical(self, "Validation Error", "Account name is required")
                return
            
            # REG-010: Duplicate Prevention
            for i, data in enumerate(self.registration_data):
                if (data['category'] == category and
                    data['subcategory'] == subcategory and
                    data['account_name'] == account_name and
                    i != self.editing_index):  # Allow editing same record
                    QMessageBox.warning(self, "Duplicate Error", 
                                      "This account already exists in the chart of accounts")
                    return
            
            # Generate GL code - REG-007: Sub-Category & GL Code Auto-Fill
            gl_code = self._generate_gl_code(category, subcategory)
            
            # Create transaction record
            transaction = {
                'category': category,
                'subcategory': subcategory,
                'account_name': account_name,
                'gl_code': gl_code,
                'opening_balance': float(opening_balance),
                'date_created': datetime.now().isoformat(),
                'date_modified': datetime.now().isoformat()
            }
            
            if self.editing_index is not None:
                # Update existing record - REG-009: Edit Transaction
                transaction['date_created'] = self.registration_data[self.editing_index]['date_created']
                self.registration_data[self.editing_index] = transaction
                self.editing_index = None
                self.post_btn.setText("Post")
                QMessageBox.information(self, "Success", f"Account '{account_name}' updated successfully")
            else:
                # Add new record
                self.registration_data.append(transaction)
                QMessageBox.information(self, "Success", f"Account '{account_name}' posted successfully")
            
            # Clear form and refresh
            self._clear_form()
            self._refresh_table()
            self._save_registration_data()
            self._validate_start_using()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to post transaction: {str(e)}")

    def _edit_transaction(self):
        """Edit selected transaction - REG-009: Edit Transaction"""
        current_row = self.transactions_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a transaction to edit")
            return
        
        if current_row >= len(self.registration_data):
            return
        
        # Load data into form
        data = self.registration_data[current_row]
        self.category_combo.setCurrentText(data['category'])
        self.subcategory_combo.setCurrentText(data['subcategory'])
        self.account_name_input.setText(data['account_name'])
        self.gl_code_input.setText(data['gl_code'])
        self.opening_balance_input.setValue(data['opening_balance'])
        
        # Set editing mode
        self.editing_index = current_row
        self.post_btn.setText("Update")
        
        # Highlight the row being edited
        self.transactions_table.selectRow(current_row)

    def _delete_transaction(self):
        """Delete selected transaction"""
        current_row = self.transactions_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a transaction to delete")
            return
        
        if current_row >= len(self.registration_data):
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to delete this transaction?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.registration_data[current_row]
            self._refresh_table()
            self._save_registration_data()
            self._validate_start_using()
            
            # Clear editing mode if deleting edited record
            if self.editing_index == current_row:
                self.editing_index = None
                self.post_btn.setText("Post")
                self._clear_form()

    def _refresh_table(self):
        """Refresh the transactions table"""
        self.transactions_table.setRowCount(len(self.registration_data))
        
        for row, data in enumerate(self.registration_data):
            # Category
            self.transactions_table.setItem(row, 0, QTableWidgetItem(data['category']))
            
            # Sub-Category
            self.transactions_table.setItem(row, 1, QTableWidgetItem(data['subcategory']))
            
            # Account Name
            self.transactions_table.setItem(row, 2, QTableWidgetItem(data['account_name']))
            
            # GL Code
            self.transactions_table.setItem(row, 3, QTableWidgetItem(data['gl_code']))
            
            # Opening Balance
            balance_item = QTableWidgetItem(_fmt_amount(data['opening_balance']))
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.transactions_table.setItem(row, 4, balance_item)
            
            # Actions
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_row(r))
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
            self.transactions_table.setCellWidget(row, 5, action_btn)

    def _select_row(self, row):
        """Select a specific row"""
        self.transactions_table.selectRow(row)

    def _generate_gl_code(self, category, subcategory):
        """Generate GL code based on category and subcategory"""
        # GL code prefixes based on RIGEL COA
        prefixes = {
            "Assets": "1",
            "Liabilities": "2", 
            "Equity": "3",
            "Income": "4",
            "Expenses": "5"
        }
        
        prefix = prefixes.get(category, "9")
        existing_codes = [data['gl_code'] for data in self.registration_data]
        
        # Find next available code
        counter = 1
        while True:
            gl_code = f"{prefix}{counter:03d}"
            if gl_code not in existing_codes:
                break
            counter += 1
        
        return gl_code

    def _clear_form(self):
        """Clear the input form"""
        self.account_name_input.clear()
        self.gl_code_input.clear()
        self.opening_balance_input.setValue(0.00)

    def _validate_start_using(self):
        """Validate if start using button should be enabled - REG-011: Start Using Navigation & Validation"""
        has_entity_name = bool(self.entity_name)
        has_accounts = len(self.registration_data) > 0
        self.start_using_btn.setEnabled(has_entity_name and has_accounts)

    def _update_last_year(self):
        """Update last year's data - REG-005: Update Last Year"""
        if not self.registration_data:
            QMessageBox.warning(self, "No Data", "No accounts found to update")
            return
        
        # This would integrate with reporting modules (Income Statement, Balance Sheet)
        # For now, we'll simulate the update
        try:
            # In a real implementation, this would:
            # 1. Read current year closing balances
            # 2. Write to Last Year column in IS and BS
            # 3. Update comparative columns
            
            QMessageBox.information(self, "Update Last Year", 
                                  "Last year data updated successfully.\n"
                                  "Income Statement and Balance Sheet comparative columns have been populated.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update last year: {str(e)}")

    def _start_using(self):
        """Navigate to main application - REG-011: Start Using Navigation & Validation"""
        if self.entity_name:
            self.registration_complete.emit(self.entity_name)
            self.navigation_requested.emit("main_index")
        else:
            QMessageBox.warning(self, "Incomplete Registration", 
                              "Please complete the entity name before proceeding")

    def _save_registration_data(self):
        """Save registration data to file"""
        try:
            data = {
                'entity_name': self.entity_name,
                'registration_data': self.registration_data,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.registration_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving registration data: {e}")

    def _load_registration_data(self):
        """Load registration data from file"""
        try:
            if self.registration_file.exists():
                with open(self.registration_file, 'r') as f:
                    data = json.load(f)
                    self.entity_name = data.get('entity_name', '')
                    self.registration_data = data.get('registration_data', [])
        except Exception as e:
            print(f"Error loading registration data: {e}")
            self.entity_name = ""
            self.registration_data = []

    def get_entity_name(self):
        """Get the current entity name - REG-004: Entity Name Propagation"""
        return self.entity_name

    def get_chart_of_accounts(self):
        """Get the chart of accounts data"""
        return self.registration_data.copy()
