#!/usr/bin/env python3
"""
RIGEL Business Company Setup Module
Full company registration and setup form matching User Manual screenshots
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QGroupBox,
    QFormLayout, QScrollArea, QFrame, QMessageBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap

from core.chart_of_accounts import coa_manager

# ─────────────────────────────────────────────────────────────────────────────
#  COMPANY SETUP FORM
# ─────────────────────────────────────────────────────────────────────────────
class CompanySetupForm(QWidget):
    """Company setup form with all required fields"""

    company_saved = pyqtSignal(dict)  # Signal emitted when company is saved

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.company_data = {}
        self.load_existing_data()
        self.setup_ui()

    def setup_ui(self):
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Company Setup")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2C3E50;
        """)

        subtitle = QLabel("Configure your company information and accounting settings")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #6A7575;
        """)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Scroll area for form content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: #F8F9FA;
            }
        """)

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(25)

        # Basic Information Section
        basic_info = self.create_basic_info_section()
        form_layout.addWidget(basic_info)

        # Contact Information Section
        contact_info = self.create_contact_info_section()
        form_layout.addWidget(contact_info)

        # Business Details Section
        business_details = self.create_business_details_section()
        form_layout.addWidget(business_details)

        # Accounting Settings Section
        accounting_settings = self.create_accounting_settings_section()
        form_layout.addWidget(accounting_settings)

        # Tax Information Section
        tax_info = self.create_tax_info_section()
        form_layout.addWidget(tax_info)

        # Opening Balances Section
        opening_balances = self.create_opening_balances_section()
        form_layout.addWidget(opening_balances)

        form_layout.addStretch()

        scroll_area.setWidget(form_widget)
        main_layout.addWidget(scroll_area)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        save_button = QPushButton("Save Company")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #00A651;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #008a45;
            }
        """)
        save_button.clicked.connect(self.save_company)
        buttons_layout.addWidget(save_button)

        reset_button = QPushButton("Reset Form")
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        reset_button.clicked.connect(self.reset_form)
        buttons_layout.addWidget(reset_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
        """)
        cancel_button.clicked.connect(self.cancel_setup)
        buttons_layout.addWidget(cancel_button)

        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

    def create_basic_info_section(self) -> QGroupBox:
        """Create basic information section"""
        group = QGroupBox("Basic Information")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                border: 2px solid #00A651;
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

        layout = QFormLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(12)

        # Company name
        self.company_name = QLineEdit()
        self.company_name.setText(self.company_data.get("company_name", ""))
        self.company_name.setPlaceholderText("Enter your company name")
        self.company_name.setStyleSheet(self.get_input_style())
        layout.addRow("Company Name *:", self.company_name)

        # Trading name
        self.trading_name = QLineEdit()
        self.trading_name.setText(self.company_data.get("trading_name", ""))
        self.trading_name.setPlaceholderText("Enter trading name (if different)")
        self.trading_name.setStyleSheet(self.get_input_style())
        layout.addRow("Trading Name:", self.trading_name)

        # Registration number
        self.registration_number = QLineEdit()
        self.registration_number.setText(self.company_data.get("registration_number", ""))
        self.registration_number.setPlaceholderText("Company registration number")
        self.registration_number.setStyleSheet(self.get_input_style())
        layout.addRow("Registration Number:", self.registration_number)

        # Incorporation date
        self.incorporation_date = QDateEdit()
        incorporation_date = self.company_data.get("incorporation_date")
        if incorporation_date:
            self.incorporation_date.setDate(QDate.fromString(incorporation_date, "yyyy-MM-dd"))
        else:
            self.incorporation_date.setDate(QDate.currentDate())
        self.incorporation_date.setCalendarPopup(True)
        self.incorporation_date.setStyleSheet(self.get_input_style())
        layout.addRow("Incorporation Date:", self.incorporation_date)

        # Business type
        self.business_type = QComboBox()
        self.business_type.addItems([
            "Select Business Type",
            "Private Company",
            "Public Company",
            "Close Corporation",
            "Sole Proprietorship",
            "Partnership",
            "Non-Profit Organization",
            "Other"
        ])
        self.business_type.setCurrentText(self.company_data.get("business_type", "Select Business Type"))
        self.business_type.setStyleSheet(self.get_combo_style())
        layout.addRow("Business Type:", self.business_type)

        return group

    def create_contact_info_section(self) -> QGroupBox:
        """Create contact information section"""
        group = QGroupBox("Contact Information")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                border: 2px solid #3498DB;
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

        layout = QFormLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(12)

        # Physical address
        self.physical_address = QTextEdit()
        self.physical_address.setPlainText(self.company_data.get("physical_address", ""))
        self.physical_address.setPlaceholderText("Enter physical address")
        self.physical_address.setMaximumHeight(80)
        self.physical_address.setStyleSheet(self.get_textedit_style())
        layout.addRow("Physical Address:", self.physical_address)

        # Postal address
        self.postal_address = QTextEdit()
        self.postal_address.setPlainText(self.company_data.get("postal_address", ""))
        self.postal_address.setPlaceholderText("Enter postal address")
        self.postal_address.setMaximumHeight(80)
        self.postal_address.setStyleSheet(self.get_textedit_style())
        layout.addRow("Postal Address:", self.postal_address)

        # Phone number
        self.phone_number = QLineEdit()
        self.phone_number.setText(self.company_data.get("phone_number", ""))
        self.phone_number.setPlaceholderText("+27 XX XXX XXXX")
        self.phone_number.setStyleSheet(self.get_input_style())
        layout.addRow("Phone Number:", self.phone_number)

        # Email address
        self.email_address = QLineEdit()
        self.email_address.setText(self.company_data.get("email_address", ""))
        self.email_address.setPlaceholderText("company@example.com")
        self.email_address.setStyleSheet(self.get_input_style())
        layout.addRow("Email Address:", self.email_address)

        # Website
        self.website = QLineEdit()
        self.website.setText(self.company_data.get("website", ""))
        self.website.setPlaceholderText("www.company.com")
        self.website.setStyleSheet(self.get_input_style())
        layout.addRow("Website:", self.website)

        return group

    def create_business_details_section(self) -> QGroupBox:
        """Create business details section"""
        group = QGroupBox("Business Details")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                border: 2px solid #E74C3C;
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

        layout = QFormLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(12)

        # Industry
        self.industry = QComboBox()
        self.industry.addItems([
            "Select Industry",
            "Manufacturing",
            "Retail",
            "Wholesale",
            "Services",
            "Construction",
            "Agriculture",
            "Mining",
            "Technology",
            "Healthcare",
            "Education",
            "Other"
        ])
        self.industry.setCurrentText(self.company_data.get("industry", "Select Industry"))
        self.industry.setStyleSheet(self.get_combo_style())
        layout.addRow("Industry:", self.industry)

        # Number of employees
        self.employee_count = QComboBox()
        self.employee_count.addItems([
            "Select Employee Count",
            "1-5 employees",
            "6-10 employees",
            "11-50 employees",
            "51-100 employees",
            "101-500 employees",
            "500+ employees"
        ])
        self.employee_count.setCurrentText(self.company_data.get("employee_count", "Select Employee Count"))
        self.employee_count.setStyleSheet(self.get_combo_style())
        layout.addRow("Number of Employees:", self.employee_count)

        # Financial year end
        self.financial_year_end = QComboBox()
        months = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        self.financial_year_end.addItems(["Select Month"] + months)
        self.financial_year_end.setCurrentText(self.company_data.get("financial_year_end", "Select Month"))
        self.financial_year_end.setStyleSheet(self.get_combo_style())
        layout.addRow("Financial Year End:", self.financial_year_end)

        # Business description
        self.business_description = QTextEdit()
        self.business_description.setPlainText(self.company_data.get("business_description", ""))
        self.business_description.setPlaceholderText("Describe your business activities")
        self.business_description.setMaximumHeight(100)
        self.business_description.setStyleSheet(self.get_textedit_style())
        layout.addRow("Business Description:", self.business_description)

        return group

    def create_accounting_settings_section(self) -> QGroupBox:
        """Create accounting settings section"""
        group = QGroupBox("Accounting Settings")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                border: 2px solid #9B59B6;
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

        layout = QFormLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(12)

        # Base currency
        self.base_currency = QComboBox()
        self.base_currency.addItems(["ZAR (South African Rand)", "USD (US Dollar)", "EUR (Euro)", "GBP (British Pound)"])
        self.base_currency.setCurrentText(self.company_data.get("base_currency", "ZAR (South African Rand)"))
        self.base_currency.setStyleSheet(self.get_combo_style())
        layout.addRow("Base Currency:", self.base_currency)

        # VAT registered
        self.vat_registered = QCheckBox("Company is VAT registered")
        self.vat_registered.setChecked(self.company_data.get("vat_registered", False))
        self.vat_registered.setStyleSheet("font-weight: bold;")
        layout.addRow("", self.vat_registered)

        # VAT number (shown only if VAT registered)
        self.vat_number = QLineEdit()
        self.vat_number.setText(self.company_data.get("vat_number", ""))
        self.vat_number.setPlaceholderText("Enter VAT number")
        self.vat_number.setStyleSheet(self.get_input_style())
        self.vat_number.setEnabled(self.vat_registered.isChecked())
        layout.addRow("VAT Number:", self.vat_number)

        # Connect VAT checkbox to VAT number field
        self.vat_registered.toggled.connect(self.vat_number.setEnabled)

        # Multi-currency support
        self.multi_currency = QCheckBox("Enable multi-currency transactions")
        self.multi_currency.setChecked(self.company_data.get("multi_currency", False))
        layout.addRow("", self.multi_currency)

        return group

    def create_tax_info_section(self) -> QGroupBox:
        """Create tax information section"""
        group = QGroupBox("Tax Information")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                border: 2px solid #E67E22;
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

        layout = QFormLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(12)

        # Tax number
        self.tax_number = QLineEdit()
        self.tax_number.setText(self.company_data.get("tax_number", ""))
        self.tax_number.setPlaceholderText("Income tax reference number")
        self.tax_number.setStyleSheet(self.get_input_style())
        layout.addRow("Tax Number:", self.tax_number)

        # PAYE reference number
        self.paye_reference = QLineEdit()
        self.paye_reference.setText(self.company_data.get("paye_reference", ""))
        self.paye_reference.setPlaceholderText("PAYE reference number")
        self.paye_reference.setStyleSheet(self.get_input_style())
        layout.addRow("PAYE Reference:", self.paye_reference)

        # UIF reference number
        self.uif_reference = QLineEdit()
        self.uif_reference.setText(self.company_data.get("uif_reference", ""))
        self.uif_reference.setPlaceholderText("UIF reference number")
        self.uif_reference.setStyleSheet(self.get_input_style())
        layout.addRow("UIF Reference:", self.uif_reference)

        # SDL reference number
        self.sdl_reference = QLineEdit()
        self.sdl_reference.setText(self.company_data.get("sdl_reference", ""))
        self.sdl_reference.setPlaceholderText("SDL reference number")
        self.sdl_reference.setStyleSheet(self.get_input_style())
        layout.addRow("SDL Reference:", self.sdl_reference)

        return group

    def create_opening_balances_section(self) -> QGroupBox:
        """Create opening balances section"""
        group = QGroupBox("Opening Balances")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                border: 2px solid #27AE60;
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

        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(15)

        # Opening balances table
        self.opening_balances_table = QTableWidget()
        self.opening_balances_table.setColumnCount(3)
        self.opening_balances_table.setHorizontalHeaderLabels(["Account", "Debit Balance", "Credit Balance"])
        self.opening_balances_table.setAlternatingRowColors(True)
        self.opening_balances_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)

        # Populate with asset and liability accounts
        asset_accounts = coa_manager.get_accounts_for_dropdown("Assets")
        liability_accounts = coa_manager.get_accounts_for_dropdown("Liabilities")
        equity_accounts = coa_manager.get_accounts_for_dropdown("Equity")

        all_accounts = asset_accounts + liability_accounts + equity_accounts
        self.opening_balances_table.setRowCount(len(all_accounts))

        for row, (code, name) in enumerate(all_accounts):
            # Account name
            account_item = QTableWidgetItem(name)
            account_item.setData(Qt.ItemDataRole.UserRole, code)
            self.opening_balances_table.setItem(row, 0, account_item)

            # Debit balance
            debit_item = QTableWidgetItem("0.00")
            self.opening_balances_table.setItem(row, 1, debit_item)

            # Credit balance
            credit_item = QTableWidgetItem("0.00")
            self.opening_balances_table.setItem(row, 2, credit_item)

        # Load existing opening balances
        opening_balances = self.company_data.get("opening_balances", {})
        for row in range(self.opening_balances_table.rowCount()):
            account_item = self.opening_balances_table.item(row, 0)
            if account_item:
                account_code = account_item.data(Qt.ItemDataRole.UserRole)
                if account_code in opening_balances:
                    balances = opening_balances[account_code]
                    self.opening_balances_table.item(row, 1).setText(str(balances.get("debit", "0.00")))
                    self.opening_balances_table.item(row, 2).setText(str(balances.get("credit", "0.00")))

        self.opening_balances_table.resizeColumnsToContents()
        layout.addWidget(self.opening_balances_table)

        return group

    def get_input_style(self) -> str:
        """Get consistent input field styling"""
        return """
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #00A651;
            }
        """

    def get_combo_style(self) -> str:
        """Get consistent combobox styling"""
        return """
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
                min-width: 200px;
            }
            QComboBox:focus {
                border-color: #00A651;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """

    def get_textedit_style(self) -> str:
        """Get consistent textedit styling"""
        return """
            QTextEdit {
                padding: 8px 12px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #00A651;
            }
        """

    def load_existing_data(self):
        """Load existing company data"""
        try:
            company_file = Path("data/company.json")
            if company_file.exists():
                with open(company_file, 'r', encoding='utf-8') as f:
                    self.company_data = json.load(f)
        except Exception as e:
            print(f"Error loading company data: {e}")
            self.company_data = {}

    def save_company(self):
        """Save company information"""
        if not self.validate_form():
            return

        # Collect form data
        company_data = {
            "company_name": self.company_name.text().strip(),
            "trading_name": self.trading_name.text().strip(),
            "registration_number": self.registration_number.text().strip(),
            "incorporation_date": self.incorporation_date.date().toString("yyyy-MM-dd"),
            "business_type": self.business_type.currentText(),
            "physical_address": self.physical_address.toPlainText().strip(),
            "postal_address": self.postal_address.toPlainText().strip(),
            "phone_number": self.phone_number.text().strip(),
            "email_address": self.email_address.text().strip(),
            "website": self.website.text().strip(),
            "industry": self.industry.currentText(),
            "employee_count": self.employee_count.currentText(),
            "financial_year_end": self.financial_year_end.currentText(),
            "business_description": self.business_description.toPlainText().strip(),
            "base_currency": self.base_currency.currentText(),
            "vat_registered": self.vat_registered.isChecked(),
            "vat_number": self.vat_number.text().strip(),
            "multi_currency": self.multi_currency.isChecked(),
            "tax_number": self.tax_number.text().strip(),
            "paye_reference": self.paye_reference.text().strip(),
            "uif_reference": self.uif_reference.text().strip(),
            "sdl_reference": self.sdl_reference.text().strip(),
            "opening_balances": self.get_opening_balances(),
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }

        # Save to file
        try:
            company_file = Path("data/company.json")
            company_file.parent.mkdir(parents=True, exist_ok=True)
            with open(company_file, 'w', encoding='utf-8') as f:
                json.dump(company_data, f, indent=2, ensure_ascii=False)

            self.company_data = company_data
            self.company_saved.emit(company_data)

            QMessageBox.information(self, "Success",
                                  "Company information saved successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error",
                               f"Failed to save company information: {str(e)}")

    def get_opening_balances(self) -> Dict[str, Dict[str, float]]:
        """Get opening balances from table"""
        balances = {}

        for row in range(self.opening_balances_table.rowCount()):
            account_item = self.opening_balances_table.item(row, 0)
            debit_item = self.opening_balances_table.item(row, 1)
            credit_item = self.opening_balances_table.item(row, 2)

            if account_item and debit_item and credit_item:
                account_code = account_item.data(Qt.ItemDataRole.UserRole)
                try:
                    debit = float(debit_item.text() or "0")
                    credit = float(credit_item.text() or "0")

                    if debit != 0 or credit != 0:
                        balances[account_code] = {
                            "debit": debit,
                            "credit": credit
                        }
                except ValueError:
                    continue

        return balances

    def validate_form(self) -> bool:
        """Validate form data"""
        if not self.company_name.text().strip():
            QMessageBox.warning(self, "Validation Error",
                              "Company name is required.")
            self.company_name.setFocus()
            return False

        if self.business_type.currentText() == "Select Business Type":
            QMessageBox.warning(self, "Validation Error",
                              "Please select a business type.")
            self.business_type.setFocus()
            return False

        if not self.physical_address.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error",
                              "Physical address is required.")
            self.physical_address.setFocus()
            return False

        if self.vat_registered.isChecked() and not self.vat_number.text().strip():
            QMessageBox.warning(self, "Validation Error",
                              "VAT number is required for VAT registered companies.")
            self.vat_number.setFocus()
            return False

        return True

    def reset_form(self):
        """Reset form to default values"""
        reply = QMessageBox.question(self, "Reset Form",
                                   "Are you sure you want to reset the form? All unsaved changes will be lost.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.company_data = {}
            # Reinitialize the form
            self.setup_ui()

    def cancel_setup(self):
        """Cancel company setup"""
        reply = QMessageBox.question(self, "Cancel Setup",
                                   "Are you sure you want to cancel? Any unsaved changes will be lost.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.main_window:
                self.main_window.show_landing_page()
            else:
                self.close()

# ─────────────────────────────────────────────────────────────────────────────
#  MODULE INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────
def create_company_setup(main_window) -> CompanySetupForm:
    """Factory function to create company setup form"""
    return CompanySetupForm(main_window)

if __name__ == "__main__":
    # Test the company setup form
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Mock main window
    class MockMainWindow:
        def show_landing_page(self):
            print("Showing landing page")

    window = MockMainWindow()
    setup = create_company_setup(window)
    setup.show()

    sys.exit(app.exec())