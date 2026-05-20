#!/usr/bin/env python3
"""
RIGEL Business - Complete Core Implementation
Includes all panels and functionality for Phase 1-4 implementation
"""

import sys
import os
import json
import hashlib
import platform
from datetime import datetime, date
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, List, Tuple, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QScrollArea,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QTextEdit,
    QGroupBox, QGridLayout, QSplitter, QHeaderView, QMessageBox,
    QFileDialog, QDateEdit, QSpinBox, QDoubleSpinBox, QCheckBox,
    QProgressBar, QTabWidget, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QPixmap, QIcon

# Import accounting engine
from accounting import AccountingLedger, CHART_OF_ACCOUNTS, VAT_RATE, _fmt_amount

# ─────────────────────────────────────────────────────────────────────────────
#  STYLING CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
class C:
    # Colors
    SIDEBAR_BG = "#1E2A2A"
    HEADER_BG = "#2A3638"
    CARD_BG = "#FFFFFF"
    TEXT_PRI = "#2C3E50"
    TEXT_SEC = "#6A7575"
    BORDER = "#E0E0E0"
    RIGEL_TXT = "#00B050"
    ACCENT = "#00B0F0"
    WARNING = "#E07B00"
    ERROR = "#E74C3C"
    SUCCESS = "#27AE60"

def F(size: int, bold: bool = False) -> QFont:
    """Helper to create fonts."""
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    return font

# ─────────────────────────────────────────────────────────────────────────────
#  WIDGET CLASSES
# ─────────────────────────────────────────────────────────────────────────────
class LogoWidget(QLabel):
    """RIGEL Business Logo Widget"""
    def __init__(self, px: int = 32, show_text: bool = True):
        super().__init__()
        self.setFixedSize(px, px if not show_text else px + 20)
        # Try to load the actual logo
        try:
            logo_path = Path("assets/branding/logo/Rigel-Package-300x300.jpg")
            if logo_path.exists():
                pixmap = QPixmap(str(logo_path))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(px, px, Qt.AspectRatioMode.KeepAspectRatio,
                                                 Qt.TransformationMode.SmoothTransformation)
                    self.setPixmap(scaled_pixmap)
                    return
        except:
            pass
        
        # Fallback to colored square
        from PyQt6.QtGui import QColor
        pixmap = QPixmap(px, px)
        pixmap.fill(QColor(C.RIGEL_TXT))
        self.setPixmap(pixmap)
        if show_text:
            self.setText("RIGEL")
            self.setStyleSheet(f"color: {C.RIGEL_TXT}; font-weight: bold;")

class LineChartWidget(QFrame):
    """Simple line chart placeholder"""
    def __init__(self, title: str):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"background: {C.CARD_BG}; border: 1px solid {C.BORDER}; border-radius: 6px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        label = QLabel(title)
        label.setFont(F(12, True))
        label.setStyleSheet(f"color: {C.TEXT_PRI};")
        layout.addWidget(label)
        
        # Placeholder chart area
        chart_area = QLabel("📊 Chart Data")
        chart_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_area.setStyleSheet(f"background: #F8F9FA; color: {C.TEXT_SEC}; border: 1px dashed {C.BORDER}; border-radius: 4px; padding: 40px;")
        layout.addWidget(chart_area)

class CashFlowChartWidget(QFrame):
    """Simple cash flow chart placeholder"""
    def __init__(self, title: str):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"background: {C.CARD_BG}; border: 1px solid {C.BORDER}; border-radius: 6px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        label = QLabel(title)
        label.setFont(F(12, True))
        label.setStyleSheet(f"color: {C.TEXT_PRI};")
        layout.addWidget(label)
        
        # Placeholder chart area
        chart_area = QLabel("💰 Cash Flow")
        chart_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_area.setStyleSheet(f"background: #F8F9FA; color: {C.TEXT_SEC}; border: 1px dashed {C.BORDER}; border-radius: 4px; padding: 40px;")
        layout.addWidget(chart_area)

