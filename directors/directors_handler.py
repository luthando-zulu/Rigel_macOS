#!/usr/bin/env python3
"""
Directors Module Handler
Implements DIR-001 to DIR-017 test cases for director management functionality
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
    QCheckBox, QHeaderView, QFrame, QScrollArea, QTabWidget,
    QSpinBox, QFormLayout, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from accounting import AccountingLedger, CHART_OF_ACCOUNTS, _fmt_amount

class DirectorsHandler(QWidget):
    """Directors Module Handler - Implements DIR-001 to DIR-017"""
    
    # Signals for communication with main window
    dashboard_refresh_requested = pyqtSignal()
    navigation_requested = pyqtSignal(str)  # Page name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ledger = getattr(parent, 'ledger', None) if parent else None
        self.directors_data = []
        self.loans_data = []
        self.expenses_data = []
        self.editing_index = None
        
        # Data file paths
        self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.directors_file = self.data_dir / "directors.json"
        self.director_loans_file = self.data_dir / "director_loans.json"
        self.director_expenses_file = self.data_dir / "director_expenses.json"
        
        self._load_data()
        self._build_ui()

    def _build_ui(self):
        """Build directors UI - DIR-001: Navigation to Directors"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Director Management")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Create tabbed interface
        tab_widget = QTabWidget()
        
        # Directors Masterfile Tab
        directors_tab = self._create_directors_tab()
        tab_widget.addTab(directors_tab, "Directors")
        
        # Loans to Directors Tab
        loans_tab = self._create_loans_tab()
        tab_widget.addTab(loans_tab, "Loans to Directors")
        
        # Director Expenses Tab
        expenses_tab = self._create_expenses_tab()
        tab_widget.addTab(expenses_tab, "Director Expenses")
        
        # Reports Tab
        reports_tab = self._create_reports_tab()
        tab_widget.addTab(reports_tab, "Reports")
        
        layout.addWidget(tab_widget)

    def _create_directors_tab(self):
        """Create directors masterfile tab - DIR-001 to DIR-010"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Director Entry Group
        director_group = QGroupBox("Director Information")
        director_group.setStyleSheet("""
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
        director_layout = QGridLayout(director_group)
        director_layout.setSpacing(10)

        # Director Code (auto-generated)
        director_layout.addWidget(QLabel("Director Code:"), 0, 0)
        self.director_code_input = QLineEdit()
        self.director_code_input.setReadOnly(True)
        self.director_code_input.setStyleSheet("background: #F5F5F5;")
        director_layout.addWidget(self.director_code_input, 0, 1)

        # Director Name
        director_layout.addWidget(QLabel("Director Name:"), 1, 0)
        self.director_name_input = QLineEdit()
        self.director_name_input.setPlaceholderText("Enter director name...")
        director_layout.addWidget(self.director_name_input, 1, 1)

        # ID Number
        director_layout.addWidget(QLabel("ID Number:"), 2, 0)
        self.id_number_input = QLineEdit()
        self.id_number_input.setPlaceholderText("Enter ID number...")
        director_layout.addWidget(self.id_number_input, 2, 1)

        # Position
        director_layout.addWidget(QLabel("Position:"), 3, 0)
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            "Chairperson", "Managing Director", "Financial Director", 
            "Non-Executive Director", "Executive Director", "Company Secretary"
        ])
        director_layout.addWidget(self.position_combo, 3, 1)

        # Appointment Date
        director_layout.addWidget(QLabel("Appointment Date:"), 4, 0)
        self.appointment_date = QDateEdit()
        self.appointment_date.setDate(QDate.currentDate())
        self.appointment_date.setCalendarPopup(True)
        director_layout.addWidget(self.appointment_date, 4, 1)

        # Contact Number
        director_layout.addWidget(QLabel("Contact Number:"), 5, 0)
        self.contact_number_input = QLineEdit()
        self.contact_number_input.setPlaceholderText("Enter contact number...")
        director_layout.addWidget(self.contact_number_input, 5, 1)

        # Email Address
        director_layout.addWidget(QLabel("Email Address:"), 6, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address...")
        director_layout.addWidget(self.email_input, 6, 1)

        # Physical Address
        director_layout.addWidget(QLabel("Physical Address:"), 7, 0)
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        self.address_input.setPlaceholderText("Enter physical address...")
        director_layout.addWidget(self.address_input, 7, 1)

        # Shareholding
        director_layout.addWidget(QLabel("Shareholding (%):"), 8, 0)
        self.shareholding_input = QDoubleSpinBox()
        self.shareholding_input.setRange(0, 100)
        self.shareholding_input.setDecimals(2)
        self.shareholding_input.setSuffix(" %")
        director_layout.addWidget(self.shareholding_input, 8, 1)

        # Active Status
        director_layout.addWidget(QLabel("Status:"), 9, 0)
        self.active_checkbox = QCheckBox("Active Director")
        self.active_checkbox.setChecked(True)
        director_layout.addWidget(self.active_checkbox, 9, 1)

        layout.addWidget(director_group)

        # Director Buttons
        director_button_layout = QHBoxLayout()
        self.add_director_btn = QPushButton("Add Director")
        self.add_director_btn.clicked.connect(self._add_director)
        self.add_director_btn.setStyleSheet("""
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
        
        self.edit_director_btn = QPushButton("Edit Director")
        self.edit_director_btn.clicked.connect(self._edit_director)
        self.edit_director_btn.setStyleSheet("""
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
        
        self.delete_director_btn = QPushButton("Delete Director")
        self.delete_director_btn.clicked.connect(self._delete_director)
        self.delete_director_btn.setStyleSheet("""
            QPushButton {
                background-color: #E07B00;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #D06B00;
            }
        """)
        
        self.clear_director_btn = QPushButton("Clear Form")
        self.clear_director_btn.clicked.connect(self._clear_director_form)
        self.clear_director_btn.setStyleSheet("""
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
        
        director_button_layout.addWidget(self.add_director_btn)
        director_button_layout.addWidget(self.edit_director_btn)
        director_button_layout.addWidget(self.delete_director_btn)
        director_button_layout.addWidget(self.clear_director_btn)
        director_button_layout.addStretch()
        layout.addLayout(director_button_layout)

        # Directors Table
        directors_table_group = QGroupBox("Directors Masterfile")
        directors_table_layout = QVBoxLayout(directors_table_group)
        
        self.directors_table = QTableWidget()
        self.directors_table.setColumnCount(7)
        self.directors_table.setHorizontalHeaderLabels([
            "Code", "Name", "Position", "Appointment Date", "Shareholding", "Status", "Actions"
        ])
        
        # Style table
        header = self.directors_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.directors_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.directors_table.verticalHeader().setDefaultSectionSize(40)
        directors_table_layout.addWidget(self.directors_table)
        
        layout.addWidget(directors_table_group)
        layout.addStretch()

        # Generate initial director code
        self._generate_director_code()

        return tab

    def _create_loans_tab(self):
        """Create loans to directors tab - DIR-011 to DIR-015"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Loan Entry Group
        loan_group = QGroupBox("Loan to Director")
        loan_layout = QGridLayout(loan_group)
        loan_layout.setSpacing(10)

        # Director Selection
        loan_layout.addWidget(QLabel("Director:"), 0, 0)
        self.loan_director_combo = QComboBox()
        self._populate_loan_director_combo()
        loan_layout.addWidget(self.loan_director_combo, 0, 1)

        # Loan Number (auto-generated)
        loan_layout.addWidget(QLabel("Loan Number:"), 1, 0)
        self.loan_number_input = QLineEdit()
        self.loan_number_input.setReadOnly(True)
        self.loan_number_input.setStyleSheet("background: #F5F5F5;")
        loan_layout.addWidget(self.loan_number_input, 1, 1)

        # Loan Date
        loan_layout.addWidget(QLabel("Loan Date:"), 2, 0)
        self.loan_date = QDateEdit()
        self.loan_date.setDate(QDate.currentDate())
        self.loan_date.setCalendarPopup(True)
        loan_layout.addWidget(self.loan_date, 2, 1)

        # Loan Amount
        loan_layout.addWidget(QLabel("Loan Amount:"), 3, 0)
        self.loan_amount = QDoubleSpinBox()
        self.loan_amount.setRange(0, 999999999)
        self.loan_amount.setDecimals(2)
        self.loan_amount.setPrefix("R ")
        self.loan_amount.setSingleStep(1000.00)
        loan_layout.addWidget(self.loan_amount, 3, 1)

        # Interest Rate
        loan_layout.addWidget(QLabel("Interest Rate (%):"), 4, 0)
        self.interest_rate = QDoubleSpinBox()
        self.interest_rate.setRange(0, 50)
        self.interest_rate.setDecimals(2)
        self.interest_rate.setSuffix(" %")
        self.interest_rate.setValue(8.0)  # Default 8%
        loan_layout.addWidget(self.interest_rate, 4, 1)

        # Loan Term (months)
        loan_layout.addWidget(QLabel("Loan Term (months):"), 5, 0)
        self.loan_term = QSpinBox()
        self.loan_term.setRange(1, 360)
        self.loan_term.setValue(60)  # Default 5 years
        loan_layout.addWidget(self.loan_term, 5, 1)

        # Repayment Method
        loan_layout.addWidget(QLabel("Repayment Method:"), 6, 0)
        self.repayment_method_combo = QComboBox()
        self.repayment_method_combo.addItems([
            "Monthly Installments", "Quarterly Installments", "Annual Installments", "Lump Sum"
        ])
        loan_layout.addWidget(self.repayment_method_combo, 6, 1)

        # Purpose
        loan_layout.addWidget(QLabel("Purpose:"), 7, 0)
        self.loan_purpose = QLineEdit()
        self.loan_purpose.setPlaceholderText("Enter loan purpose...")
        loan_layout.addWidget(self.loan_purpose, 7, 1)

        layout.addWidget(loan_group)

        # Loan Buttons
        loan_button_layout = QHBoxLayout()
        self.create_loan_btn = QPushButton("Create Loan")
        self.create_loan_btn.clicked.connect(self._create_loan)
        self.create_loan_btn.setStyleSheet("""
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
        
        self.clear_loan_btn = QPushButton("Clear Form")
        self.clear_loan_btn.clicked.connect(self._clear_loan_form)
        self.clear_loan_btn.setStyleSheet("""
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
        
        loan_button_layout.addWidget(self.create_loan_btn)
        loan_button_layout.addWidget(self.clear_loan_btn)
        loan_button_layout.addStretch()
        layout.addLayout(loan_button_layout)

        # Loans Table
        loans_table_group = QGroupBox("Loans to Directors")
        loans_table_layout = QVBoxLayout(loans_table_group)
        
        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(8)
        self.loans_table.setHorizontalHeaderLabels([
            "Loan No", "Director", "Date", "Amount", "Interest Rate", "Term", "Balance", "Actions"
        ])
        
        # Style table
        header = self.loans_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.loans_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.loans_table.verticalHeader().setDefaultSectionSize(40)
        loans_table_layout.addWidget(self.loans_table)
        
        layout.addWidget(loans_table_group)
        layout.addStretch()

        # Generate initial loan number
        self._generate_loan_number()

        return tab

    def _create_expenses_tab(self):
        """Create director expenses tab - DIR-016"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Expense Entry Group
        expense_group = QGroupBox("Director Expense")
        expense_layout = QGridLayout(expense_group)
        expense_layout.setSpacing(10)

        # Director Selection
        expense_layout.addWidget(QLabel("Director:"), 0, 0)
        self.expense_director_combo = QComboBox()
        self._populate_expense_director_combo()
        expense_layout.addWidget(self.expense_director_combo, 0, 1)

        # Expense Date
        expense_layout.addWidget(QLabel("Expense Date:"), 1, 0)
        self.expense_date = QDateEdit()
        self.expense_date.setDate(QDate.currentDate())
        self.expense_date.setCalendarPopup(True)
        expense_layout.addWidget(self.expense_date, 1, 1)

        # Expense Category
        expense_layout.addWidget(QLabel("Expense Category:"), 2, 0)
        self.expense_category_combo = QComboBox()
        self.expense_category_combo.addItems([
            "Travel", "Entertainment", "Training", "Office Supplies", 
            "Communication", "Professional Fees", "Other"
        ])
        expense_layout.addWidget(self.expense_category_combo, 2, 1)

        # Expense Amount
        expense_layout.addWidget(QLabel("Expense Amount:"), 3, 0)
        self.expense_amount = QDoubleSpinBox()
        self.expense_amount.setRange(0, 999999999)
        self.expense_amount.setDecimals(2)
        self.expense_amount.setPrefix("R ")
        self.expense_amount.setSingleStep(100.00)
        expense_layout.addWidget(self.expense_amount, 3, 1)

        # Description
        expense_layout.addWidget(QLabel("Description:"), 4, 0)
        self.expense_description = QLineEdit()
        self.expense_description.setPlaceholderText("Enter expense description...")
        expense_layout.addWidget(self.expense_description, 4, 1)

        # Receipt/Invoice Number
        expense_layout.addWidget(QLabel("Receipt/Invoice:"), 5, 0)
        self.receipt_number = QLineEdit()
        self.receipt_number.setPlaceholderText("Enter receipt or invoice number...")
        expense_layout.addWidget(self.receipt_number, 5, 1)

        layout.addWidget(expense_group)

        # Expense Buttons
        expense_button_layout = QHBoxLayout()
        self.add_expense_btn = QPushButton("Add Expense")
        self.add_expense_btn.clicked.connect(self._add_expense)
        self.add_expense_btn.setStyleSheet("""
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
        
        self.clear_expense_btn = QPushButton("Clear Form")
        self.clear_expense_btn.clicked.connect(self._clear_expense_form)
        self.clear_expense_btn.setStyleSheet("""
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
        
        expense_button_layout.addWidget(self.add_expense_btn)
        expense_button_layout.addWidget(self.clear_expense_btn)
        expense_button_layout.addStretch()
        layout.addLayout(expense_button_layout)

        # Expenses Table
        expenses_table_group = QGroupBox("Director Expenses")
        expenses_table_layout = QVBoxLayout(expenses_table_group)
        
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(6)
        self.expenses_table.setHorizontalHeaderLabels([
            "Date", "Director", "Category", "Amount", "Description", "Receipt"
        ])
        
        # Style table
        header = self.expenses_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.expenses_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.expenses_table.verticalHeader().setDefaultSectionSize(40)
        expenses_table_layout.addWidget(self.expenses_table)
        
        layout.addWidget(expenses_table_group)
        layout.addStretch()

        return tab

    def _create_reports_tab(self):
        """Create reports tab - DIR-017"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Report Generation Group
        report_group = QGroupBox("Generate Director Reports")
        report_layout = QGridLayout(report_group)
        report_layout.setSpacing(10)

        # Report Type
        report_layout.addWidget(QLabel("Report Type:"), 0, 0)
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Directors Register", "Loans to Directors Statement", 
            "Director Expense Report", "AFS Note 2 - Loans to Directors"
        ])
        report_layout.addWidget(self.report_type_combo, 0, 1)

        # Report Period
        report_layout.addWidget(QLabel("From Date:"), 1, 0)
        self.report_from_date = QDateEdit()
        self.report_from_date.setDate(QDate.currentDate().addMonths(-12))
        self.report_from_date.setCalendarPopup(True)
        report_layout.addWidget(self.report_from_date, 1, 1)

        report_layout.addWidget(QLabel("To Date:"), 2, 0)
        self.report_to_date = QDateEdit()
        self.report_to_date.setDate(QDate.currentDate())
        self.report_to_date.setCalendarPopup(True)
        report_layout.addWidget(self.report_to_date, 2, 1)

        layout.addWidget(report_group)

        # Report Buttons
        report_button_layout = QHBoxLayout()
        self.generate_report_btn = QPushButton("Generate Report")
        self.generate_report_btn.clicked.connect(self._generate_report)
        self.generate_report_btn.setStyleSheet("""
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
        
        self.print_report_btn = QPushButton("Print Report")
        self.print_report_btn.clicked.connect(self._print_report)
        self.print_report_btn.setStyleSheet("""
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
        
        report_button_layout.addWidget(self.generate_report_btn)
        report_button_layout.addWidget(self.print_report_btn)
        report_button_layout.addStretch()
        layout.addLayout(report_button_layout)

        # Report Preview
        report_preview_group = QGroupBox("Report Preview")
        report_preview_layout = QVBoxLayout(report_preview_group)
        
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        self.report_preview.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                padding: 10px;
                font-family: 'Courier New', monospace;
            }
        """)
        report_preview_layout.addWidget(self.report_preview)
        
        layout.addWidget(report_preview_group)
        layout.addStretch()

        return tab

    def _generate_director_code(self):
        """Generate unique director code"""
        existing_codes = [d["code"] for d in self.directors_data]
        prefix = "DIR"
        counter = 1
        while f"{prefix}{counter:03d}" in existing_codes:
            counter += 1
        self.director_code_input.setText(f"{prefix}{counter:03d}")

    def _generate_loan_number(self):
        """Generate unique loan number"""
        existing_numbers = [l["loan_number"] for l in self.loans_data]
        prefix = "LN"
        counter = 1
        current_year = date.today().year
        while f"{prefix}{current_year}{counter:04d}" in existing_numbers:
            counter += 1
        self.loan_number_input.setText(f"{prefix}{current_year}{counter:04d}")

    def _populate_loan_director_combo(self):
        """Populate director dropdown for loans"""
        self.loan_director_combo.clear()
        for director in self.directors_data:
            if director["active"]:  # Only active directors
                self.loan_director_combo.addItem(f"{director['code']} - {director['name']}")

    def _populate_expense_director_combo(self):
        """Populate director dropdown for expenses"""
        self.expense_director_combo.clear()
        for director in self.directors_data:
            if director["active"]:  # Only active directors
                self.expense_director_combo.addItem(f"{director['code']} - {director['name']}")

    def _add_director(self):
        """Add new director - DIR-002 to DIR-008"""
        try:
            director_code = self.director_code_input.text().strip()
            director_name = self.director_name_input.text().strip()
            id_number = self.id_number_input.text().strip()
            position = self.position_combo.currentText()
            appointment_date = self.appointment_date.date().toString("yyyy-MM-dd")
            contact_number = self.contact_number_input.text().strip()
            email = self.email_input.text().strip()
            address = self.address_input.toPlainText().strip()
            shareholding = self.shareholding_input.value()
            active = self.active_checkbox.isChecked()
            
            # Validation
            if not director_name:
                QMessageBox.warning(self, "Validation Error", "Director name is required")
                return
            
            if not id_number:
                QMessageBox.warning(self, "Validation Error", "ID number is required")
                return
            
            # Check for duplicates
            for director in self.directors_data:
                if (director["name"].lower() == director_name.lower() and 
                    director["code"] != director_code):
                    QMessageBox.warning(self, "Duplicate Error", 
                                      "A director with this name already exists")
                    return
                
                if director["id_number"] == id_number and director["code"] != director_code:
                    QMessageBox.warning(self, "Duplicate Error", 
                                      "A director with this ID number already exists")
                    return
            
            # Create director record
            director = {
                "code": director_code,
                "name": director_name,
                "id_number": id_number,
                "position": position,
                "appointment_date": appointment_date,
                "contact_number": contact_number,
                "email": email,
                "address": address,
                "shareholding": shareholding,
                "active": active,
                "date_created": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat()
            }
            
            self.directors_data.append(director)
            self._save_data()
            self._refresh_directors_table()
            self._clear_director_form()
            self._generate_director_code()
            
            # Update dropdowns
            self._populate_loan_director_combo()
            self._populate_expense_director_combo()
            
            QMessageBox.information(self, "Success", 
                                  f"Director '{director_name}' added successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add director: {str(e)}")

    def _edit_director(self):
        """Edit existing director"""
        current_row = self.directors_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", 
                              "Please select a director to edit")
            return
        
        if current_row >= len(self.directors_data):
            return
        
        # Load director data into form
        director = self.directors_data[current_row]
        self.director_code_input.setText(director["code"])
        self.director_name_input.setText(director["name"])
        self.id_number_input.setText(director["id_number"])
        self.position_combo.setCurrentText(director["position"])
        self.appointment_date.setDate(QDate.fromString(director["appointment_date"], "yyyy-MM-dd"))
        self.contact_number_input.setText(director["contact_number"])
        self.email_input.setText(director["email"])
        self.address_input.setPlainText(director["address"])
        self.shareholding_input.setValue(director["shareholding"])
        self.active_checkbox.setChecked(director["active"])
        
        # Change button text to update
        self.add_director_btn.setText("Update Director")
        self.editing_index = current_row

    def _delete_director(self):
        """Delete director"""
        current_row = self.directors_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", 
                              "Please select a director to delete")
            return
        
        if current_row >= len(self.directors_data):
            return
        
        director = self.directors_data[current_row]
        
        # Check if director has outstanding loans
        director_loans = [l for l in self.loans_data if l["director_code"] == director["code"]]
        if director_loans:
            QMessageBox.warning(self, "Cannot Delete", 
                              f"Director '{director['name']}' has {len(director_loans)} outstanding loans. Cannot delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete director '{director['name']}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.directors_data[current_row]
            self._save_data()
            self._refresh_directors_table()
            self._clear_director_form()
            self._generate_director_code()
            
            # Update dropdowns
            self._populate_loan_director_combo()
            self._populate_expense_director_combo()

    def _create_loan(self):
        """Create loan to director - DIR-011 to DIR-014"""
        try:
            director_text = self.loan_director_combo.currentText()
            if not director_text:
                QMessageBox.warning(self, "Validation Error", "Please select a director")
                return
            
            director_code = director_text.split(" - ")[0]
            loan_number = self.loan_number_input.text().strip()
            loan_date = self.loan_date.date().toString("yyyy-MM-dd")
            loan_amount = self.loan_amount.value()
            interest_rate = self.interest_rate.value()
            loan_term = self.loan_term.value()
            repayment_method = self.repayment_method_combo.currentText()
            purpose = self.loan_purpose.text().strip()
            
            if loan_amount <= 0:
                QMessageBox.warning(self, "Validation Error", 
                                  "Loan amount must be greater than 0")
                return
            
            if not purpose:
                QMessageBox.warning(self, "Validation Error", "Loan purpose is required")
                return
            
            # Create loan record
            loan = {
                "loan_number": loan_number,
                "director_code": director_code,
                "loan_date": loan_date,
                "loan_amount": loan_amount,
                "interest_rate": interest_rate,
                "loan_term": loan_term,
                "repayment_method": repayment_method,
                "purpose": purpose,
                "balance_outstanding": loan_amount,
                "status": "Active",
                "timestamp": datetime.now().isoformat()
            }
            
            # Post to ledger using CCE cumulative update - DIR-014
            if self.ledger:
                # Create journal entry for loan to director
                lines = [
                    {
                        "account_code": "1100",  # Loans to Directors (Current Asset)
                        "debit": loan_amount,
                        "credit": 0,
                        "notes": f"Loan to {director_code} - {purpose}"
                    },
                    {
                        "account_code": "1000",  # Bank FNB Cheque
                        "debit": 0,
                        "credit": loan_amount,
                        "notes": f"Loan disbursement to {director_code}"
                    }
                ]
                
                journal_code = self.ledger.post_journal_entry(
                    date_str=loan_date,
                    reference=loan_number,
                    description=f"Loan to Director - {purpose}",
                    lines=lines,
                    auto_balance=False  # Already balanced
                )
                
                loan["journal_code"] = journal_code
                
                # Apply CCE cumulative update
                self.ledger.update_cce(-loan_amount, "director_loan")
            
            self.loans_data.append(loan)
            self._save_data()
            self._refresh_loans_table()
            self._clear_loan_form()
            self._generate_loan_number()
            
            # Request dashboard refresh
            self.dashboard_refresh_requested.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Loan {loan_number} created successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create loan: {str(e)}")

    def _add_expense(self):
        """Add director expense - DIR-016"""
        try:
            director_text = self.expense_director_combo.currentText()
            if not director_text:
                QMessageBox.warning(self, "Validation Error", "Please select a director")
                return
            
            director_code = director_text.split(" - ")[0]
            expense_date = self.expense_date.date().toString("yyyy-MM-dd")
            expense_category = self.expense_category_combo.currentText()
            expense_amount = self.expense_amount.value()
            description = self.expense_description.text().strip()
            receipt_number = self.receipt_number.text().strip()
            
            if expense_amount <= 0:
                QMessageBox.warning(self, "Validation Error", 
                                  "Expense amount must be greater than 0")
                return
            
            if not description:
                QMessageBox.warning(self, "Validation Error", 
                                  "Expense description is required")
                return
            
            # Create expense record
            expense = {
                "director_code": director_code,
                "expense_date": expense_date,
                "expense_category": expense_category,
                "expense_amount": expense_amount,
                "description": description,
                "receipt_number": receipt_number,
                "timestamp": datetime.now().isoformat()
            }
            
            # Post to ledger
            if self.ledger:
                # Create journal entry for director expense
                lines = [
                    {
                        "account_code": "5100",  # Operating Expenses
                        "debit": expense_amount,
                        "credit": 0,
                        "notes": f"Director expense - {description}"
                    },
                    {
                        "account_code": "1000",  # Bank FNB Cheque
                        "debit": 0,
                        "credit": expense_amount,
                        "notes": f"Payment for director expense - {receipt_number}"
                    }
                ]
                
                journal_code = self.ledger.post_journal_entry(
                    date_str=expense_date,
                    reference=receipt_number or "EXP",
                    description=f"Director Expense - {expense_category}",
                    lines=lines,
                    auto_balance=False  # Already balanced
                )
                
                expense["journal_code"] = journal_code
                
                # Apply CCE cumulative update
                self.ledger.update_cce(-expense_amount, "director_expense")
            
            self.expenses_data.append(expense)
            self._save_data()
            self._refresh_expenses_table()
            self._clear_expense_form()
            
            # Request dashboard refresh
            self.dashboard_refresh_requested.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Expense of {_fmt_amount(expense_amount)} added successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add expense: {str(e)}")

    def _generate_report(self):
        """Generate director reports - DIR-017"""
        try:
            report_type = self.report_type_combo.currentText()
            from_date = self.report_from_date.date().toString("yyyy-MM-dd")
            to_date = self.report_to_date.date().toString("yyyy-MM-dd")
            
            if report_type == "Directors Register":
                self._generate_directors_register(from_date, to_date)
            elif report_type == "Loans to Directors Statement":
                self._generate_loans_statement(from_date, to_date)
            elif report_type == "Director Expense Report":
                self._generate_expense_report(from_date, to_date)
            elif report_type == "AFS Note 2 - Loans to Directors":
                self._generate_afs_note_2(from_date, to_date)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

    def _generate_directors_register(self, from_date, to_date):
        """Generate directors register"""
        report = f"""
{'='*60}
DIRECTORS REGISTER
{'='*60}

Report Period: {from_date} to {to_date}

{'='*60}
ACTIVE DIRECTORS
{'='*60}

Code  Name                    Position           Appointment Date  Shareholding
{'-'*60}
"""
        
        for director in self.directors_data:
            if director["active"]:
                report += f"{director['code']:5} {director['name'][:23]:23} {director['position'][:18]:18} {director['appointment_date']:15} {director['shareholding']:11.2f}%\n"
        
        report += f"""
{'='*60}
Total Active Directors: {len([d for d in self.directors_data if d['active']])}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _generate_loans_statement(self, from_date, to_date):
        """Generate loans to directors statement"""
        report = f"""
{'='*60}
LOANS TO DIRECTORS STATEMENT
{'='*60}

Report Period: {from_date} to {to_date}

{'='*60}
OUTSTANDING LOANS
{'='*60}

Loan No    Director           Date        Amount      Interest    Balance
{'-'*60}
"""
        
        total_loans = 0.0
        total_balance = 0.0
        
        for loan in self.loans_data:
            if from_date <= loan["loan_date"] <= to_date:
                # Find director name
                director_name = "Unknown"
                for director in self.directors_data:
                    if director["code"] == loan["director_code"]:
                        director_name = director["name"]
                        break
                
                total_loans += loan["loan_amount"]
                total_balance += loan["balance_outstanding"]
                
                report += f"{loan['loan_number']:10} {director_name[:18]:18} {loan['loan_date']:12} {_fmt_amount(loan['loan_amount']):11} {loan['interest_rate']:8.2f}% {_fmt_amount(loan['balance_outstanding']):11}\n"
        
        report += f"""
{'-'*60}
Total Loans:      {_fmt_amount(total_loans):>11}
Total Balance:    {_fmt_amount(total_balance):>11}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _generate_expense_report(self, from_date, to_date):
        """Generate director expense report"""
        report = f"""
{'='*60}
DIRECTOR EXPENSE REPORT
{'='*60}

Report Period: {from_date} to {to_date}

{'='*60}
EXPENSES BY CATEGORY
{'='*60}
"""
        
        # Calculate totals by category
        category_totals = {}
        for expense in self.expenses_data:
            if from_date <= expense["expense_date"] <= to_date:
                category = expense["expense_category"]
                if category not in category_totals:
                    category_totals[category] = 0.0
                category_totals[category] += expense["expense_amount"]
        
        for category, total in category_totals.items():
            report += f"{category[:20]:20} {_fmt_amount(total):>15}\n"
        
        report += f"""
{'='*60}
DETAILED EXPENSES
{'='*60}

Date        Director           Category           Amount      Description
{'-'*60}
"""
        
        total_expenses = 0.0
        for expense in self.expenses_data:
            if from_date <= expense["expense_date"] <= to_date:
                # Find director name
                director_name = "Unknown"
                for director in self.directors_data:
                    if director["code"] == expense["director_code"]:
                        director_name = director["name"]
                        break
                
                total_expenses += expense["expense_amount"]
                
                report += f"{expense['expense_date']:12} {director_name[:18]:18} {expense['expense_category'][:18]:18} {_fmt_amount(expense['expense_amount']):11} {expense['description'][:25]:25}\n"
        
        report += f"""
{'-'*60}
Total Expenses: {_fmt_amount(total_expenses):>15}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _generate_afs_note_2(self, from_date, to_date):
        """Generate AFS Note 2 - Loans to Directors"""
        report = f"""
{'='*60}
ANNUAL FINANCIAL STATEMENTS - NOTE 2
LOANS TO DIRECTORS
{'='*60}

Year Ended: {to_date[:4]}

{'='*60}
2. LOANS TO DIRECTORS
{'='*60}

The following loans were advanced to directors during the year:

{'='*60}
LOAN DETAILS
{'='*60}

Director               Loan Amount    Interest Rate    Terms        Balance
{'-'*60}
"""
        
        total_balance = 0.0
        
        for loan in self.loans_data:
            if loan["status"] == "Active":
                # Find director name
                director_name = "Unknown"
                for director in self.directors_data:
                    if director["code"] == loan["director_code"]:
                        director_name = director["name"]
                        break
                
                total_balance += loan["balance_outstanding"]
                
                terms = f"{loan['loan_term']} months - {loan['repayment_method']}"
                report += f"{director_name[:22]:22} {_fmt_amount(loan['loan_amount']):14} {loan['interest_rate']:13.2f}% {terms[:12]:12} {_fmt_amount(loan['balance_outstanding']):12}\n"
        
        report += f"""
{'-'*60}
Total Balance Outstanding: {_fmt_amount(total_balance):>12}

{'='*60}
LOAN TERMS AND CONDITIONS
{'='*60}

All loans to directors are made on arm's length terms and are subject
to normal commercial interest rates. The loans are repayable in accordance
with the terms specified above and are secured by appropriate guarantees
where applicable.

The loans have been approved by the board of directors and comply with
the requirements of the Companies Act and relevant corporate governance
guidelines.

{'='*60}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _print_report(self):
        """Print director report"""
        report_text = self.report_preview.toPlainText()
        if not report_text.strip():
            QMessageBox.warning(self, "No Report", "Please generate a report first")
            return
        
        # In a real implementation, this would send to printer
        QMessageBox.information(self, "Print Report", 
                              "Report sent to printer (simulated)")

    def _clear_director_form(self):
        """Clear director form"""
        self.director_name_input.clear()
        self.id_number_input.clear()
        self.position_combo.setCurrentIndex(0)
        self.contact_number_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.shareholding_input.setValue(0)
        self.active_checkbox.setChecked(True)
        self.add_director_btn.setText("Add Director")
        self.editing_index = None

    def _clear_loan_form(self):
        """Clear loan form"""
        self.loan_director_combo.setCurrentIndex(0)
        self.loan_amount.setValue(0)
        self.interest_rate.setValue(8.0)
        self.loan_term.setValue(60)
        self.repayment_method_combo.setCurrentIndex(0)
        self.loan_purpose.clear()

    def _clear_expense_form(self):
        """Clear expense form"""
        self.expense_director_combo.setCurrentIndex(0)
        self.expense_category_combo.setCurrentIndex(0)
        self.expense_amount.setValue(0)
        self.expense_description.clear()
        self.receipt_number.clear()

    def _refresh_directors_table(self):
        """Refresh directors table"""
        self.directors_table.setRowCount(len(self.directors_data))
        
        for row, director in enumerate(self.directors_data):
            self.directors_table.setItem(row, 0, QTableWidgetItem(director["code"]))
            self.directors_table.setItem(row, 1, QTableWidgetItem(director["name"]))
            self.directors_table.setItem(row, 2, QTableWidgetItem(director["position"]))
            self.directors_table.setItem(row, 3, QTableWidgetItem(director["appointment_date"]))
            self.directors_table.setItem(row, 4, QTableWidgetItem(f"{director['shareholding']:.2f}%"))
            
            # Status with color coding
            status_item = QTableWidgetItem("Active" if director["active"] else "Inactive")
            if director["active"]:
                status_item.setStyleSheet("color: #00B050; font-weight: bold;")
            else:
                status_item.setStyleSheet("color: #D32F2F; font-weight: bold;")
            
            self.directors_table.setItem(row, 5, status_item)
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_director(r))
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
            self.directors_table.setCellWidget(row, 6, action_btn)

    def _refresh_loans_table(self):
        """Refresh loans table"""
        self.loans_table.setRowCount(len(self.loans_data))
        
        for row, loan in enumerate(self.loans_data):
            self.loans_table.setItem(row, 0, QTableWidgetItem(loan["loan_number"]))
            
            # Find director name
            director_name = "Unknown"
            for director in self.directors_data:
                if director["code"] == loan["director_code"]:
                    director_name = director["name"]
                    break
            
            self.loans_table.setItem(row, 1, QTableWidgetItem(director_name))
            self.loans_table.setItem(row, 2, QTableWidgetItem(loan["loan_date"]))
            self.loans_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(loan["loan_amount"])))
            self.loans_table.setItem(row, 4, QTableWidgetItem(f"{loan['interest_rate']:.2f}%"))
            self.loans_table.setItem(row, 5, QTableWidgetItem(f"{loan['loan_term']} months"))
            self.loans_table.setItem(row, 6, QTableWidgetItem(_fmt_amount(loan["balance_outstanding"])))
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_loan(r))
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
            self.loans_table.setCellWidget(row, 7, action_btn)

    def _refresh_expenses_table(self):
        """Refresh expenses table"""
        self.expenses_table.setRowCount(len(self.expenses_data))
        
        for row, expense in enumerate(self.expenses_data):
            self.expenses_table.setItem(row, 0, QTableWidgetItem(expense["expense_date"]))
            
            # Find director name
            director_name = "Unknown"
            for director in self.directors_data:
                if director["code"] == expense["director_code"]:
                    director_name = director["name"]
                    break
            
            self.expenses_table.setItem(row, 1, QTableWidgetItem(director_name))
            self.expenses_table.setItem(row, 2, QTableWidgetItem(expense["expense_category"]))
            self.expenses_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(expense["expense_amount"])))
            self.expenses_table.setItem(row, 4, QTableWidgetItem(expense["description"]))
            self.expenses_table.setItem(row, 5, QTableWidgetItem(expense.get("receipt_number", "")))

    def _select_director(self, row):
        """Select director row"""
        self.directors_table.selectRow(row)

    def _select_loan(self, row):
        """Select loan row"""
        self.loans_table.selectRow(row)

    def _save_data(self):
        """Save all data to files"""
        try:
            with open(self.directors_file, 'w') as f:
                json.dump(self.directors_data, f, indent=2)
            with open(self.director_loans_file, 'w') as f:
                json.dump(self.loans_data, f, indent=2)
            with open(self.director_expenses_file, 'w') as f:
                json.dump(self.expenses_data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def _load_data(self):
        """Load all data from files"""
        try:
            if self.directors_file.exists():
                with open(self.directors_file, 'r') as f:
                    self.directors_data = json.load(f)
            
            if self.director_loans_file.exists():
                with open(self.director_loans_file, 'r') as f:
                    self.loans_data = json.load(f)
            
            if self.director_expenses_file.exists():
                with open(self.director_expenses_file, 'r') as f:
                    self.expenses_data = json.load(f)
                    
        except Exception as e:
            print(f"Error loading data: {e}")
            self.directors_data = []
            self.loans_data = []
            self.expenses_data = []

    def get_directors_data(self):
        """Get directors data"""
        return self.directors_data.copy()

    def get_director_loans_balance(self, director_code: str = None) -> float:
        """Get total outstanding loans balance"""
        total = 0.0
        for loan in self.loans_data:
            if loan["status"] == "Active":
                if director_code is None or loan["director_code"] == director_code:
                    total += loan["balance_outstanding"]
        return total
