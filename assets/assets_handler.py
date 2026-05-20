#!/usr/bin/env python3
"""
Assets Module Handler
Implements AST-001 to AST-011 test cases for fixed assets management functionality
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

from accounting import AccountingLedger, CHART_OF_ACCOUNTS, _fmt_amount, VAT_RATE

class AssetsHandler(QWidget):
    """Assets Module Handler - Implements AST-001 to AST-011"""
    
    # Signals for communication with main window
    dashboard_refresh_requested = pyqtSignal()
    navigation_requested = pyqtSignal(str)  # Page name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ledger = getattr(parent, 'ledger', None) if parent else None
        self.assets_data = []
        self.asset_transactions_data = []
        self.editing_index = None
        
        # Data file paths
        self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.assets_file = self.data_dir / "fixed_assets.json"
        self.asset_transactions_file = self.data_dir / "asset_transactions.json"
        
        self._load_data()
        self._build_ui()

    def _build_ui(self):
        """Build assets UI - AST-001: Navigation to Assets"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Fixed Assets Management")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Create tabbed interface
        tab_widget = QTabWidget()
        
        # Assets Masterfile Tab
        assets_tab = self._create_assets_tab()
        tab_widget.addTab(assets_tab, "Assets")
        
        # Asset Transactions Tab
        transactions_tab = self._create_transactions_tab()
        tab_widget.addTab(transactions_tab, "Asset Transactions")
        
        # Depreciation Tab
        depreciation_tab = self._create_depreciation_tab()
        tab_widget.addTab(depreciation_tab, "Depreciation")
        
        # Reports Tab
        reports_tab = self._create_reports_tab()
        tab_widget.addTab(reports_tab, "Reports")
        
        layout.addWidget(tab_widget)

    def _create_assets_tab(self):
        """Create assets masterfile tab - AST-001 to AST-003"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Asset Entry Group
        asset_group = QGroupBox("Fixed Asset Information")
        asset_group.setStyleSheet("""
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
        asset_layout = QGridLayout(asset_group)
        asset_layout.setSpacing(10)

        # Asset Code (auto-generated)
        asset_layout.addWidget(QLabel("Asset Code:"), 0, 0)
        self.asset_code_input = QLineEdit()
        self.asset_code_input.setReadOnly(True)
        self.asset_code_input.setStyleSheet("background: #F5F5F5;")
        asset_layout.addWidget(self.asset_code_input, 0, 1)

        # Asset Description
        asset_layout.addWidget(QLabel("Asset Description:"), 1, 0)
        self.asset_description_input = QLineEdit()
        self.asset_description_input.setPlaceholderText("Enter asset description...")
        asset_layout.addWidget(self.asset_description_input, 1, 1)

        # Asset Category
        asset_layout.addWidget(QLabel("Asset Category:"), 2, 0)
        self.asset_category_combo = QComboBox()
        self.asset_category_combo.addItems([
            "Land & Buildings", "Plant & Machinery", "Furniture & Fixtures", 
            "Motor Vehicles", "Computer Equipment", "Office Equipment", "Other"
        ])
        self.asset_category_combo.currentTextChanged.connect(self._on_category_changed)
        asset_layout.addWidget(self.asset_category_combo, 2, 1)

        # Asset Class (auto-populated based on category)
        asset_layout.addWidget(QLabel("Asset Class:"), 3, 0)
        self.asset_class_input = QLineEdit()
        self.asset_class_input.setReadOnly(True)
        self.asset_class_input.setStyleSheet("background: #F5F5F5;")
        asset_layout.addWidget(self.asset_class_input, 3, 1)

        # Purchase Date
        asset_layout.addWidget(QLabel("Purchase Date:"), 4, 0)
        self.purchase_date = QDateEdit()
        self.purchase_date.setDate(QDate.currentDate())
        self.purchase_date.setCalendarPopup(True)
        asset_layout.addWidget(self.purchase_date, 4, 1)

        # Cost Price
        asset_layout.addWidget(QLabel("Cost Price (excl VAT):"), 5, 0)
        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setRange(0, 999999999)
        self.cost_price_input.setDecimals(2)
        self.cost_price_input.setPrefix("R ")
        self.cost_price_input.setSingleStep(1000.00)
        self.cost_price_input.valueChanged.connect(self._calculate_vat_and_total)
        asset_layout.addWidget(self.cost_price_input, 5, 1)

        # VAT (15%)
        asset_layout.addWidget(QLabel("VAT (15%):"), 6, 0)
        self.vat_amount_input = QDoubleSpinBox()
        self.vat_amount_input.setRange(0, 999999999)
        self.vat_amount_input.setDecimals(2)
        self.vat_amount_input.setPrefix("R ")
        self.vat_amount_input.setReadOnly(True)
        self.vat_amount_input.setStyleSheet("background: #F5F5F5;")
        asset_layout.addWidget(self.vat_amount_input, 6, 1)

        # Total Cost (incl VAT)
        asset_layout.addWidget(QLabel("Total Cost (incl VAT):"), 7, 0)
        self.total_cost_input = QDoubleSpinBox()
        self.total_cost_input.setRange(0, 999999999)
        self.total_cost_input.setDecimals(2)
        self.total_cost_input.setPrefix("R ")
        self.total_cost_input.setReadOnly(True)
        self.total_cost_input.setStyleSheet("background: #F5F5F5; font-weight: bold;")
        asset_layout.addWidget(self.total_cost_input, 7, 1)

        # Useful Life (years)
        asset_layout.addWidget(QLabel("Useful Life (years):"), 8, 0)
        self.useful_life_input = QSpinBox()
        self.useful_life_input.setRange(1, 50)
        self.useful_life_input.setValue(5)  # Default 5 years
        asset_layout.addWidget(self.useful_life_input, 8, 1)

        # Depreciation Method
        asset_layout.addWidget(QLabel("Depreciation Method:"), 9, 0)
        self.depreciation_method_combo = QComboBox()
        self.depreciation_method_combo.addItems([
            "Straight Line", "Diminishing Balance", "Units of Production"
        ])
        asset_layout.addWidget(self.depreciation_method_combo, 9, 1)

        # Location
        asset_layout.addWidget(QLabel("Location:"), 10, 0)
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter asset location...")
        asset_layout.addWidget(self.location_input, 10, 1)

        # Responsible Person
        asset_layout.addWidget(QLabel("Responsible Person:"), 11, 0)
        self.responsible_person_input = QLineEdit()
        self.responsible_person_input.setPlaceholderText("Enter responsible person...")
        asset_layout.addWidget(self.responsible_person_input, 11, 1)

        # Serial Number
        asset_layout.addWidget(QLabel("Serial Number:"), 12, 0)
        self.serial_number_input = QLineEdit()
        self.serial_number_input.setPlaceholderText("Enter serial number...")
        asset_layout.addWidget(self.serial_number_input, 12, 1)

        # Status
        asset_layout.addWidget(QLabel("Status:"), 13, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "In Use", "Under Maintenance", "Sold", "Written Off", "Retired"
        ])
        asset_layout.addWidget(self.status_combo, 13, 1)

        layout.addWidget(asset_group)

        # Asset Buttons
        asset_button_layout = QHBoxLayout()
        self.add_asset_btn = QPushButton("Add Asset")
        self.add_asset_btn.clicked.connect(self._add_asset)
        self.add_asset_btn.setStyleSheet("""
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
        
        self.edit_asset_btn = QPushButton("Edit Asset")
        self.edit_asset_btn.clicked.connect(self._edit_asset)
        self.edit_asset_btn.setStyleSheet("""
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
        
        self.delete_asset_btn = QPushButton("Delete Asset")
        self.delete_asset_btn.clicked.connect(self._delete_asset)
        self.delete_asset_btn.setStyleSheet("""
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
        
        self.clear_asset_btn = QPushButton("Clear Form")
        self.clear_asset_btn.clicked.connect(self._clear_asset_form)
        self.clear_asset_btn.setStyleSheet("""
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
        
        asset_button_layout.addWidget(self.add_asset_btn)
        asset_button_layout.addWidget(self.edit_asset_btn)
        asset_button_layout.addWidget(self.delete_asset_btn)
        asset_button_layout.addWidget(self.clear_asset_btn)
        asset_button_layout.addStretch()
        layout.addLayout(asset_button_layout)

        # Assets Table
        assets_table_group = QGroupBox("Fixed Assets Register")
        assets_table_layout = QVBoxLayout(assets_table_group)
        
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(9)
        self.assets_table.setHorizontalHeaderLabels([
            "Code", "Description", "Category", "Purchase Date", "Cost", 
            "Accumulated Depreciation", "Net Book Value", "Status", "Actions"
        ])
        
        # Style table
        header = self.assets_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.assets_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.assets_table.verticalHeader().setDefaultSectionSize(40)
        assets_table_layout.addWidget(self.assets_table)
        
        layout.addWidget(assets_table_group)
        layout.addStretch()

        # Generate initial asset code and set defaults
        self._generate_asset_code()
        self._on_category_changed()
        self._calculate_vat_and_total()

        return tab

    def _create_transactions_tab(self):
        """Create asset transactions tab - AST-004"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Transaction Entry Group
        transaction_group = QGroupBox("Asset Transaction")
        transaction_layout = QGridLayout(transaction_group)
        transaction_layout.setSpacing(10)

        # Asset Selection
        transaction_layout.addWidget(QLabel("Asset:"), 0, 0)
        self.transaction_asset_combo = QComboBox()
        self._populate_transaction_asset_combo()
        transaction_layout.addWidget(self.transaction_asset_combo, 0, 1)

        # Transaction Type
        transaction_layout.addWidget(QLabel("Transaction Type:"), 1, 0)
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.addItems([
            "Purchase", "Sale", "Disposal", "Write Off", "Revaluation"
        ])
        transaction_layout.addWidget(self.transaction_type_combo, 1, 1)

        # Transaction Date
        transaction_layout.addWidget(QLabel("Date:"), 2, 0)
        self.transaction_date = QDateEdit()
        self.transaction_date.setDate(QDate.currentDate())
        self.transaction_date.setCalendarPopup(True)
        transaction_layout.addWidget(self.transaction_date, 2, 1)

        # Amount
        transaction_layout.addWidget(QLabel("Amount:"), 3, 0)
        self.transaction_amount = QDoubleSpinBox()
        self.transaction_amount.setRange(0, 999999999)
        self.transaction_amount.setDecimals(2)
        self.transaction_amount.setPrefix("R ")
        self.transaction_amount.setSingleStep(1000.00)
        transaction_layout.addWidget(self.transaction_amount, 3, 1)

        # Reference
        transaction_layout.addWidget(QLabel("Reference:"), 4, 0)
        self.transaction_reference = QLineEdit()
        self.transaction_reference.setPlaceholderText("Enter reference...")
        transaction_layout.addWidget(self.transaction_reference, 4, 1)

        # Notes
        transaction_layout.addWidget(QLabel("Notes:"), 5, 0)
        self.transaction_notes = QTextEdit()
        self.transaction_notes.setMaximumHeight(60)
        self.transaction_notes.setPlaceholderText("Enter transaction notes...")
        transaction_layout.addWidget(self.transaction_notes, 5, 1)

        layout.addWidget(transaction_group)

        # Transaction Buttons
        transaction_button_layout = QHBoxLayout()
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
        
        transaction_button_layout.addWidget(self.post_transaction_btn)
        transaction_button_layout.addWidget(self.clear_transaction_btn)
        transaction_button_layout.addStretch()
        layout.addLayout(transaction_button_layout)

        # Transactions Table
        transactions_table_group = QGroupBox("Asset Transactions")
        transactions_table_layout = QVBoxLayout(transactions_table_group)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Asset", "Type", "Amount", "Reference", "Notes"
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
        transactions_table_layout.addWidget(self.transactions_table)
        
        layout.addWidget(transactions_table_group)
        layout.addStretch()

        return tab

    def _create_depreciation_tab(self):
        """Create depreciation tab - AST-005 to AST-007"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Depreciation Processing
        depreciation_group = QGroupBox("Depreciation Processing")
        depreciation_layout = QGridLayout(depreciation_group)
        depreciation_layout.setSpacing(10)

        # Depreciation Period
        depreciation_layout.addWidget(QLabel("Depreciation Period:"), 0, 0)
        self.depreciation_period_combo = QComboBox()
        self.depreciation_period_combo.addItems([
            "January 2024", "February 2024", "March 2024", "April 2024",
            "May 2024", "June 2024", "July 2024", "August 2024",
            "September 2024", "October 2024", "November 2024", "December 2024"
        ])
        depreciation_layout.addWidget(self.depreciation_period_combo, 0, 1)

        # Process Depreciation Button
        self.process_depreciation_btn = QPushButton("Process Depreciation")
        self.process_depreciation_btn.clicked.connect(self._process_depreciation)
        self.process_depreciation_btn.setStyleSheet("""
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
        depreciation_layout.addWidget(self.process_depreciation_btn, 1, 0, 1, 2)

        layout.addWidget(depreciation_group)

        # Depreciation Schedule
        depreciation_schedule_group = QGroupBox("Depreciation Schedule")
        depreciation_schedule_layout = QVBoxLayout(depreciation_schedule_group)
        
        self.depreciation_table = QTableWidget()
        self.depreciation_table.setColumnCount(7)
        self.depreciation_table.setHorizontalHeaderLabels([
            "Asset", "Cost", "Accumulated Depreciation", "NBV", 
            "Annual Depreciation", "Monthly Depreciation", "Remaining Life"
        ])
        
        # Style table
        header = self.depreciation_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.depreciation_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.depreciation_table.verticalHeader().setDefaultSectionSize(40)
        depreciation_schedule_layout.addWidget(self.depreciation_table)
        
        layout.addWidget(depreciation_schedule_group)
        layout.addStretch()

        return tab

    def _create_reports_tab(self):
        """Create reports tab - AST-008 to AST-011"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Report Generation Group
        report_group = QGroupBox("Generate Asset Reports")
        report_layout = QGridLayout(report_group)
        report_layout.setSpacing(10)

        # Report Type
        report_layout.addWidget(QLabel("Report Type:"), 0, 0)
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Fixed Assets Register", "Asset Movement Statement", 
            "Depreciation Schedule", "AFS Note 1 - PPE"
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

    def _generate_asset_code(self):
        """Generate unique asset code"""
        existing_codes = [a["code"] for a in self.assets_data]
        prefix = "AST"
        counter = 1
        while f"{prefix}{counter:03d}" in existing_codes:
            counter += 1
        self.asset_code_input.setText(f"{prefix}{counter:03d}")

    def _on_category_changed(self):
        """Handle asset category change"""
        category = self.asset_category_combo.currentText()
        
        # Auto-populate asset class based on category
        asset_classes = {
            "Land & Buildings": "LandBuildings",
            "Plant & Machinery": "PlantMachinery",
            "Furniture & Fixtures": "FurnitureFixtures",
            "Motor Vehicles": "MotorVehicles",
            "Computer Equipment": "ComputerEquipment",
            "Office Equipment": "OfficeEquipment",
            "Other": "OtherAssets"
        }
        
        asset_class = asset_classes.get(category, "OtherAssets")
        self.asset_class_input.setText(asset_class)

    def _calculate_vat_and_total(self):
        """Calculate VAT and total cost"""
        cost_price = self.cost_price_input.value()
        vat_amount = cost_price * float(VAT_RATE)
        total_cost = cost_price + vat_amount
        
        self.vat_amount_input.setValue(vat_amount)
        self.total_cost_input.setValue(total_cost)

    def _populate_transaction_asset_combo(self):
        """Populate asset dropdown for transactions"""
        self.transaction_asset_combo.clear()
        for asset in self.assets_data:
            if asset["status"] in ["In Use", "Under Maintenance"]:  # Only active assets
                self.transaction_asset_combo.addItem(f"{asset['code']} - {asset['description']}")

    def _add_asset(self):
        """Add new asset - AST-002 to AST-003"""
        try:
            asset_code = self.asset_code_input.text().strip()
            description = self.asset_description_input.text().strip()
            category = self.asset_category_combo.currentText()
            asset_class = self.asset_class_input.text().strip()
            purchase_date = self.purchase_date.date().toString("yyyy-MM-dd")
            cost_price = self.cost_price_input.value()
            vat_amount = self.vat_amount_input.value()
            total_cost = self.total_cost_input.value()
            useful_life = self.useful_life_input.value()
            depreciation_method = self.depreciation_method_combo.currentText()
            location = self.location_input.text().strip()
            responsible_person = self.responsible_person_input.text().strip()
            serial_number = self.serial_number_input.text().strip()
            status = self.status_combo.currentText()
            
            # Validation
            if not description:
                QMessageBox.warning(self, "Validation Error", "Asset description is required")
                return
            
            if cost_price <= 0:
                QMessageBox.warning(self, "Validation Error", "Cost price must be greater than 0")
                return
            
            if useful_life <= 0:
                QMessageBox.warning(self, "Validation Error", "Useful life must be greater than 0")
                return
            
            # Check for duplicates
            for asset in self.assets_data:
                if (asset["description"].lower() == description.lower() and 
                    asset["code"] != asset_code):
                    QMessageBox.warning(self, "Duplicate Error", 
                                      "An asset with this description already exists")
                    return
                
                if asset["serial_number"] == serial_number and asset["code"] != asset_code and serial_number:
                    QMessageBox.warning(self, "Duplicate Error", 
                                      "An asset with this serial number already exists")
                    return
            
            # Create asset record
            asset = {
                "code": asset_code,
                "description": description,
                "category": category,
                "asset_class": asset_class,
                "purchase_date": purchase_date,
                "cost_price": cost_price,
                "vat_amount": vat_amount,
                "total_cost": total_cost,
                "useful_life": useful_life,
                "depreciation_method": depreciation_method,
                "accumulated_depreciation": 0.0,
                "net_book_value": total_cost,
                "location": location,
                "responsible_person": responsible_person,
                "serial_number": serial_number,
                "status": status,
                "date_created": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat()
            }
            
            self.assets_data.append(asset)
            self._save_data()
            self._refresh_assets_table()
            self._clear_asset_form()
            self._generate_asset_code()
            
            # Update transaction dropdown
            self._populate_transaction_asset_combo()
            
            QMessageBox.information(self, "Success", 
                                  f"Asset '{description}' added successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add asset: {str(e)}")

    def _edit_asset(self):
        """Edit existing asset"""
        current_row = self.assets_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", 
                              "Please select an asset to edit")
            return
        
        if current_row >= len(self.assets_data):
            return
        
        # Load asset data into form
        asset = self.assets_data[current_row]
        self.asset_code_input.setText(asset["code"])
        self.asset_description_input.setText(asset["description"])
        self.asset_category_combo.setCurrentText(asset["category"])
        self.asset_class_input.setText(asset["asset_class"])
        self.purchase_date.setDate(QDate.fromString(asset["purchase_date"], "yyyy-MM-dd"))
        self.cost_price_input.setValue(asset["cost_price"])
        self.vat_amount_input.setValue(asset["vat_amount"])
        self.total_cost_input.setValue(asset["total_cost"])
        self.useful_life_input.setValue(asset["useful_life"])
        self.depreciation_method_combo.setCurrentText(asset["depreciation_method"])
        self.location_input.setText(asset["location"])
        self.responsible_person_input.setText(asset["responsible_person"])
        self.serial_number_input.setText(asset["serial_number"])
        self.status_combo.setCurrentText(asset["status"])
        
        # Change button text to update
        self.add_asset_btn.setText("Update Asset")
        self.editing_index = current_row

    def _delete_asset(self):
        """Delete asset"""
        current_row = self.assets_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", 
                              "Please select an asset to delete")
            return
        
        if current_row >= len(self.assets_data):
            return
        
        asset = self.assets_data[current_row]
        
        # Check if asset has transactions
        asset_transactions = [t for t in self.asset_transactions_data if t["asset_code"] == asset["code"]]
        if asset_transactions:
            QMessageBox.warning(self, "Cannot Delete", 
                              f"Asset '{asset['description']}' has {len(asset_transactions)} transactions. Cannot delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete asset '{asset['description']}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.assets_data[current_row]
            self._save_data()
            self._refresh_assets_table()
            self._clear_asset_form()
            self._generate_asset_code()
            
            # Update transaction dropdown
            self._populate_transaction_asset_combo()

    def _post_transaction(self):
        """Post asset transaction - AST-004: Asset Posting with CCE Cumulative Fix"""
        try:
            asset_text = self.transaction_asset_combo.currentText()
            if not asset_text:
                QMessageBox.warning(self, "Validation Error", "Please select an asset")
                return
            
            asset_code = asset_text.split(" - ")[0]
            transaction_type = self.transaction_type_combo.currentText()
            transaction_date = self.transaction_date.date().toString("yyyy-MM-dd")
            amount = self.transaction_amount.value()
            reference = self.transaction_reference.text().strip()
            notes = self.transaction_notes.toPlainText().strip()
            
            if amount <= 0:
                QMessageBox.warning(self, "Validation Error", "Amount must be greater than 0")
                return
            
            # Find asset
            asset = None
            for a in self.assets_data:
                if a["code"] == asset_code:
                    asset = a
                    break
            
            if not asset:
                QMessageBox.warning(self, "Error", "Asset not found")
                return
            
            # Create transaction record
            transaction = {
                "asset_code": asset_code,
                "transaction_type": transaction_type,
                "transaction_date": transaction_date,
                "amount": amount,
                "reference": reference,
                "notes": notes,
                "timestamp": datetime.now().isoformat()
            }
            
            # Post to ledger using CCE cumulative update - AST-004 requires CCE cumulative fix
            if self.ledger and transaction_type == "Purchase":
                # Create journal entry for asset purchase with proper double-entry
                lines = [
                    {
                        "account_code": "1300",  # Fixed Assets (PPE)
                        "debit": asset["cost_price"],  # Net cost (excl VAT)
                        "credit": 0,
                        "notes": f"Purchase of {asset['description']} - {reference}"
                    },
                    {
                        "account_code": "1500",  # VAT Input
                        "debit": asset["vat_amount"],  # VAT amount
                        "credit": 0,
                        "notes": f"VAT on asset purchase - {asset['description']}"
                    },
                    {
                        "account_code": "1000",  # Bank FNB Cheque
                        "debit": 0,
                        "credit": asset["total_cost"],  # Total cost incl VAT
                        "notes": f"Payment for asset purchase - {asset['description']}"
                    }
                ]
                
                journal_code = self.ledger.post_journal_entry(
                    date_str=transaction_date,
                    reference=reference or "AST",
                    description=f"Asset Purchase - {asset['description']}",
                    lines=lines,
                    auto_balance=False  # Already balanced
                )
                
                transaction["journal_code"] = journal_code
                
                # Apply CCE cumulative update for cash outflow
                self.ledger.update_cce(-asset["total_cost"], "asset_purchase")
            
            self.asset_transactions_data.append(transaction)
            self._save_data()
            self._refresh_transactions_table()
            self._clear_transaction_form()
            
            # Request dashboard refresh
            self.dashboard_refresh_requested.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Transaction posted successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to post transaction: {str(e)}")

    def _process_depreciation(self):
        """Process depreciation for all assets - AST-005 to AST-007"""
        try:
            depreciation_period = self.depreciation_period_combo.currentText()
            
            if not depreciation_period:
                QMessageBox.warning(self, "Validation Error", "Please select a depreciation period")
                return
            
            total_depreciation = 0.0
            
            # Process depreciation for each active asset
            for asset in self.assets_data:
                if asset["status"] not in ["In Use", "Under Maintenance"]:
                    continue
                
                # Calculate annual depreciation
                if asset["depreciation_method"] == "Straight Line":
                    annual_depreciation = asset["total_cost"] / asset["useful_life"]
                elif asset["depreciation_method"] == "Diminishing Balance":
                    # Simplified diminishing balance (double declining)
                    rate = 2 / asset["useful_life"]
                    annual_depreciation = (asset["net_book_value"]) * rate
                    # Ensure we don't depreciate below zero
                    annual_depreciation = min(annual_depreciation, asset["net_book_value"])
                else:
                    annual_depreciation = asset["total_cost"] / asset["useful_life"]  # Default to straight line
                
                monthly_depreciation = annual_depreciation / 12
                
                # Update accumulated depreciation and net book value
                asset["accumulated_depreciation"] += monthly_depreciation
                asset["net_book_value"] = max(0, asset["total_cost"] - asset["accumulated_depreciation"])
                
                total_depreciation += monthly_depreciation
            
            self._save_data()
            self._refresh_assets_table()
            self._refresh_depreciation_table()
            
            # Request dashboard refresh
            self.dashboard_refresh_requested.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Depreciation for {depreciation_period} processed successfully\n"
                                  f"Total monthly depreciation: {_fmt_amount(total_depreciation)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process depreciation: {str(e)}")

    def _generate_report(self):
        """Generate asset reports - AST-008 to AST-011"""
        try:
            report_type = self.report_type_combo.currentText()
            from_date = self.report_from_date.date().toString("yyyy-MM-dd")
            to_date = self.report_to_date.date().toString("yyyy-MM-dd")
            
            if report_type == "Fixed Assets Register":
                self._generate_assets_register(from_date, to_date)
            elif report_type == "Asset Movement Statement":
                self._generate_movement_statement(from_date, to_date)
            elif report_type == "Depreciation Schedule":
                self._generate_depreciation_schedule_report(from_date, to_date)
            elif report_type == "AFS Note 1 - PPE":
                self._generate_afs_note_1(from_date, to_date)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

    def _generate_assets_register(self, from_date, to_date):
        """Generate fixed assets register - AST-008"""
        report = f"""
{'='*60}
FIXED ASSETS REGISTER
{'='*60}

Report Period: {from_date} to {to_date}

{'='*60}
ASSETS REGISTER
{'='*60}

Code  Description              Category          Purchase Date   Cost         NBV          Status
{'-'*60}
"""
        
        total_cost = 0.0
        total_nbv = 0.0
        
        for asset in self.assets_data:
            if from_date <= asset["purchase_date"] <= to_date:
                total_cost += asset["total_cost"]
                total_nbv += asset["net_book_value"]
                
                report += f"{asset['code']:5} {asset['description'][:23]:23} {asset['category'][:16]:16} {asset['purchase_date']:12} {_fmt_amount(asset['total_cost']):12} {_fmt_amount(asset['net_book_value']):12} {asset['status']:12}\n"
        
        report += f"""
{'-'*60}
Total Cost:      {_fmt_amount(total_cost):>12}
Total NBV:        {_fmt_amount(total_nbv):>12}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _generate_movement_statement(self, from_date, to_date):
        """Generate asset movement statement - AST-009"""
        report = f"""
{'='*60}
ASSET MOVEMENT STATEMENT
{'='*60}

Report Period: {from_date} to {to_date}

{'='*60}
ASSET MOVEMENTS
{'='*60}

Date        Asset                   Type        Amount        Reference
{'-'*60}
"""
        
        total_movements = 0.0
        
        for transaction in self.asset_transactions_data:
            if from_date <= transaction["transaction_date"] <= to_date:
                # Find asset description
                asset_description = "Unknown"
                for asset in self.assets_data:
                    if asset["code"] == transaction["asset_code"]:
                        asset_description = asset["description"]
                        break
                
                total_movements += transaction["amount"]
                
                report += f"{transaction['transaction_date']:12} {asset_description[:22]:22} {transaction['transaction_type'][:11]:11} {_fmt_amount(transaction['amount']):12} {transaction.get('reference', ''):12}\n"
        
        report += f"""
{'-'*60}
Total Movements: {_fmt_amount(total_movements):>15}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _generate_depreciation_schedule_report(self, from_date, to_date):
        """Generate depreciation schedule report - AST-010"""
        report = f"""
{'='*60}
DEPRECIATION SCHEDULE
{'='*60}

Report Period: {from_date} to {to_date}

{'='*60}
DEPRECIATION DETAILS
{'='*60}

Asset                   Cost         Acc Dep      NBV          Annual Dep   Monthly Dep
{'-'*60}
"""
        
        total_cost = 0.0
        total_accumulated = 0.0
        total_nbv = 0.0
        
        for asset in self.assets_data:
            if asset["status"] in ["In Use", "Under Maintenance"]:
                # Calculate depreciation
                if asset["depreciation_method"] == "Straight Line":
                    annual_depreciation = asset["total_cost"] / asset["useful_life"]
                else:
                    annual_depreciation = asset["total_cost"] / asset["useful_life"]  # Simplified
                
                monthly_depreciation = annual_depreciation / 12
                
                total_cost += asset["total_cost"]
                total_accumulated += asset["accumulated_depreciation"]
                total_nbv += asset["net_book_value"]
                
                desc = asset['description'][:22]
                cost_str = _fmt_amount(asset['total_cost'])
                acc_str = _fmt_amount(asset['accumulated_depreciation'])
                nbv_str = _fmt_amount(asset['net_book_value'])
                annual_str = _fmt_amount(annual_depreciation)
                monthly_str = _fmt_amount(monthly_depreciation)
                
                report += f"{desc} {cost_str:12} {acc_str:12} {nbv_str:12} {annual_str:12} {monthly_str:12}\n"
        
        report += f"""
{'-'*60}
Total Cost:         {_fmt_amount(total_cost):>12}
Total Accumulated:   {_fmt_amount(total_accumulated):>12}
Total NBV:           {_fmt_amount(total_nbv):>12}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _generate_afs_note_1(self, from_date, to_date):
        """Generate AFS Note 1 - PPE - AST-011"""
        report = f"""
{'='*60}
ANNUAL FINANCIAL STATEMENTS - NOTE 1
PROPERTY, PLANT & EQUIPMENT
{'='*60}

Year Ended: {to_date[:4]}

{'='*60}
1. PROPERTY, PLANT & EQUIPMENT
{'='*60}

The following movements in property, plant and equipment occurred during the year:

{'='*60}
OPENING BALANCE
{'='*60}

Asset Class             Cost         Accum Dep   NBV
{'-'*60}
"""
        
        # Group assets by category
        categories = {}
        total_cost = 0.0
        total_accumulated = 0.0
        total_nbv = 0.0
        
        for asset in self.assets_data:
            category = asset["category"]
            if category not in categories:
                categories[category] = {
                    "cost": 0.0,
                    "accumulated": 0.0,
                    "nbv": 0.0
                }
            
            categories[category]["cost"] += asset["total_cost"]
            categories[category]["accumulated"] += asset["accumulated_depreciation"]
            categories[category]["nbv"] += asset["net_book_value"]
            
            total_cost += asset["total_cost"]
            total_accumulated += asset["accumulated_depreciation"]
            total_nbv += asset["net_book_value"]
        
        for category, data in categories.items():
            cat_str = category[:22]
            cost_str = _fmt_amount(data['cost'])
            acc_str = _fmt_amount(data['accumulated'])
            nbv_str = _fmt_amount(data['nbv'])
            report += f"{cat_str} {cost_str:12} {acc_str:12} {nbv_str:12}\n"
        
        report += f"""
{'-'*60}
Total                   {_fmt_amount(total_cost):>12} {_fmt_amount(total_accumulated):>12} {_fmt_amount(total_nbv):>12}

{'='*60}
ACCOUNTING POLICIES
{'='*60}

Property, plant and equipment are stated at cost less accumulated depreciation.
Depreciation is charged using the straight-line method over the estimated useful
lives of the assets as follows:

- Land & Buildings: 50 years
- Plant & Machinery: 10 years
- Furniture & Fixtures: 5 years
- Motor Vehicles: 5 years
- Computer Equipment: 3 years
- Office Equipment: 5 years

{'='*60}
VALUATION
{'='*60}

The carrying amounts of property, plant and equipment are reviewed for impairment
when events or changes in circumstances indicate that the carrying amount may not be
recoverable.

{'='*60}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _print_report(self):
        """Print asset report"""
        report_text = self.report_preview.toPlainText()
        if not report_text.strip():
            QMessageBox.warning(self, "No Report", "Please generate a report first")
            return
        
        # In a real implementation, this would send to printer
        QMessageBox.information(self, "Print Report", 
                              "Report sent to printer (simulated)")

    def _clear_asset_form(self):
        """Clear asset form"""
        self.asset_description_input.clear()
        self.asset_category_combo.setCurrentIndex(0)
        self.cost_price_input.setValue(0)
        self.useful_life_input.setValue(5)
        self.depreciation_method_combo.setCurrentIndex(0)
        self.location_input.clear()
        self.responsible_person_input.clear()
        self.serial_number_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.add_asset_btn.setText("Add Asset")
        self.editing_index = None
        
        # Reset calculations
        self._on_category_changed()
        self._calculate_vat_and_total()

    def _clear_transaction_form(self):
        """Clear transaction form"""
        self.transaction_asset_combo.setCurrentIndex(0)
        self.transaction_type_combo.setCurrentIndex(0)
        self.transaction_amount.setValue(0)
        self.transaction_reference.clear()
        self.transaction_notes.clear()

    def _refresh_assets_table(self):
        """Refresh assets table"""
        self.assets_table.setRowCount(len(self.assets_data))
        
        for row, asset in enumerate(self.assets_data):
            self.assets_table.setItem(row, 0, QTableWidgetItem(asset["code"]))
            self.assets_table.setItem(row, 1, QTableWidgetItem(asset["description"]))
            self.assets_table.setItem(row, 2, QTableWidgetItem(asset["category"]))
            self.assets_table.setItem(row, 3, QTableWidgetItem(asset["purchase_date"]))
            self.assets_table.setItem(row, 4, QTableWidgetItem(_fmt_amount(asset["total_cost"])))
            self.assets_table.setItem(row, 5, QTableWidgetItem(_fmt_amount(asset["accumulated_depreciation"])))
            self.assets_table.setItem(row, 6, QTableWidgetItem(_fmt_amount(asset["net_book_value"])))
            
            # Status with color coding
            status_item = QTableWidgetItem(asset["status"])
            if asset["status"] == "In Use":
                status_item.setStyleSheet("color: #00B050; font-weight: bold;")
            elif asset["status"] == "Under Maintenance":
                status_item.setStyleSheet("color: #E07B00; font-weight: bold;")
            else:
                status_item.setStyleSheet("color: #D32F2F; font-weight: bold;")
            
            self.assets_table.setItem(row, 7, status_item)
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_asset(r))
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
            self.assets_table.setCellWidget(row, 8, action_btn)

    def _refresh_transactions_table(self):
        """Refresh transactions table"""
        self.transactions_table.setRowCount(len(self.asset_transactions_data))
        
        # Sort transactions by date (most recent first)
        sorted_transactions = sorted(self.asset_transactions_data, 
                                    key=lambda x: x["transaction_date"], 
                                    reverse=True)
        
        for row, transaction in enumerate(sorted_transactions):
            # Find asset description
            asset_description = "Unknown"
            for asset in self.assets_data:
                if asset["code"] == transaction["asset_code"]:
                    asset_description = asset["description"]
                    break
            
            self.transactions_table.setItem(row, 0, QTableWidgetItem(transaction["transaction_date"]))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(f"{transaction['asset_code']} - {asset_description}"))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(transaction["transaction_type"]))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(transaction["amount"])))
            self.transactions_table.setItem(row, 4, QTableWidgetItem(transaction.get("reference", "")))
            self.transactions_table.setItem(row, 5, QTableWidgetItem(transaction.get("notes", "")))

    def _refresh_depreciation_table(self):
        """Refresh depreciation table"""
        active_assets = [a for a in self.assets_data if a["status"] in ["In Use", "Under Maintenance"]]
        self.depreciation_table.setRowCount(len(active_assets))
        
        for row, asset in enumerate(active_assets):
            # Calculate depreciation
            if asset["depreciation_method"] == "Straight Line":
                annual_depreciation = asset["total_cost"] / asset["useful_life"]
            else:
                annual_depreciation = asset["total_cost"] / asset["useful_life"]  # Simplified
            
            monthly_depreciation = annual_depreciation / 12
            remaining_life = asset["net_book_value"] / annual_depreciation if annual_depreciation > 0 else 0
            
            self.depreciation_table.setItem(row, 0, QTableWidgetItem(asset["description"]))
            self.depreciation_table.setItem(row, 1, QTableWidgetItem(_fmt_amount(asset["total_cost"])))
            self.depreciation_table.setItem(row, 2, QTableWidgetItem(_fmt_amount(asset["accumulated_depreciation"])))
            self.depreciation_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(asset["net_book_value"])))
            self.depreciation_table.setItem(row, 4, QTableWidgetItem(_fmt_amount(annual_depreciation)))
            self.depreciation_table.setItem(row, 5, QTableWidgetItem(_fmt_amount(monthly_depreciation)))
            self.depreciation_table.setItem(row, 6, QTableWidgetItem(f"{remaining_life:.1f} years"))

    def _select_asset(self, row):
        """Select asset row"""
        self.assets_table.selectRow(row)

    def _save_data(self):
        """Save all data to files"""
        try:
            with open(self.assets_file, 'w') as f:
                json.dump(self.assets_data, f, indent=2)
            with open(self.asset_transactions_file, 'w') as f:
                json.dump(self.asset_transactions_data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def _load_data(self):
        """Load all data from files"""
        try:
            if self.assets_file.exists():
                with open(self.assets_file, 'r') as f:
                    self.assets_data = json.load(f)
            
            if self.asset_transactions_file.exists():
                with open(self.asset_transactions_file, 'r') as f:
                    self.asset_transactions_data = json.load(f)
                    
        except Exception as e:
            print(f"Error loading data: {e}")
            self.assets_data = []
            self.asset_transactions_data = []

    def get_assets_data(self):
        """Get assets data"""
        return self.assets_data.copy()

    def get_total_asset_value(self) -> float:
        """Get total asset value"""
        return sum(asset["net_book_value"] for asset in self.assets_data if asset["status"] in ["In Use", "Under Maintenance"])
