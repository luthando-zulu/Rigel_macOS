#!/usr/bin/env python3
"""
Customers Module Handler
Implements CUS-001 to CUS-014 test cases for customer management functionality
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
    QSpinBox, QFormLayout
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from accounting import AccountingLedger, CHART_OF_ACCOUNTS, _fmt_amount

class CustomersHandler(QWidget):
    """Customers Module Handler - Implements CUS-001 to CUS-014"""
    
    # Signals for communication with main window
    dashboard_refresh_requested = pyqtSignal()
    navigation_requested = pyqtSignal(str)  # Page name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ledger = getattr(parent, 'ledger', None) if parent else None
        self.customers_data = []
        self.invoices_data = []
        self.payments_data = []
        self.editing_index = None
        
        # Data file paths
        self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.customers_file = self.data_dir / "customers.json"
        self.invoices_file = self.data_dir / "customer_invoices.json"
        self.payments_file = self.data_dir / "customer_payments.json"
        
        self._load_data()
        self._build_ui()

    def _build_ui(self):
        """Build customers UI - CUS-001: Navigation to Customers"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Customer Management")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Create tabbed interface
        tab_widget = QTabWidget()
        
        # Customer Masterfile Tab
        customers_tab = self._create_customers_tab()
        tab_widget.addTab(customers_tab, "Customers")
        
        # Invoices Tab
        invoices_tab = self._create_invoices_tab()
        tab_widget.addTab(invoices_tab, "Invoices")
        
        # Payments Tab
        payments_tab = self._create_payments_tab()
        tab_widget.addTab(payments_tab, "Account Payments")
        
        # Statements Tab
        statements_tab = self._create_statements_tab()
        tab_widget.addTab(statements_tab, "Statements")
        
        layout.addWidget(tab_widget)

    def _create_customers_tab(self):
        """Create customers masterfile tab - CUS-001 to CUS-008"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Customer Entry Group
        customer_group = QGroupBox("Customer Information")
        customer_group.setStyleSheet("""
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
        customer_layout = QGridLayout(customer_group)
        customer_layout.setSpacing(10)

        # Customer Code (auto-generated)
        customer_layout.addWidget(QLabel("Customer Code:"), 0, 0)
        self.customer_code_input = QLineEdit()
        self.customer_code_input.setReadOnly(True)
        self.customer_code_input.setStyleSheet("background: #F5F5F5;")
        customer_layout.addWidget(self.customer_code_input, 0, 1)

        # Customer Name
        customer_layout.addWidget(QLabel("Customer Name:"), 1, 0)
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("Enter customer name...")
        customer_layout.addWidget(self.customer_name_input, 1, 1)

        # Contact Person
        customer_layout.addWidget(QLabel("Contact Person:"), 2, 0)
        self.contact_person_input = QLineEdit()
        self.contact_person_input.setPlaceholderText("Enter contact person...")
        customer_layout.addWidget(self.contact_person_input, 2, 1)

        # Phone Number
        customer_layout.addWidget(QLabel("Phone Number:"), 3, 0)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number...")
        customer_layout.addWidget(self.phone_input, 3, 1)

        # Email Address
        customer_layout.addWidget(QLabel("Email Address:"), 4, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address...")
        customer_layout.addWidget(self.email_input, 4, 1)

        # Physical Address
        customer_layout.addWidget(QLabel("Physical Address:"), 5, 0)
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        self.address_input.setPlaceholderText("Enter physical address...")
        customer_layout.addWidget(self.address_input, 5, 1)

        # VAT Number
        customer_layout.addWidget(QLabel("VAT Number:"), 6, 0)
        self.vat_input = QLineEdit()
        self.vat_input.setPlaceholderText("Enter VAT number...")
        customer_layout.addWidget(self.vat_input, 6, 1)

        # Credit Limit
        customer_layout.addWidget(QLabel("Credit Limit:"), 7, 0)
        self.credit_limit_input = QDoubleSpinBox()
        self.credit_limit_input.setRange(0, 999999999)
        self.credit_limit_input.setDecimals(2)
        self.credit_limit_input.setPrefix("R ")
        self.credit_limit_input.setSingleStep(1000.00)
        customer_layout.addWidget(self.credit_limit_input, 7, 1)

        # Payment Terms
        customer_layout.addWidget(QLabel("Payment Terms:"), 8, 0)
        self.payment_terms_combo = QComboBox()
        self.payment_terms_combo.addItems([
            "30 Days", "60 Days", "90 Days", "COD", "Immediate"
        ])
        customer_layout.addWidget(self.payment_terms_combo, 8, 1)

        layout.addWidget(customer_group)

        # Customer Buttons
        customer_button_layout = QHBoxLayout()
        self.add_customer_btn = QPushButton("Add Customer")
        self.add_customer_btn.clicked.connect(self._add_customer)
        self.add_customer_btn.setStyleSheet("""
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
        
        self.edit_customer_btn = QPushButton("Edit Customer")
        self.edit_customer_btn.clicked.connect(self._edit_customer)
        self.edit_customer_btn.setStyleSheet("""
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
        
        self.delete_customer_btn = QPushButton("Delete Customer")
        self.delete_customer_btn.clicked.connect(self._delete_customer)
        self.delete_customer_btn.setStyleSheet("""
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
        
        self.clear_customer_btn = QPushButton("Clear Form")
        self.clear_customer_btn.clicked.connect(self._clear_customer_form)
        self.clear_customer_btn.setStyleSheet("""
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
        
        customer_button_layout.addWidget(self.add_customer_btn)
        customer_button_layout.addWidget(self.edit_customer_btn)
        customer_button_layout.addWidget(self.delete_customer_btn)
        customer_button_layout.addWidget(self.clear_customer_btn)
        customer_button_layout.addStretch()
        layout.addLayout(customer_button_layout)

        # Customers Table
        customers_table_group = QGroupBox("Customer Masterfile")
        customers_table_layout = QVBoxLayout(customers_table_group)
        
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(8)
        self.customers_table.setHorizontalHeaderLabels([
            "Code", "Name", "Contact", "Phone", "Email", "Credit Limit", "Balance", "Actions"
        ])
        
        # Style table
        header = self.customers_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.customers_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.customers_table.verticalHeader().setDefaultSectionSize(40)
        customers_table_layout.addWidget(self.customers_table)
        
        layout.addWidget(customers_table_group)
        layout.addStretch()

        # Generate initial customer code
        self._generate_customer_code()

        return tab

    def _create_invoices_tab(self):
        """Create invoices tab - CUS-009 to CUS-011"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Invoice Entry Group
        invoice_group = QGroupBox("Invoice Information")
        invoice_layout = QGridLayout(invoice_group)
        invoice_layout.setSpacing(10)

        # Customer Selection
        invoice_layout.addWidget(QLabel("Customer:"), 0, 0)
        self.invoice_customer_combo = QComboBox()
        self._populate_customer_combo()
        invoice_layout.addWidget(self.invoice_customer_combo, 0, 1)

        # Invoice Number (auto-generated)
        invoice_layout.addWidget(QLabel("Invoice Number:"), 1, 0)
        self.invoice_number_input = QLineEdit()
        self.invoice_number_input.setReadOnly(True)
        self.invoice_number_input.setStyleSheet("background: #F5F5F5;")
        invoice_layout.addWidget(self.invoice_number_input, 1, 1)

        # Invoice Date
        invoice_layout.addWidget(QLabel("Invoice Date:"), 2, 0)
        self.invoice_date = QDateEdit()
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setCalendarPopup(True)
        invoice_layout.addWidget(self.invoice_date, 2, 1)

        # Due Date
        invoice_layout.addWidget(QLabel("Due Date:"), 3, 0)
        self.due_date = QDateEdit()
        self.due_date.setDate(QDate.currentDate().addDays(30))
        self.due_date.setCalendarPopup(True)
        invoice_layout.addWidget(self.due_date, 3, 1)

        # Description
        invoice_layout.addWidget(QLabel("Description:"), 4, 0)
        self.invoice_description = QLineEdit()
        self.invoice_description.setPlaceholderText("Invoice description...")
        invoice_layout.addWidget(self.invoice_description, 4, 1)

        # Amount
        invoice_layout.addWidget(QLabel("Amount:"), 5, 0)
        self.invoice_amount = QDoubleSpinBox()
        self.invoice_amount.setRange(0, 999999999)
        self.invoice_amount.setDecimals(2)
        self.invoice_amount.setPrefix("R ")
        self.invoice_amount.setSingleStep(100.00)
        invoice_layout.addWidget(self.invoice_amount, 5, 1)

        # VAT (15%)
        invoice_layout.addWidget(QLabel("VAT (15%):"), 6, 0)
        self.invoice_vat = QDoubleSpinBox()
        self.invoice_vat.setRange(0, 999999999)
        self.invoice_vat.setDecimals(2)
        self.invoice_vat.setPrefix("R ")
        self.invoice_vat.setReadOnly(True)
        self.invoice_vat.setStyleSheet("background: #F5F5F5;")
        invoice_layout.addWidget(self.invoice_vat, 6, 1)

        # Total Amount
        invoice_layout.addWidget(QLabel("Total Amount:"), 7, 0)
        self.invoice_total = QDoubleSpinBox()
        self.invoice_total.setRange(0, 999999999)
        self.invoice_total.setDecimals(2)
        self.invoice_total.setPrefix("R ")
        self.invoice_total.setReadOnly(True)
        self.invoice_total.setStyleSheet("background: #F5F5F5; font-weight: bold;")
        invoice_layout.addWidget(self.invoice_total, 7, 1)

        layout.addWidget(invoice_group)

        # Connect amount change to calculate VAT and total
        self.invoice_amount.valueChanged.connect(self._calculate_invoice_totals)

        # Invoice Buttons
        invoice_button_layout = QHBoxLayout()
        self.create_invoice_btn = QPushButton("Create Invoice")
        self.create_invoice_btn.clicked.connect(self._create_invoice)
        self.create_invoice_btn.setStyleSheet("""
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
        
        self.clear_invoice_btn = QPushButton("Clear Form")
        self.clear_invoice_btn.clicked.connect(self._clear_invoice_form)
        self.clear_invoice_btn.setStyleSheet("""
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
        
        invoice_button_layout.addWidget(self.create_invoice_btn)
        invoice_button_layout.addWidget(self.clear_invoice_btn)
        invoice_button_layout.addStretch()
        layout.addLayout(invoice_button_layout)

        # Invoices Table
        invoices_table_group = QGroupBox("Customer Invoices")
        invoices_table_layout = QVBoxLayout(invoices_table_group)
        
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(7)
        self.invoices_table.setHorizontalHeaderLabels([
            "Invoice No", "Customer", "Date", "Due Date", "Amount", "Status", "Actions"
        ])
        
        # Style table
        header = self.invoices_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.invoices_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.invoices_table.verticalHeader().setDefaultSectionSize(40)
        invoices_table_layout.addWidget(self.invoices_table)
        
        layout.addWidget(invoices_table_group)
        layout.addStretch()

        # Generate initial invoice number
        self._generate_invoice_number()

        return tab

    def _create_payments_tab(self):
        """Create account payments tab - CUS-005, CUS-006, CUS-012, CUS-013"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Payment Entry Group
        payment_group = QGroupBox("Account Payment")
        payment_layout = QGridLayout(payment_group)
        payment_layout.setSpacing(10)

        # Customer Selection
        payment_layout.addWidget(QLabel("Customer:"), 0, 0)
        self.payment_customer_combo = QComboBox()
        self._populate_payment_customer_combo()
        payment_layout.addWidget(self.payment_customer_combo, 0, 1)

        # Invoice Selection
        payment_layout.addWidget(QLabel("Invoice:"), 1, 0)
        self.payment_invoice_combo = QComboBox()
        self.payment_invoice_combo.currentTextChanged.connect(self._on_invoice_selected)
        payment_layout.addWidget(self.payment_invoice_combo, 1, 1)

        # Payment Date
        payment_layout.addWidget(QLabel("Payment Date:"), 2, 0)
        self.payment_date = QDateEdit()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setCalendarPopup(True)
        payment_layout.addWidget(self.payment_date, 2, 1)

        # Payment Amount
        payment_layout.addWidget(QLabel("Payment Amount:"), 3, 0)
        self.payment_amount = QDoubleSpinBox()
        self.payment_amount.setRange(0, 999999999)
        self.payment_amount.setDecimals(2)
        self.payment_amount.setPrefix("R ")
        self.payment_amount.setSingleStep(100.00)
        payment_layout.addWidget(self.payment_amount, 3, 1)

        # Payment Method
        payment_layout.addWidget(QLabel("Payment Method:"), 4, 0)
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems([
            "Bank Transfer", "Cash", "Credit Card", "EFT", "Other"
        ])
        payment_layout.addWidget(self.payment_method_combo, 4, 1)

        # Reference
        payment_layout.addWidget(QLabel("Reference:"), 5, 0)
        self.payment_reference = QLineEdit()
        self.payment_reference.setPlaceholderText("Payment reference...")
        payment_layout.addWidget(self.payment_reference, 5, 1)

        layout.addWidget(payment_group)

        # Payment Buttons
        payment_button_layout = QHBoxLayout()
        self.process_payment_btn = QPushButton("Process Payment")
        self.process_payment_btn.clicked.connect(self._process_payment)
        self.process_payment_btn.setStyleSheet("""
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
        
        self.clear_payment_btn = QPushButton("Clear Form")
        self.clear_payment_btn.clicked.connect(self._clear_payment_form)
        self.clear_payment_btn.setStyleSheet("""
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
        
        payment_button_layout.addWidget(self.process_payment_btn)
        payment_button_layout.addWidget(self.clear_payment_btn)
        payment_button_layout.addStretch()
        layout.addLayout(payment_button_layout)

        # Payments Table
        payments_table_group = QGroupBox("Account Payments")
        payments_table_layout = QVBoxLayout(payments_table_group)
        
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(6)
        self.payments_table.setHorizontalHeaderLabels([
            "Date", "Customer", "Invoice", "Amount", "Method", "Reference"
        ])
        
        # Style table
        header = self.payments_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.payments_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.payments_table.verticalHeader().setDefaultSectionSize(40)
        payments_table_layout.addWidget(self.payments_table)
        
        layout.addWidget(payments_table_group)
        layout.addStretch()

        return tab

    def _create_statements_tab(self):
        """Create customer statements tab - CUS-014"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Statement Generation Group
        statement_group = QGroupBox("Generate Customer Statement")
        statement_layout = QGridLayout(statement_group)
        statement_layout.setSpacing(10)

        # Customer Selection
        statement_layout.addWidget(QLabel("Customer:"), 0, 0)
        self.statement_customer_combo = QComboBox()
        self._populate_statement_customer_combo()
        statement_layout.addWidget(self.statement_customer_combo, 0, 1)

        # Statement Period
        statement_layout.addWidget(QLabel("From Date:"), 1, 0)
        self.statement_from_date = QDateEdit()
        self.statement_from_date.setDate(QDate.currentDate().addMonths(-1))
        self.statement_from_date.setCalendarPopup(True)
        statement_layout.addWidget(self.statement_from_date, 1, 1)

        statement_layout.addWidget(QLabel("To Date:"), 2, 0)
        self.statement_to_date = QDateEdit()
        self.statement_to_date.setDate(QDate.currentDate())
        self.statement_to_date.setCalendarPopup(True)
        statement_layout.addWidget(self.statement_to_date, 2, 1)

        layout.addWidget(statement_group)

        # Statement Buttons
        statement_button_layout = QHBoxLayout()
        self.generate_statement_btn = QPushButton("Generate Statement")
        self.generate_statement_btn.clicked.connect(self._generate_statement)
        self.generate_statement_btn.setStyleSheet("""
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
        
        self.print_statement_btn = QPushButton("Print Statement")
        self.print_statement_btn.clicked.connect(self._print_statement)
        self.print_statement_btn.setStyleSheet("""
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
        
        statement_button_layout.addWidget(self.generate_statement_btn)
        statement_button_layout.addWidget(self.print_statement_btn)
        statement_button_layout.addStretch()
        layout.addLayout(statement_button_layout)

        # Statement Preview
        statement_preview_group = QGroupBox("Statement Preview")
        statement_preview_layout = QVBoxLayout(statement_preview_group)
        
        self.statement_preview = QTextEdit()
        self.statement_preview.setReadOnly(True)
        self.statement_preview.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                padding: 10px;
                font-family: 'Courier New', monospace;
            }
        """)
        statement_preview_layout.addWidget(self.statement_preview)
        
        layout.addWidget(statement_preview_group)
        layout.addStretch()

        return tab

    def _generate_customer_code(self):
        """Generate unique customer code"""
        existing_codes = [c["code"] for c in self.customers_data]
        prefix = "CUS"
        counter = 1
        while f"{prefix}{counter:03d}" in existing_codes:
            counter += 1
        self.customer_code_input.setText(f"{prefix}{counter:03d}")

    def _generate_invoice_number(self):
        """Generate unique invoice number"""
        existing_numbers = [i["invoice_number"] for i in self.invoices_data]
        prefix = "INV"
        counter = 1
        current_year = date.today().year
        while f"{prefix}{current_year}{counter:04d}" in existing_numbers:
            counter += 1
        self.invoice_number_input.setText(f"{prefix}{current_year}{counter:04d}")

    def _calculate_invoice_totals(self):
        """Calculate VAT and total amount"""
        amount = self.invoice_amount.value()
        vat = amount * Decimal("0.15")
        total = amount + vat
        
        self.invoice_vat.setValue(float(vat))
        self.invoice_total.setValue(float(total))

    def _populate_customer_combo(self):
        """Populate customer dropdown for invoices"""
        self.invoice_customer_combo.clear()
        for customer in self.customers_data:
            self.invoice_customer_combo.addItem(f"{customer['code']} - {customer['name']}")

    def _populate_payment_customer_combo(self):
        """Populate customer dropdown for payments"""
        self.payment_customer_combo.clear()
        for customer in self.customers_data:
            self.payment_customer_combo.addItem(f"{customer['code']} - {customer['name']}")

    def _populate_statement_customer_combo(self):
        """Populate customer dropdown for statements"""
        self.statement_customer_combo.clear()
        for customer in self.customers_data:
            self.statement_customer_combo.addItem(f"{customer['code']} - {customer['name']}")

    def _on_invoice_selected(self):
        """Handle invoice selection for payments"""
        selected_text = self.payment_invoice_combo.currentText()
        if selected_text:
            # Extract invoice amount and set as max payment
            for invoice in self.invoices_data:
                if invoice["invoice_number"] in selected_text:
                    self.payment_amount.setMaximum(invoice["total_amount"])
                    break

    def _add_customer(self):
        """Add new customer - CUS-002 to CUS-004"""
        try:
            customer_code = self.customer_code_input.text().strip()
            customer_name = self.customer_name_input.text().strip()
            contact_person = self.contact_person_input.text().strip()
            phone = self.phone_input.text().strip()
            email = self.email_input.text().strip()
            address = self.address_input.toPlainText().strip()
            vat_number = self.vat_input.text().strip()
            credit_limit = self.credit_limit_input.value()
            payment_terms = self.payment_terms_combo.currentText()
            
            # Validation
            if not customer_name:
                QMessageBox.warning(self, "Validation Error", "Customer name is required")
                return
            
            # Check for duplicates
            for customer in self.customers_data:
                if customer["name"].lower() == customer_name.lower() and customer["code"] != customer_code:
                    QMessageBox.warning(self, "Duplicate Error", "A customer with this name already exists")
                    return
            
            # Create customer record
            customer = {
                "code": customer_code,
                "name": customer_name,
                "contact_person": contact_person,
                "phone": phone,
                "email": email,
                "address": address,
                "vat_number": vat_number,
                "credit_limit": credit_limit,
                "payment_terms": payment_terms,
                "balance": 0.0,
                "date_created": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat()
            }
            
            self.customers_data.append(customer)
            self._save_data()
            self._refresh_customers_table()
            self._clear_customer_form()
            self._generate_customer_code()
            
            # Update dropdowns
            self._populate_customer_combo()
            self._populate_payment_customer_combo()
            self._populate_statement_customer_combo()
            
            QMessageBox.information(self, "Success", f"Customer '{customer_name}' added successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add customer: {str(e)}")

    def _edit_customer(self):
        """Edit existing customer"""
        current_row = self.customers_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a customer to edit")
            return
        
        if current_row >= len(self.customers_data):
            return
        
        # Load customer data into form
        customer = self.customers_data[current_row]
        self.customer_code_input.setText(customer["code"])
        self.customer_name_input.setText(customer["name"])
        self.contact_person_input.setText(customer["contact_person"])
        self.phone_input.setText(customer["phone"])
        self.email_input.setText(customer["email"])
        self.address_input.setPlainText(customer["address"])
        self.vat_input.setText(customer["vat_number"])
        self.credit_limit_input.setValue(customer["credit_limit"])
        self.payment_terms_combo.setCurrentText(customer["payment_terms"])
        
        # Change button text to update
        self.add_customer_btn.setText("Update Customer")
        self.editing_index = current_row

    def _delete_customer(self):
        """Delete customer"""
        current_row = self.customers_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", "Please select a customer to delete")
            return
        
        if current_row >= len(self.customers_data):
            return
        
        customer = self.customers_data[current_row]
        
        # Check if customer has invoices
        customer_invoices = [i for i in self.invoices_data if i["customer_code"] == customer["code"]]
        if customer_invoices:
            QMessageBox.warning(self, "Cannot Delete", 
                              f"Customer '{customer['name']}' has {len(customer_invoices)} invoices. Cannot delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete customer '{customer['name']}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.customers_data[current_row]
            self._save_data()
            self._refresh_customers_table()
            self._clear_customer_form()
            self._generate_customer_code()
            
            # Update dropdowns
            self._populate_customer_combo()
            self._populate_payment_customer_combo()
            self._populate_statement_customer_combo()

    def _create_invoice(self):
        """Create customer invoice - CUS-009 to CUS-011"""
        try:
            customer_text = self.invoice_customer_combo.currentText()
            if not customer_text:
                QMessageBox.warning(self, "Validation Error", "Please select a customer")
                return
            
            customer_code = customer_text.split(" - ")[0]
            invoice_number = self.invoice_number_input.text().strip()
            invoice_date = self.invoice_date.date().toString("yyyy-MM-dd")
            due_date = self.due_date.date().toString("yyyy-MM-dd")
            description = self.invoice_description.text().strip()
            amount = self.invoice_amount.value()
            vat = self.invoice_vat.value()
            total = self.invoice_total.value()
            
            if not description:
                QMessageBox.warning(self, "Validation Error", "Invoice description is required")
                return
            
            if amount <= 0:
                QMessageBox.warning(self, "Validation Error", "Invoice amount must be greater than 0")
                return
            
            # Create invoice record
            invoice = {
                "invoice_number": invoice_number,
                "customer_code": customer_code,
                "invoice_date": invoice_date,
                "due_date": due_date,
                "description": description,
                "amount": amount,
                "vat": vat,
                "total_amount": total,
                "status": "Unpaid",
                "balance_due": total,
                "timestamp": datetime.now().isoformat()
            }
            
            # Post to ledger
            if self.ledger:
                # Create journal entry for invoice
                lines = [
                    {
                        "account_code": "1100",  # Accounts Receivable
                        "debit": total,
                        "credit": 0,
                        "notes": f"Invoice {invoice_number} - {description}"
                    },
                    {
                        "account_code": "4000",  # Sales Revenue
                        "debit": 0,
                        "credit": amount,
                        "notes": f"Invoice {invoice_number} - {description}"
                    },
                    {
                        "account_code": "2200",  # VAT Output
                        "debit": 0,
                        "credit": vat,
                        "notes": f"VAT on Invoice {invoice_number}"
                    }
                ]
                
                journal_code = self.ledger.post_journal_entry(
                    date_str=invoice_date,
                    reference=invoice_number,
                    description=f"Customer Invoice - {description}",
                    lines=lines,
                    auto_balance=False  # Already balanced
                )
                
                invoice["journal_code"] = journal_code
            
            self.invoices_data.append(invoice)
            self._save_data()
            self._refresh_invoices_table()
            self._clear_invoice_form()
            self._generate_invoice_number()
            
            # Update customer balance
            self._update_customer_balance(customer_code)
            
            # Request dashboard refresh
            self.dashboard_refresh_requested.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Invoice {invoice_number} created successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create invoice: {str(e)}")

    def _process_payment(self):
        """Process account payment - CUS-005, CUS-006, CUS-012, CUS-013"""
        try:
            customer_text = self.payment_customer_combo.currentText()
            invoice_text = self.payment_invoice_combo.currentText()
            
            if not customer_text or not invoice_text:
                QMessageBox.warning(self, "Validation Error", "Please select customer and invoice")
                return
            
            customer_code = customer_text.split(" - ")[0]
            invoice_number = invoice_text.split(" - ")[0]
            payment_date = self.payment_date.date().toString("yyyy-MM-dd")
            payment_amount = self.payment_amount.value()
            payment_method = self.payment_method_combo.currentText()
            reference = self.payment_reference.text().strip()
            
            if payment_amount <= 0:
                QMessageBox.warning(self, "Validation Error", "Payment amount must be greater than 0")
                return
            
            # Find invoice
            invoice = None
            for inv in self.invoices_data:
                if inv["invoice_number"] == invoice_number:
                    invoice = inv
                    break
            
            if not invoice:
                QMessageBox.warning(self, "Error", "Invoice not found")
                return
            
            if payment_amount > invoice["balance_due"]:
                QMessageBox.warning(self, "Validation Error", 
                                  "Payment amount cannot exceed balance due")
                return
            
            # Create payment record
            payment = {
                "customer_code": customer_code,
                "invoice_number": invoice_number,
                "payment_date": payment_date,
                "payment_amount": payment_amount,
                "payment_method": payment_method,
                "reference": reference,
                "timestamp": datetime.now().isoformat()
            }
            
            # Post to ledger using CCE cumulative update
            if self.ledger:
                # Create journal entry for payment
                lines = [
                    {
                        "account_code": "1000",  # Bank FNB Cheque
                        "debit": payment_amount,
                        "credit": 0,
                        "notes": f"Payment from {customer_code} - {reference}"
                    },
                    {
                        "account_code": "1100",  # Accounts Receivable
                        "debit": 0,
                        "credit": payment_amount,
                        "notes": f"Payment for Invoice {invoice_number}"
                    }
                ]
                
                journal_code = self.ledger.post_journal_entry(
                    date_str=payment_date,
                    reference=reference or "PAY",
                    description=f"Customer Payment - {invoice_number}",
                    lines=lines,
                    auto_balance=False  # Already balanced
                )
                
                payment["journal_code"] = journal_code
                
                # Apply CCE cumulative update
                self.ledger.update_cce(payment_amount, "customer_payment")
            
            self.payments_data.append(payment)
            
            # Update invoice balance
            invoice["balance_due"] -= payment_amount
            if invoice["balance_due"] <= 0:
                invoice["status"] = "Paid"
                invoice["balance_due"] = 0
            else:
                invoice["status"] = "Partially Paid"
            
            self._save_data()
            self._refresh_payments_table()
            self._refresh_invoices_table()
            self._clear_payment_form()
            
            # Update customer balance
            self._update_customer_balance(customer_code)
            
            # Request dashboard refresh
            self.dashboard_refresh_requested.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Payment of {_fmt_amount(payment_amount)} processed successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process payment: {str(e)}")

    def _generate_statement(self):
        """Generate customer statement - CUS-014"""
        try:
            customer_text = self.statement_customer_combo.currentText()
            if not customer_text:
                QMessageBox.warning(self, "Validation Error", "Please select a customer")
                return
            
            customer_code = customer_text.split(" - ")[0]
            from_date = self.statement_from_date.date().toString("yyyy-MM-dd")
            to_date = self.statement_to_date.date().toString("yyyy-MM-dd")
            
            # Find customer
            customer = None
            for c in self.customers_data:
                if c["code"] == customer_code:
                    customer = c
                    break
            
            if not customer:
                QMessageBox.warning(self, "Error", "Customer not found")
                return
            
            # Generate statement content
            statement = f"""
{'='*60}
CUSTOMER STATEMENT
{'='*60}

Customer: {customer['name']} ({customer['code']})
Address: {customer['address']}
Phone: {customer['phone']}
Email: {customer['email']}

Statement Period: {from_date} to {to_date}

{'='*60}
TRANSACTIONS
{'='*60}

Date        Description                 Invoice        Amount        Balance
{'-'*60}
"""
            
            # Add invoices
            balance = 0.0
            for invoice in self.invoices_data:
                if (invoice["customer_code"] == customer_code and 
                    from_date <= invoice["invoice_date"] <= to_date):
                    balance += invoice["total_amount"]
                    statement += f"{invoice['invoice_date']}  {invoice['description'][:25]:25}  {invoice['invoice_number']:12}  {_fmt_amount(invoice['total_amount']):12}  {_fmt_amount(balance):12}\n"
            
            # Add payments
            for payment in self.payments_data:
                if (payment["customer_code"] == customer_code and 
                    from_date <= payment["payment_date"] <= to_date):
                    balance -= payment["payment_amount"]
                    statement += f"{payment['payment_date']}  Payment - {payment['payment_method'][:20]:20}  {payment['reference']:12}  {_fmt_amount(-payment['payment_amount']):12}  {_fmt_amount(balance):12}\n"
            
            statement += f"""
{'-'*60}
Current Balance: {_fmt_amount(balance):>12}

{'='*60}
Payment Terms: {customer['payment_terms']}
Credit Limit: {_fmt_amount(customer['credit_limit'])}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
            
            self.statement_preview.setPlainText(statement)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate statement: {str(e)}")

    def _print_statement(self):
        """Print customer statement"""
        statement_text = self.statement_preview.toPlainText()
        if not statement_text.strip():
            QMessageBox.warning(self, "No Statement", "Please generate a statement first")
            return
        
        # In a real implementation, this would send to printer
        QMessageBox.information(self, "Print Statement", 
                              "Statement sent to printer (simulated)")

    def _update_customer_balance(self, customer_code):
        """Update customer outstanding balance"""
        balance = 0.0
        
        # Calculate from invoices
        for invoice in self.invoices_data:
            if invoice["customer_code"] == customer_code:
                balance += invoice["balance_due"]
        
        # Update customer record
        for customer in self.customers_data:
            if customer["code"] == customer_code:
                customer["balance"] = balance
                break
        
        self._refresh_customers_table()

    def _clear_customer_form(self):
        """Clear customer form"""
        self.customer_name_input.clear()
        self.contact_person_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.vat_input.clear()
        self.credit_limit_input.setValue(0)
        self.payment_terms_combo.setCurrentIndex(0)
        self.add_customer_btn.setText("Add Customer")
        self.editing_index = None

    def _clear_invoice_form(self):
        """Clear invoice form"""
        self.invoice_customer_combo.setCurrentIndex(0)
        self.invoice_description.clear()
        self.invoice_amount.setValue(0)
        self.invoice_vat.setValue(0)
        self.invoice_total.setValue(0)

    def _clear_payment_form(self):
        """Clear payment form"""
        self.payment_customer_combo.setCurrentIndex(0)
        self.payment_invoice_combo.clear()
        self.payment_amount.setValue(0)
        self.payment_method_combo.setCurrentIndex(0)
        self.payment_reference.clear()

    def _refresh_customers_table(self):
        """Refresh customers table"""
        self.customers_table.setRowCount(len(self.customers_data))
        
        for row, customer in enumerate(self.customers_data):
            self.customers_table.setItem(row, 0, QTableWidgetItem(customer["code"]))
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer["name"]))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer["contact_person"]))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer["phone"]))
            self.customers_table.setItem(row, 4, QTableWidgetItem(customer["email"]))
            self.customers_table.setItem(row, 5, QTableWidgetItem(_fmt_amount(customer["credit_limit"])))
            
            balance_item = QTableWidgetItem(_fmt_amount(customer["balance"]))
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            # Color code balance
            if customer["balance"] > 0:
                balance_item.setStyleSheet("color: #E07B00; font-weight: bold;")
            else:
                balance_item.setStyleSheet("color: #00B050;")
            self.customers_table.setItem(row, 6, balance_item)
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_customer(r))
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
            self.customers_table.setCellWidget(row, 7, action_btn)

    def _refresh_invoices_table(self):
        """Refresh invoices table"""
        self.invoices_table.setRowCount(len(self.invoices_data))
        
        for row, invoice in enumerate(self.invoices_data):
            self.invoices_table.setItem(row, 0, QTableWidgetItem(invoice["invoice_number"]))
            
            # Find customer name
            customer_name = "Unknown"
            for customer in self.customers_data:
                if customer["code"] == invoice["customer_code"]:
                    customer_name = customer["name"]
                    break
            
            self.invoices_table.setItem(row, 1, QTableWidgetItem(customer_name))
            self.invoices_table.setItem(row, 2, QTableWidgetItem(invoice["invoice_date"]))
            self.invoices_table.setItem(row, 3, QTableWidgetItem(invoice["due_date"]))
            self.invoices_table.setItem(row, 4, QTableWidgetItem(_fmt_amount(invoice["total_amount"])))
            
            # Status with color coding
            status_item = QTableWidgetItem(invoice["status"])
            if invoice["status"] == "Paid":
                status_item.setStyleSheet("color: #00B050; font-weight: bold;")
            elif invoice["status"] == "Partially Paid":
                status_item.setStyleSheet("color: #E07B00; font-weight: bold;")
            else:
                status_item.setStyleSheet("color: #D32F2F; font-weight: bold;")
            
            self.invoices_table.setItem(row, 5, status_item)
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_invoice(r))
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
            self.invoices_table.setCellWidget(row, 6, action_btn)

    def _refresh_payments_table(self):
        """Refresh payments table"""
        self.payments_table.setRowCount(len(self.payments_data))
        
        for row, payment in enumerate(self.payments_data):
            self.payments_table.setItem(row, 0, QTableWidgetItem(payment["payment_date"]))
            
            # Find customer name
            customer_name = "Unknown"
            for customer in self.customers_data:
                if customer["code"] == payment["customer_code"]:
                    customer_name = customer["name"]
                    break
            
            self.payments_table.setItem(row, 1, QTableWidgetItem(customer_name))
            self.payments_table.setItem(row, 2, QTableWidgetItem(payment["invoice_number"]))
            self.payments_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(payment["payment_amount"])))
            self.payments_table.setItem(row, 4, QTableWidgetItem(payment["payment_method"]))
            self.payments_table.setItem(row, 5, QTableWidgetItem(payment.get("reference", "")))

    def _select_customer(self, row):
        """Select customer row"""
        self.customers_table.selectRow(row)

    def _select_invoice(self, row):
        """Select invoice row"""
        self.invoices_table.selectRow(row)

    def _save_data(self):
        """Save all data to files"""
        try:
            with open(self.customers_file, 'w') as f:
                json.dump(self.customers_data, f, indent=2)
            with open(self.invoices_file, 'w') as f:
                json.dump(self.invoices_data, f, indent=2)
            with open(self.payments_file, 'w') as f:
                json.dump(self.payments_data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def _load_data(self):
        """Load all data from files"""
        try:
            if self.customers_file.exists():
                with open(self.customers_file, 'r') as f:
                    self.customers_data = json.load(f)
            
            if self.invoices_file.exists():
                with open(self.invoices_file, 'r') as f:
                    self.invoices_data = json.load(f)
            
            if self.payments_file.exists():
                with open(self.payments_file, 'r') as f:
                    self.payments_data = json.load(f)
                    
        except Exception as e:
            print(f"Error loading data: {e}")
            self.customers_data = []
            self.invoices_data = []
            self.payments_data = []

    def get_customers_data(self):
        """Get customers data"""
        return self.customers_data.copy()

    def get_customer_balance(self, customer_code: str) -> float:
        """Get customer outstanding balance"""
        for customer in self.customers_data:
            if customer["code"] == customer_code:
                return customer["balance"]
        return 0.0
