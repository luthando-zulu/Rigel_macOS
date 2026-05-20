#!/usr/bin/env python3
"""
Inventories Module Handler
Implements INVMOD-001 to INVMOD-009 test cases for inventory management functionality
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

class InventoriesHandler(QWidget):
    """Inventories Module Handler - Implements INVMOD-001 to INVMOD-009"""
    
    # Signals for communication with main window
    dashboard_refresh_requested = pyqtSignal()
    navigation_requested = pyqtSignal(str)  # Page name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ledger = getattr(parent, 'ledger', None) if parent else None
        self.inventory_items_data = []
        self.inventory_transactions_data = []
        self.editing_index = None
        
        # Data file paths
        self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.inventory_items_file = self.data_dir / "inventory_items.json"
        self.inventory_transactions_file = self.data_dir / "inventory_transactions.json"
        
        self._load_data()
        self._build_ui()

    def _build_ui(self):
        """Build inventories UI - INVMOD-001: Navigation to Inventories"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Inventory Management")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Create tabbed interface
        tab_widget = QTabWidget()
        
        # Inventory Items Tab
        items_tab = self._create_items_tab()
        tab_widget.addTab(items_tab, "Inventory Items")
        
        # Transactions Tab
        transactions_tab = self._create_transactions_tab()
        tab_widget.addTab(transactions_tab, "Transactions")
        
        # Stock Movement Tab
        stock_movement_tab = self._create_stock_movement_tab()
        tab_widget.addTab(stock_movement_tab, "Stock Movement")
        
        # Valuation Tab
        valuation_tab = self._create_valuation_tab()
        tab_widget.addTab(valuation_tab, "Valuation")
        
        layout.addWidget(tab_widget)

    def _create_items_tab(self):
        """Create inventory items tab - INVMOD-001 to INVMOD-004"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Item Entry Group
        item_group = QGroupBox("Inventory Item Information")
        item_group.setStyleSheet("""
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
        item_layout = QGridLayout(item_group)
        item_layout.setSpacing(10)

        # Item Code (auto-generated)
        item_layout.addWidget(QLabel("Item Code:"), 0, 0)
        self.item_code_input = QLineEdit()
        self.item_code_input.setReadOnly(True)
        self.item_code_input.setStyleSheet("background: #F5F5F5;")
        item_layout.addWidget(self.item_code_input, 0, 1)

        # Item Description
        item_layout.addWidget(QLabel("Item Description:"), 1, 0)
        self.item_description_input = QLineEdit()
        self.item_description_input.setPlaceholderText("Enter item description...")
        item_layout.addWidget(self.item_description_input, 1, 1)

        # Category
        item_layout.addWidget(QLabel("Category:"), 2, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Raw Materials", "Work in Progress", "Finished Goods", 
            "Supplies", "Packaging Materials", "Other"
        ])
        item_layout.addWidget(self.category_combo, 2, 1)

        # Unit of Measure
        item_layout.addWidget(QLabel("Unit of Measure:"), 3, 0)
        self.uom_combo = QComboBox()
        self.uom_combo.addItems([
            "Each", "Kilogram", "Liter", "Meter", "Box", "Carton", "Pallet"
        ])
        item_layout.addWidget(self.uom_combo, 3, 1)

        # Cost Price
        item_layout.addWidget(QLabel("Cost Price:"), 4, 0)
        self.cost_price_input = QDoubleSpinBox()
        self.cost_price_input.setRange(0, 999999999)
        self.cost_price_input.setDecimals(2)
        self.cost_price_input.setPrefix("R ")
        self.cost_price_input.setSingleStep(10.00)
        item_layout.addWidget(self.cost_price_input, 4, 1)

        # Selling Price
        item_layout.addWidget(QLabel("Selling Price:"), 5, 0)
        self.selling_price_input = QDoubleSpinBox()
        self.selling_price_input.setRange(0, 999999999)
        self.selling_price_input.setDecimals(2)
        self.selling_price_input.setPrefix("R ")
        self.selling_price_input.setSingleStep(10.00)
        item_layout.addWidget(self.selling_price_input, 5, 1)

        # Reorder Level
        item_layout.addWidget(QLabel("Reorder Level:"), 6, 0)
        self.reorder_level_input = QSpinBox()
        self.reorder_level_input.setRange(0, 999999)
        item_layout.addWidget(self.reorder_level_input, 6, 1)

        # Maximum Stock
        item_layout.addWidget(QLabel("Maximum Stock:"), 7, 0)
        self.max_stock_input = QSpinBox()
        self.max_stock_input.setRange(0, 999999)
        item_layout.addWidget(self.max_stock_input, 7, 1)

        # Supplier
        item_layout.addWidget(QLabel("Preferred Supplier:"), 8, 0)
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Enter supplier name...")
        item_layout.addWidget(self.supplier_input, 8, 1)

        # Location
        item_layout.addWidget(QLabel("Storage Location:"), 9, 0)
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter storage location...")
        item_layout.addWidget(self.location_input, 9, 1)

        # Active Status
        item_layout.addWidget(QLabel("Status:"), 10, 0)
        self.active_checkbox = QCheckBox("Active Item")
        self.active_checkbox.setChecked(True)
        item_layout.addWidget(self.active_checkbox, 10, 1)

        layout.addWidget(item_group)

        # Item Buttons
        item_button_layout = QHBoxLayout()
        self.add_item_btn = QPushButton("Add Item")
        self.add_item_btn.clicked.connect(self._add_item)
        self.add_item_btn.setStyleSheet("""
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
        
        self.edit_item_btn = QPushButton("Edit Item")
        self.edit_item_btn.clicked.connect(self._edit_item)
        self.edit_item_btn.setStyleSheet("""
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
        
        self.delete_item_btn = QPushButton("Delete Item")
        self.delete_item_btn.clicked.connect(self._delete_item)
        self.delete_item_btn.setStyleSheet("""
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
        
        self.clear_item_btn = QPushButton("Clear Form")
        self.clear_item_btn.clicked.connect(self._clear_item_form)
        self.clear_item_btn.setStyleSheet("""
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
        
        item_button_layout.addWidget(self.add_item_btn)
        item_button_layout.addWidget(self.edit_item_btn)
        item_button_layout.addWidget(self.delete_item_btn)
        item_button_layout.addWidget(self.clear_item_btn)
        item_button_layout.addStretch()
        layout.addLayout(item_button_layout)

        # Items Table
        items_table_group = QGroupBox("Inventory Items")
        items_table_layout = QVBoxLayout(items_table_group)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(9)
        self.items_table.setHorizontalHeaderLabels([
            "Code", "Description", "Category", "Cost Price", "Selling Price", 
            "Current Stock", "Reorder Level", "Value", "Actions"
        ])
        
        # Style table
        header = self.items_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.items_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.items_table.verticalHeader().setDefaultSectionSize(40)
        items_table_layout.addWidget(self.items_table)
        
        layout.addWidget(items_table_group)
        layout.addStretch()

        # Generate initial item code
        self._generate_item_code()

        return tab

    def _create_transactions_tab(self):
        """Create inventory transactions tab - INVMOD-005 to INVMOD-007"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Transaction Entry Group
        transaction_group = QGroupBox("Inventory Transaction")
        transaction_layout = QGridLayout(transaction_group)
        transaction_layout.setSpacing(10)

        # Item Selection
        transaction_layout.addWidget(QLabel("Item:"), 0, 0)
        self.transaction_item_combo = QComboBox()
        self._populate_transaction_item_combo()
        transaction_layout.addWidget(self.transaction_item_combo, 0, 1)

        # Transaction Type
        transaction_layout.addWidget(QLabel("Transaction Type:"), 1, 0)
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.addItems([
            "Purchase", "Sale", "Return to Supplier", "Customer Return", 
            "Adjustment In", "Adjustment Out", "Transfer In", "Transfer Out"
        ])
        self.transaction_type_combo.currentTextChanged.connect(self._on_transaction_type_changed)
        transaction_layout.addWidget(self.transaction_type_combo, 1, 1)

        # Transaction Date
        transaction_layout.addWidget(QLabel("Date:"), 2, 0)
        self.transaction_date = QDateEdit()
        self.transaction_date.setDate(QDate.currentDate())
        self.transaction_date.setCalendarPopup(True)
        transaction_layout.addWidget(self.transaction_date, 2, 1)

        # Quantity
        transaction_layout.addWidget(QLabel("Quantity:"), 3, 0)
        self.transaction_quantity = QSpinBox()
        self.transaction_quantity.setRange(1, 999999)
        transaction_layout.addWidget(self.transaction_quantity, 3, 1)

        # Unit Price
        transaction_layout.addWidget(QLabel("Unit Price:"), 4, 0)
        self.unit_price_input = QDoubleSpinBox()
        self.unit_price_input.setRange(0, 999999999)
        self.unit_price_input.setDecimals(2)
        self.unit_price_input.setPrefix("R ")
        self.unit_price_input.setSingleStep(10.00)
        transaction_layout.addWidget(self.unit_price_input, 4, 1)

        # Total Value (calculated)
        transaction_layout.addWidget(QLabel("Total Value:"), 5, 0)
        self.total_value_input = QDoubleSpinBox()
        self.total_value_input.setRange(0, 999999999)
        self.total_value_input.setDecimals(2)
        self.total_value_input.setPrefix("R ")
        self.total_value_input.setReadOnly(True)
        self.total_value_input.setStyleSheet("background: #F5F5F5;")
        transaction_layout.addWidget(self.total_value_input, 5, 1)

        # Reference/Document Number
        transaction_layout.addWidget(QLabel("Reference:"), 6, 0)
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Enter reference/document number...")
        transaction_layout.addWidget(self.reference_input, 6, 1)

        # Notes
        transaction_layout.addWidget(QLabel("Notes:"), 7, 0)
        self.transaction_notes = QTextEdit()
        self.transaction_notes.setMaximumHeight(60)
        self.transaction_notes.setPlaceholderText("Enter transaction notes...")
        transaction_layout.addWidget(self.transaction_notes, 7, 1)

        layout.addWidget(transaction_group)

        # Connect quantity and price changes to calculate total
        self.transaction_quantity.valueChanged.connect(self._calculate_total_value)
        self.unit_price_input.valueChanged.connect(self._calculate_total_value)

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
        transactions_table_group = QGroupBox("Inventory Transactions")
        transactions_table_layout = QVBoxLayout(transactions_table_group)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Item", "Type", "Quantity", "Unit Price", "Total Value", "Reference"
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

    def _create_stock_movement_tab(self):
        """Create stock movement tab - INVMOD-008"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Stock Movement Summary
        movement_group = QGroupBox("Stock Movement Summary")
        movement_layout = QVBoxLayout(movement_group)
        
        self.movement_table = QTableWidget()
        self.movement_table.setColumnCount(6)
        self.movement_table.setHorizontalHeaderLabels([
            "Item Code", "Description", "Opening Stock", "In", "Out", "Closing Stock"
        ])
        
        # Style table
        header = self.movement_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.movement_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.movement_table.verticalHeader().setDefaultSectionSize(40)
        movement_layout.addWidget(self.movement_table)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        self.refresh_movement_btn = QPushButton("Refresh Movement")
        self.refresh_movement_btn.clicked.connect(self._refresh_stock_movement)
        self.refresh_movement_btn.setStyleSheet("""
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
        refresh_layout.addWidget(self.refresh_movement_btn)
        refresh_layout.addStretch()
        movement_layout.addLayout(refresh_layout)
        
        layout.addWidget(movement_group)
        layout.addStretch()

        return tab

    def _create_valuation_tab(self):
        """Create inventory valuation tab - INVMOD-009"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Valuation Summary
        valuation_group = QGroupBox("Inventory Valuation")
        valuation_layout = QVBoxLayout(valuation_group)
        
        self.valuation_table = QTableWidget()
        self.valuation_table.setColumnCount(6)
        self.valuation_table.setHorizontalHeaderLabels([
            "Category", "Item Count", "Total Quantity", "Average Cost", "Total Value", "% of Total"
        ])
        
        # Style table
        header = self.valuation_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.valuation_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.valuation_table.verticalHeader().setDefaultSectionSize(40)
        valuation_layout.addWidget(self.valuation_table)
        
        # Refresh button
        refresh_valuation_layout = QHBoxLayout()
        self.refresh_valuation_btn = QPushButton("Refresh Valuation")
        self.refresh_valuation_btn.clicked.connect(self._refresh_valuation)
        self.refresh_valuation_btn.setStyleSheet("""
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
        refresh_valuation_layout.addWidget(self.refresh_valuation_btn)
        refresh_valuation_layout.addStretch()
        valuation_layout.addLayout(refresh_valuation_layout)
        
        # Total valuation label
        self.total_valuation_label = QLabel("Total Inventory Value: R 0.00")
        self.total_valuation_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00B050; margin: 10px;")
        valuation_layout.addWidget(self.total_valuation_label)
        
        layout.addWidget(valuation_group)
        layout.addStretch()

        return tab

    def _generate_item_code(self):
        """Generate unique item code"""
        existing_codes = [i["code"] for i in self.inventory_items_data]
        prefix = "INV"
        counter = 1
        while f"{prefix}{counter:03d}" in existing_codes:
            counter += 1
        self.item_code_input.setText(f"{prefix}{counter:03d}")

    def _populate_transaction_item_combo(self):
        """Populate item dropdown for transactions"""
        self.transaction_item_combo.clear()
        for item in self.inventory_items_data:
            if item["active"]:  # Only active items
                self.transaction_item_combo.addItem(f"{item['code']} - {item['description']}")

    def _on_transaction_type_changed(self):
        """Handle transaction type change"""
        transaction_type = self.transaction_type_combo.currentText()
        
        # Set default unit price based on item cost or selling price
        if self.transaction_item_combo.currentText():
            item_text = self.transaction_item_combo.currentText()
            item_code = item_text.split(" - ")[0]
            
            for item in self.inventory_items_data:
                if item["code"] == item_code:
                    if transaction_type in ["Purchase", "Return to Supplier", "Adjustment In", "Transfer In"]:
                        self.unit_price_input.setValue(item["cost_price"])
                    else:  # Sale, Customer Return, etc.
                        self.unit_price_input.setValue(item["selling_price"])
                    break

    def _calculate_total_value(self):
        """Calculate total value from quantity and unit price"""
        quantity = self.transaction_quantity.value()
        unit_price = self.unit_price_input.value()
        total = quantity * unit_price
        self.total_value_input.setValue(total)

    def _add_item(self):
        """Add new inventory item - INVMOD-002 to INVMOD-004"""
        try:
            item_code = self.item_code_input.text().strip()
            description = self.item_description_input.text().strip()
            category = self.category_combo.currentText()
            uom = self.uom_combo.currentText()
            cost_price = self.cost_price_input.value()
            selling_price = self.selling_price_input.value()
            reorder_level = self.reorder_level_input.value()
            max_stock = self.max_stock_input.value()
            supplier = self.supplier_input.text().strip()
            location = self.location_input.text().strip()
            active = self.active_checkbox.isChecked()
            
            # Validation
            if not description:
                QMessageBox.warning(self, "Validation Error", "Item description is required")
                return
            
            if cost_price <= 0:
                QMessageBox.warning(self, "Validation Error", "Cost price must be greater than 0")
                return
            
            if selling_price <= 0:
                QMessageBox.warning(self, "Validation Error", "Selling price must be greater than 0")
                return
            
            # Check for duplicates
            for item in self.inventory_items_data:
                if (item["description"].lower() == description.lower() and 
                    item["code"] != item_code):
                    QMessageBox.warning(self, "Duplicate Error", 
                                      "An item with this description already exists")
                    return
            
            # Create item record
            item = {
                "code": item_code,
                "description": description,
                "category": category,
                "uom": uom,
                "cost_price": cost_price,
                "selling_price": selling_price,
                "current_stock": 0,
                "reorder_level": reorder_level,
                "max_stock": max_stock,
                "supplier": supplier,
                "location": location,
                "active": active,
                "date_created": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat()
            }
            
            self.inventory_items_data.append(item)
            self._save_data()
            self._refresh_items_table()
            self._clear_item_form()
            self._generate_item_code()
            
            # Update transaction dropdown
            self._populate_transaction_item_combo()
            
            QMessageBox.information(self, "Success", 
                                  f"Item '{description}' added successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add item: {str(e)}")

    def _edit_item(self):
        """Edit existing item"""
        current_row = self.items_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", 
                              "Please select an item to edit")
            return
        
        if current_row >= len(self.inventory_items_data):
            return
        
        # Load item data into form
        item = self.inventory_items_data[current_row]
        self.item_code_input.setText(item["code"])
        self.item_description_input.setText(item["description"])
        self.category_combo.setCurrentText(item["category"])
        self.uom_combo.setCurrentText(item["uom"])
        self.cost_price_input.setValue(item["cost_price"])
        self.selling_price_input.setValue(item["selling_price"])
        self.reorder_level_input.setValue(item["reorder_level"])
        self.max_stock_input.setValue(item["max_stock"])
        self.supplier_input.setText(item["supplier"])
        self.location_input.setText(item["location"])
        self.active_checkbox.setChecked(item["active"])
        
        # Change button text to update
        self.add_item_btn.setText("Update Item")
        self.editing_index = current_row

    def _delete_item(self):
        """Delete item"""
        current_row = self.items_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", 
                              "Please select an item to delete")
            return
        
        if current_row >= len(self.inventory_items_data):
            return
        
        item = self.inventory_items_data[current_row]
        
        # Check if item has transactions
        item_transactions = [t for t in self.inventory_transactions_data if t["item_code"] == item["code"]]
        if item_transactions:
            QMessageBox.warning(self, "Cannot Delete", 
                              f"Item '{item['description']}' has {len(item_transactions)} transactions. Cannot delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete item '{item['description']}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.inventory_items_data[current_row]
            self._save_data()
            self._refresh_items_table()
            self._clear_item_form()
            self._generate_item_code()
            
            # Update transaction dropdown
            self._populate_transaction_item_combo()

    def _post_transaction(self):
        """Post inventory transaction - INVMOD-005 to INVMOD-007"""
        try:
            item_text = self.transaction_item_combo.currentText()
            if not item_text:
                QMessageBox.warning(self, "Validation Error", "Please select an item")
                return
            
            item_code = item_text.split(" - ")[0]
            transaction_type = self.transaction_type_combo.currentText()
            transaction_date = self.transaction_date.date().toString("yyyy-MM-dd")
            quantity = self.transaction_quantity.value()
            unit_price = self.unit_price_input.value()
            total_value = self.total_value_input.value()
            reference = self.reference_input.text().strip()
            notes = self.transaction_notes.toPlainText().strip()
            
            if quantity <= 0:
                QMessageBox.warning(self, "Validation Error", "Quantity must be greater than 0")
                return
            
            # Find item
            item = None
            for i in self.inventory_items_data:
                if i["code"] == item_code:
                    item = i
                    break
            
            if not item:
                QMessageBox.warning(self, "Error", "Item not found")
                return
            
            # Check stock availability for outbound transactions
            if transaction_type in ["Sale", "Adjustment Out", "Transfer Out"]:
                if item["current_stock"] < quantity:
                    QMessageBox.warning(self, "Insufficient Stock", 
                                      f"Insufficient stock. Available: {item['current_stock']}, Required: {quantity}")
                    return
            
            # Create transaction record
            transaction = {
                "item_code": item_code,
                "transaction_type": transaction_type,
                "transaction_date": transaction_date,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_value": total_value,
                "reference": reference,
                "notes": notes,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update item stock
            if transaction_type in ["Purchase", "Return to Supplier", "Adjustment In", "Transfer In"]:
                item["current_stock"] += quantity
            else:  # Outbound transactions
                item["current_stock"] -= quantity
            
            # Post to ledger for financial transactions
            if self.ledger and transaction_type in ["Purchase", "Sale"]:
                if transaction_type == "Purchase":
                    # Purchase: Dr Inventory, Cr Bank
                    lines = [
                        {
                            "account_code": "1200",  # Inventory
                            "debit": total_value,
                            "credit": 0,
                            "notes": f"Purchase of {item['description']} - {reference}"
                        },
                        {
                            "account_code": "1000",  # Bank FNB Cheque
                            "debit": 0,
                            "credit": total_value,
                            "notes": f"Payment for inventory - {reference}"
                        }
                    ]
                    
                    journal_code = self.ledger.post_journal_entry(
                        date_str=transaction_date,
                        reference=reference or "PUR",
                        description=f"Inventory Purchase - {item['description']}",
                        lines=lines,
                        auto_balance=False  # Already balanced
                    )
                    
                    transaction["journal_code"] = journal_code
                    
                    # Apply CCE cumulative update
                    self.ledger.update_cce(-total_value, "inventory_purchase")
                
                elif transaction_type == "Sale":
                    # Sale: Dr Cost of Sales, Cr Inventory
                    cost_value = quantity * item["cost_price"]
                    lines = [
                        {
                            "account_code": "5000",  # Cost of Sales
                            "debit": cost_value,
                            "credit": 0,
                            "notes": f"Cost of sale - {item['description']} - {reference}"
                        },
                        {
                            "account_code": "1200",  # Inventory
                            "debit": 0,
                            "credit": cost_value,
                            "notes": f"Inventory reduction - {item['description']}"
                        }
                    ]
                    
                    journal_code = self.ledger.post_journal_entry(
                        date_str=transaction_date,
                        reference=reference or "SALE",
                        description=f"Cost of Sale - {item['description']}",
                        lines=lines,
                        auto_balance=False  # Already balanced
                    )
                    
                    transaction["journal_code"] = journal_code
            
            self.inventory_transactions_data.append(transaction)
            self._save_data()
            self._refresh_items_table()
            self._refresh_transactions_table()
            self._clear_transaction_form()
            
            # Request dashboard refresh
            self.dashboard_refresh_requested.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Transaction posted successfully. New stock level: {item['current_stock']}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to post transaction: {str(e)}")

    def _refresh_stock_movement(self):
        """Refresh stock movement summary - INVMOD-008"""
        try:
            # Calculate stock movement for each item
            movement_data = []
            
            for item in self.inventory_items_data:
                if not item["active"]:
                    continue
                
                # Calculate opening stock (simplified - current stock minus movements)
                opening_stock = item["current_stock"]
                stock_in = 0
                stock_out = 0
                
                # Calculate movements from transactions
                for transaction in self.inventory_transactions_data:
                    if transaction["item_code"] == item["code"]:
                        if transaction["transaction_type"] in ["Purchase", "Return to Supplier", "Adjustment In", "Transfer In"]:
                            stock_in += transaction["quantity"]
                            opening_stock -= transaction["quantity"]
                        else:
                            stock_out += transaction["quantity"]
                            opening_stock += transaction["quantity"]
                
                movement_data.append({
                    "item_code": item["code"],
                    "description": item["description"],
                    "opening_stock": max(0, opening_stock),
                    "stock_in": stock_in,
                    "stock_out": stock_out,
                    "closing_stock": item["current_stock"]
                })
            
            # Update movement table
            self.movement_table.setRowCount(len(movement_data))
            
            for row, data in enumerate(movement_data):
                self.movement_table.setItem(row, 0, QTableWidgetItem(data["item_code"]))
                self.movement_table.setItem(row, 1, QTableWidgetItem(data["description"]))
                self.movement_table.setItem(row, 2, QTableWidgetItem(str(data["opening_stock"])))
                self.movement_table.setItem(row, 3, QTableWidgetItem(str(data["stock_in"])))
                self.movement_table.setItem(row, 4, QTableWidgetItem(str(data["stock_out"])))
                self.movement_table.setItem(row, 5, QTableWidgetItem(str(data["closing_stock"])))
                
                # Color code low stock
                if data["closing_stock"] <= data.get("reorder_level", 0):
                    for col in range(6):
                        item = self.movement_table.item(row, col)
                        if item:
                            item.setStyleSheet("color: #E07B00; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh stock movement: {str(e)}")

    def _refresh_valuation(self):
        """Refresh inventory valuation - INVMOD-009"""
        try:
            # Calculate valuation by category
            category_data = {}
            total_value = 0.0
            
            for item in self.inventory_items_data:
                if not item["active"]:
                    continue
                
                category = item["category"]
                if category not in category_data:
                    category_data[category] = {
                        "item_count": 0,
                        "total_quantity": 0,
                        "total_value": 0.0
                    }
                
                item_value = item["current_stock"] * item["cost_price"]
                category_data[category]["item_count"] += 1
                category_data[category]["total_quantity"] += item["current_stock"]
                category_data[category]["total_value"] += item_value
                total_value += item_value
            
            # Update valuation table
            self.valuation_table.setRowCount(len(category_data))
            
            for row, (category, data) in enumerate(category_data.items()):
                avg_cost = data["total_value"] / data["total_quantity"] if data["total_quantity"] > 0 else 0
                percentage = (data["total_value"] / total_value * 100) if total_value > 0 else 0
                
                self.valuation_table.setItem(row, 0, QTableWidgetItem(category))
                self.valuation_table.setItem(row, 1, QTableWidgetItem(str(data["item_count"])))
                self.valuation_table.setItem(row, 2, QTableWidgetItem(str(data["total_quantity"])))
                self.valuation_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(avg_cost)))
                self.valuation_table.setItem(row, 4, QTableWidgetItem(_fmt_amount(data["total_value"])))
                self.valuation_table.setItem(row, 5, QTableWidgetItem(f"{percentage:.1f}%"))
            
            # Update total valuation label
            self.total_valuation_label.setText(f"Total Inventory Value: {_fmt_amount(total_value)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh valuation: {str(e)}")

    def _clear_item_form(self):
        """Clear item form"""
        self.item_description_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.uom_combo.setCurrentIndex(0)
        self.cost_price_input.setValue(0)
        self.selling_price_input.setValue(0)
        self.reorder_level_input.setValue(0)
        self.max_stock_input.setValue(0)
        self.supplier_input.clear()
        self.location_input.clear()
        self.active_checkbox.setChecked(True)
        self.add_item_btn.setText("Add Item")
        self.editing_index = None

    def _clear_transaction_form(self):
        """Clear transaction form"""
        self.transaction_item_combo.setCurrentIndex(0)
        self.transaction_type_combo.setCurrentIndex(0)
        self.transaction_quantity.setValue(1)
        self.unit_price_input.setValue(0)
        self.total_value_input.setValue(0)
        self.reference_input.clear()
        self.transaction_notes.clear()

    def _refresh_items_table(self):
        """Refresh items table"""
        self.items_table.setRowCount(len(self.inventory_items_data))
        
        for row, item in enumerate(self.inventory_items_data):
            self.items_table.setItem(row, 0, QTableWidgetItem(item["code"]))
            self.items_table.setItem(row, 1, QTableWidgetItem(item["description"]))
            self.items_table.setItem(row, 2, QTableWidgetItem(item["category"]))
            self.items_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(item["cost_price"])))
            self.items_table.setItem(row, 4, QTableWidgetItem(_fmt_amount(item["selling_price"])))
            self.items_table.setItem(row, 5, QTableWidgetItem(str(item["current_stock"])))
            self.items_table.setItem(row, 6, QTableWidgetItem(str(item["reorder_level"])))
            
            # Calculate current value
            current_value = item["current_stock"] * item["cost_price"]
            value_item = QTableWidgetItem(_fmt_amount(current_value))
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            # Color code low stock
            if item["current_stock"] <= item["reorder_level"] and item["current_stock"] > 0:
                value_item.setStyleSheet("color: #E07B00; font-weight: bold;")
            elif item["current_stock"] == 0:
                value_item.setStyleSheet("color: #D32F2F; font-weight: bold;")
            else:
                value_item.setStyleSheet("color: #00B050;")
            
            self.items_table.setItem(row, 7, value_item)
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_item(r))
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
            self.items_table.setCellWidget(row, 8, action_btn)

    def _refresh_transactions_table(self):
        """Refresh transactions table"""
        self.transactions_table.setRowCount(len(self.inventory_transactions_data))
        
        # Sort transactions by date (most recent first)
        sorted_transactions = sorted(self.inventory_transactions_data, 
                                    key=lambda x: x["transaction_date"], 
                                    reverse=True)
        
        for row, transaction in enumerate(sorted_transactions):
            # Find item description
            item_description = "Unknown"
            for item in self.inventory_items_data:
                if item["code"] == transaction["item_code"]:
                    item_description = item["description"]
                    break
            
            self.transactions_table.setItem(row, 0, QTableWidgetItem(transaction["transaction_date"]))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(f"{transaction['item_code']} - {item_description}"))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(transaction["transaction_type"]))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(str(transaction["quantity"])))
            self.transactions_table.setItem(row, 4, QTableWidgetItem(_fmt_amount(transaction["unit_price"])))
            self.transactions_table.setItem(row, 5, QTableWidgetItem(_fmt_amount(transaction["total_value"])))
            self.transactions_table.setItem(row, 6, QTableWidgetItem(transaction.get("reference", "")))

    def _select_item(self, row):
        """Select item row"""
        self.items_table.selectRow(row)

    def _save_data(self):
        """Save all data to files"""
        try:
            with open(self.inventory_items_file, 'w') as f:
                json.dump(self.inventory_items_data, f, indent=2)
            with open(self.inventory_transactions_file, 'w') as f:
                json.dump(self.inventory_transactions_data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def _load_data(self):
        """Load all data from files"""
        try:
            if self.inventory_items_file.exists():
                with open(self.inventory_items_file, 'r') as f:
                    self.inventory_items_data = json.load(f)
            
            if self.inventory_transactions_file.exists():
                with open(self.inventory_transactions_file, 'r') as f:
                    self.inventory_transactions_data = json.load(f)
                    
        except Exception as e:
            print(f"Error loading data: {e}")
            self.inventory_items_data = []
            self.inventory_transactions_data = []

    def get_inventory_items_data(self):
        """Get inventory items data"""
        return self.inventory_items_data.copy()

    def get_inventory_value(self) -> float:
        """Get total inventory value"""
        total_value = 0.0
        for item in self.inventory_items_data:
            if item["active"]:
                total_value += item["current_stock"] * item["cost_price"]
        return total_value