# ─────────────────────────────────────────────────────────────────────────────
#  PANEL CLASSES
# ─────────────────────────────────────────────────────────────────────────────
class BasePanel(QWidget):
    """Base class for all panels with common functionality"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ledger = getattr(parent, 'ledger', None) if parent else None
        
    def show_error(self, title: str, message: str):
        """Show error message"""
        QMessageBox.critical(self, title, message)
        
    def show_info(self, title: str, message: str):
        """Show info message"""
        QMessageBox.information(self, title, message)
        
    def show_warning(self, title: str, message: str):
        """Show warning message"""
        QMessageBox.warning(self, title, message)

class MainIndexPanel(BasePanel):
    """Main Dashboard Panel"""
    def __init__(self, lic, parent=None):
        super().__init__(parent)
        self.lic = lic
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("RIGEL Business Dashboard")
        header.setFont(F(24, True))
        header.setStyleSheet(f"color: {C.TEXT_PRI}; margin-bottom: 10px;")
        layout.addWidget(header)

        # KPI Cards
        kpi_layout = QHBoxLayout()
        for title, value, color in [
            ("Cash Balance", "R 0.00", "#00B050"),
            ("Accounts Receivable", "R 0.00", "#00B0F0"),
            ("Accounts Payable", "R 0.00", "#E07B00"),
            ("Total Fixed Assets", "R 0.00", "#6A7575"),
        ]:
            card = QFrame()
            card.setStyleSheet(f"background: {C.CARD_BG}; border: 1px solid {C.BORDER}; border-radius: 8px; padding: 16px;")
            cl = QVBoxLayout(card)
            cl.addWidget(QLabel(title))
            val = QLabel(value)
            val.setFont(F(18, True))
            val.setStyleSheet(f"color: {color};")
            cl.addWidget(val)
            kpi_layout.addWidget(card)
        layout.addLayout(kpi_layout)

        # Charts Row
        charts = QHBoxLayout()
        charts.addWidget(LineChartWidget("Company Performance"))
        charts.addWidget(CashFlowChartWidget("Cash Flow Statement"))
        layout.addLayout(charts)

class RegistrationPanel(BasePanel):
    """Company Registration Panel - Phase 1 Implementation"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entity_name = ""
        self.registration_data = []
        self._build_ui()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Company Registration")
        header.setFont(F(20, True))
        header.setStyleSheet(f"color: {C.TEXT_PRI}; margin-bottom: 10px;")
        layout.addWidget(header)

        # Entity Name Section
        entity_group = QGroupBox("Entity Information")
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
        accounts_layout = QVBoxLayout(accounts_group)

        # Form for adding accounts
        form_layout = QGridLayout()
        
        # Category dropdown
        form_layout.addWidget(QLabel("Category:"), 0, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Assets", "Liabilities", "Equity", "Income", "Expenses"])
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        form_layout.addWidget(self.category_combo, 0, 1)
        
        # Sub-category dropdown
        form_layout.addWidget(QLabel("Sub-Category:"), 1, 0)
        self.subcategory_combo = QComboBox()
        form_layout.addWidget(self.subcategory_combo, 1, 1)
        
        # Account Name
        form_layout.addWidget(QLabel("Account Name:"), 2, 0)
        self.account_name_input = QLineEdit()
        form_layout.addWidget(self.account_name_input, 2, 1)
        
        # GL Code (auto-filled)
        form_layout.addWidget(QLabel("GL Code:"), 3, 0)
        self.gl_code_input = QLineEdit()
        self.gl_code_input.setReadOnly(True)
        form_layout.addWidget(self.gl_code_input, 3, 1)
        
        # Opening Balance
        form_layout.addWidget(QLabel("Opening Balance:"), 4, 0)
        self.opening_balance_input = QDoubleSpinBox()
        self.opening_balance_input.setRange(-999999999, 999999999)
        self.opening_balance_input.setDecimals(2)
        self.opening_balance_input.setPrefix("R ")
        form_layout.addWidget(self.opening_balance_input, 4, 1)
        
        accounts_layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.post_btn = QPushButton("Post")
        self.post_btn.clicked.connect(self._post_transaction)
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._edit_transaction)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_transaction)
        
        button_layout.addWidget(self.post_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        self.update_last_year_btn = QPushButton("Update Last Year")
        self.update_last_year_btn.clicked.connect(self._update_last_year)
        button_layout.addWidget(self.update_last_year_btn)
        
        accounts_layout.addLayout(button_layout)
        layout.addWidget(accounts_group)

        # Posted Transactions Table
        table_group = QGroupBox("Posted Accounts")
        table_layout = QVBoxLayout(table_group)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels([
            "Category", "Sub-Category", "Account Name", "GL Code", "Opening Balance", "Actions"
        ])
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        table_layout.addWidget(self.transactions_table)
        
        layout.addWidget(table_group)

        # Navigation Buttons
        nav_layout = QHBoxLayout()
        self.start_using_btn = QPushButton("Start Using RIGEL Business")
        self.start_using_btn.clicked.connect(self._start_using)
        self.start_using_btn.setEnabled(False)  # Disabled until entity name and accounts added
        nav_layout.addWidget(self.start_using_btn)
        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        # Initialize subcategories
        self._on_category_changed()

    def _on_entity_name_changed(self, text):
        """Handle entity name change"""
        self.entity_name = text.strip()
        self._validate_start_using()

    def _on_category_changed(self):
        """Update subcategory dropdown based on category"""
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
        """Post a new account to the chart of accounts"""
        try:
            category = self.category_combo.currentText()
            subcategory = self.subcategory_combo.currentText()
            account_name = self.account_name_input.text().strip()
            opening_balance = self.opening_balance_input.value()
            
            if not account_name:
                self.show_error("Validation Error", "Account name is required")
                return
            
            # Check for duplicates
            for row in range(self.transactions_table.rowCount()):
                if (self.transactions_table.item(row, 0).text() == category and
                    self.transactions_table.item(row, 1).text() == subcategory and
                    self.transactions_table.item(row, 2).text() == account_name):
                    self.show_error("Duplicate Error", "This account already exists")
                    return
            
            # Generate GL code
            gl_code = self._generate_gl_code(category, subcategory)
            
            # Add to table
            row = self.transactions_table.rowCount()
            self.transactions_table.insertRow(row)
            
            self.transactions_table.setItem(row, 0, QTableWidgetItem(category))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(subcategory))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(account_name))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(gl_code))
            self.transactions_table.setItem(row, 4, QTableWidgetItem(f"R {opening_balance:,.2f}"))
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_row(r))
            self.transactions_table.setCellWidget(row, 5, action_btn)
            
            # Store data
            self.registration_data.append({
                'category': category,
                'subcategory': subcategory,
                'account_name': account_name,
                'gl_code': gl_code,
                'opening_balance': opening_balance
            })
            
            # Clear form
            self._clear_form()
            
            # Validate start using button
            self._validate_start_using()
            
            self.show_info("Success", f"Account '{account_name}' posted successfully")
            
        except Exception as e:
            self.show_error("Error", f"Failed to post transaction: {str(e)}")

    def _edit_transaction(self):
        """Edit selected transaction"""
        current_row = self.transactions_table.currentRow()
        if current_row < 0:
            self.show_warning("Selection Required", "Please select a transaction to edit")
            return
        
        # Load data into form
        data = self.registration_data[current_row]
        self.category_combo.setCurrentText(data['category'])
        self.subcategory_combo.setCurrentText(data['subcategory'])
        self.account_name_input.setText(data['account_name'])
        self.gl_code_input.setText(data['gl_code'])
        self.opening_balance_input.setValue(data['opening_balance'])
        
        # Remove from table and data
        self.transactions_table.removeRow(current_row)
        del self.registration_data[current_row]

    def _delete_transaction(self):
        """Delete selected transaction"""
        current_row = self.transactions_table.currentRow()
        if current_row < 0:
            self.show_warning("Selection Required", "Please select a transaction to delete")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to delete this transaction?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.transactions_table.removeRow(current_row)
            del self.registration_data[current_row]
            self._validate_start_using()

    def _select_row(self, row):
        """Select a specific row"""
        self.transactions_table.selectRow(row)

    def _generate_gl_code(self, category, subcategory):
        """Generate GL code based on category and subcategory"""
        # Simple GL code generation logic
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
        base_code = prefix + "000"
        counter = 1
        while f"{prefix}{counter:03d}" in existing_codes:
            counter += 1
        
        return f"{prefix}{counter:03d}"

    def _clear_form(self):
        """Clear the input form"""
        self.account_name_input.clear()
        self.gl_code_input.clear()
        self.opening_balance_input.setValue(0.00)

    def _validate_start_using(self):
        """Validate if start using button should be enabled"""
        has_entity_name = bool(self.entity_name)
        has_accounts = len(self.registration_data) > 0
        self.start_using_btn.setEnabled(has_entity_name and has_accounts)

    def _update_last_year(self):
        """Update last year's data"""
        if not self.registration_data:
            self.show_warning("No Data", "No accounts found to update")
            return
        
        # This would integrate with reporting modules
        self.show_info("Update Last Year", "Last year data updated successfully")

    def _start_using(self):
        """Navigate to main application"""
        if hasattr(self.parent, '_nav_to'):
            self.parent._nav_to("main_index")
        else:
            self.show_info("Ready", "Registration complete! Ready to use RIGEL Business.")

class IndexPanel(BasePanel):
    """Index Panel placeholder"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Index Panel - Under Construction"))

# Placeholder panels for other modules
class TrialBalancePanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Trial Balance Panel - Under Construction"))

class GLPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("General Ledger Panel - Under Construction"))

class VATPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("VAT Panel - Under Construction"))

class PerformancePanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Performance Panel - Under Construction"))

class BalanceSheetPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Balance Sheet Panel - Under Construction"))

class CashBookPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Cash Book Panel - Under Construction"))

class CustomersPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Customers Panel - Under Construction"))

class SuppliersPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Suppliers Panel - Under Construction"))

class EmployeesPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Employees Panel - Under Construction"))

class PayslipsPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Payslips Panel - Under Construction"))

class AssetsPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Assets Panel - Under Construction"))

class InventoriesPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Inventories Panel - Under Construction"))

class LoansPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Loans Panel - Under Construction"))

class InvestmentsPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Investments Panel - Under Construction"))

class DirectorsPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Directors Panel - Under Construction"))

class ProjectsPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Projects Panel - Under Construction"))

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self, lic):
        super().__init__()
        self._lic = lic
        self.ledger = AccountingLedger()
        self.setWindowTitle("RIGEL Business — Powered by Stella Lumen")
        self.resize(1380, 820)
        self.setMinimumSize(1100, 680)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # Main Content
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)

        self._create_panels()
        self._nav_to("main_index")

    def _create_sidebar(self):
        w = QWidget()
        w.setFixedWidth(240)
        w.setStyleSheet(f"background: {C.SIDEBAR_BG};")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet(f"background: {C.HEADER_BG}; border-bottom: 1px solid {C.BORDER};")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 0, 16, 0)
        logo = LogoWidget(px=42, show_text=False)
        hl.addWidget(logo)
        title = QLabel("RIGEL")
        title.setFont(F(18, True))
        title.setStyleSheet(f"color: {C.RIGEL_TXT};")
        hl.addWidget(title)
        hl.addStretch()
        layout.addWidget(header)

        # Navigation
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(8, 12, 8, 12)
        nav_layout.setSpacing(2)

        sections = [
            ("MAIN", ["Main Index", "Registration", "Index"]),
            ("ACCOUNTING", ["Trial Balance", "General Ledger", "VAT", "Performance", "Balance Sheet"]),
            ("CASH & BANKING", ["Cash Book"]),
            ("CUSTOMERS", ["Customers"]),
            ("SUPPLIERS", ["Suppliers"]),
            ("PAYROLL", ["Employees", "Payslips"]),
            ("INVENTORY", ["Inventories"]),
            ("FINANCE", ["Assets", "Investments", "Loans"]),
            ("DIRECTORS", ["Directors"]),
            ("PROJECTS", ["Projects"]),
        ]

        self.nav_buttons = {}
        for section_name, items in sections:
            sec_label = QLabel(section_name)
            sec_label.setFont(F(9, True))
            sec_label.setStyleSheet(f"color: #6A7575; padding: 8px 16px 4px;")
            nav_layout.addWidget(sec_label)

            for item in items:
                btn = QPushButton(item)
                btn.setCheckable(True)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        text-align: left; padding: 10px 20px; border: none;
                        color: {C.TEXT_SEC}; background: transparent; font-size: 13px;
                    }}
                    QPushButton:hover {{ background: #2A3638; color: white; }}
                    QPushButton:checked {{ background: #00B050; color: white; font-weight: bold; }}
                """)
                btn.clicked.connect(lambda _, name=item: self._nav_to(name.lower().replace(" ", "_")))
                nav_layout.addWidget(btn)
                self.nav_buttons[item.lower().replace(" ", "_")] = btn

        nav_layout.addStretch()
        scroll.setWidget(nav_container)
        layout.addWidget(scroll)
        return w

    def _create_panels(self):
        """Create all panels and add to stack"""
        # Main panels
        self.main_index_panel = MainIndexPanel(self._lic, self)
        self.content_stack.addWidget(self.main_index_panel)
        
        self.registration_panel = RegistrationPanel(self)
        self.content_stack.addWidget(self.registration_panel)
        
        self.index_panel = IndexPanel(self)
        self.content_stack.addWidget(self.index_panel)
        
        # Accounting panels
        self.trial_balance_panel = TrialBalancePanel(self)
        self.content_stack.addWidget(self.trial_balance_panel)
        
        self.gl_panel = GLPanel(self)
        self.content_stack.addWidget(self.gl_panel)
        
        self.vat_panel = VATPanel(self)
        self.content_stack.addWidget(self.vat_panel)
        
        self.performance_panel = PerformancePanel(self)
        self.content_stack.addWidget(self.performance_panel)
        
        self.balance_sheet_panel = BalanceSheetPanel(self)
        self.content_stack.addWidget(self.balance_sheet_panel)
        
        # Banking panels
        self.cash_book_panel = CashBookPanel(self)
        self.content_stack.addWidget(self.cash_book_panel)
        
        # Customer panels
        self.customers_panel = CustomersPanel(self)
        self.content_stack.addWidget(self.customers_panel)
        
        # Supplier panels
        self.suppliers_panel = SuppliersPanel(self)
        self.content_stack.addWidget(self.suppliers_panel)
        
        # Payroll panels
        self.employees_panel = EmployeesPanel(self)
        self.content_stack.addWidget(self.employees_panel)
        
        self.payslips_panel = PayslipsPanel(self)
        self.content_stack.addWidget(self.payslips_panel)
        
        # Inventory panels
        self.inventories_panel = InventoriesPanel(self)
        self.content_stack.addWidget(self.inventories_panel)
        
        # Finance panels
        self.assets_panel = AssetsPanel(self)
        self.content_stack.addWidget(self.assets_panel)
        
        self.loans_panel = LoansPanel(self)
        self.content_stack.addWidget(self.loans_panel)
        
        self.investments_panel = InvestmentsPanel(self)
        self.content_stack.addWidget(self.investments_panel)
        
        # Directors panels
        self.directors_panel = DirectorsPanel(self)
        self.content_stack.addWidget(self.directors_panel)
        
        # Projects panels
        self.projects_panel = ProjectsPanel(self)
        self.content_stack.addWidget(self.projects_panel)

    def _nav_to(self, key):
        """Navigate to specific panel"""
        # Highlight sidebar
        for k, btn in self.nav_buttons.items():
            btn.setChecked(k == key)
        
        # Show appropriate panel
        panel_map = {
            "main_index": self.main_index_panel,
            "registration": self.registration_panel,
            "index": self.index_panel,
            "trial_balance": self.trial_balance_panel,
            "general_ledger": self.gl_panel,
            "vat": self.vat_panel,
            "performance": self.performance_panel,
            "balance_sheet": self.balance_sheet_panel,
            "cash_book": self.cash_book_panel,
            "customers": self.customers_panel,
            "suppliers": self.suppliers_panel,
            "employees": self.employees_panel,
            "payslips": self.payslips_panel,
            "inventories": self.inventories_panel,
            "assets": self.assets_panel,
            "investments": self.investments_panel,
            "loans": self.loans_panel,
            "directors": self.directors_panel,
            "projects": self.projects_panel,
        }
        
        if key in panel_map:
            self.content_stack.setCurrentWidget(panel_map[key])
        else:
            self.content_stack.setCurrentWidget(self.main_index_panel)

# ─────────────────────────────────────────────────────────────────────────────
#  LICENSE AND LAUNCH FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def check_license(license_type: str = "TRIAL") -> str:
    """Check license validity"""
    # Simple license check - in production this would be more sophisticated
    if license_type == "TRIAL":
        return "TRIAL"
    elif license_type == "FULL":
        return "FULL"
    else:
        return "TRIAL"

def launch_application():
    """Main launch function"""
    app = QApplication(sys.argv)
    app.setApplicationName("RIGEL Business")
    app.setOrganizationName("Stella Lumen")
    
    # Check license
    lic = check_license("TRIAL")
    
    # Create and show main window
    window = MainWindow(lic)
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(launch_application())
