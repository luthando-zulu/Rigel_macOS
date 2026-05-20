#!/usr/bin/env python3
"""
Employees Module Handler
Implements EMP-001 to EMP-006 test cases for employee management functionality
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

class EmployeesHandler(QWidget):
    """Employees Module Handler - Implements EMP-001 to EMP-006"""
    
    # Signals for communication with main window
    dashboard_refresh_requested = pyqtSignal()
    navigation_requested = pyqtSignal(str)  # Page name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ledger = getattr(parent, 'ledger', None) if parent else None
        self.employees_data = []
        self.payroll_data = []
        self.editing_index = None
        
        # Data file paths
        self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.employees_file = self.data_dir / "employees.json"
        self.payroll_file = self.data_dir / "payroll.json"
        
        self._load_data()
        self._build_ui()

    def _build_ui(self):
        """Build employees UI - EMP-001: Navigation to Employees"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Employee Management")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Create tabbed interface
        tab_widget = QTabWidget()
        
        # Employees Masterfile Tab
        employees_tab = self._create_employees_tab()
        tab_widget.addTab(employees_tab, "Employees")
        
        # Payroll Tab
        payroll_tab = self._create_payroll_tab()
        tab_widget.addTab(payroll_tab, "Payroll")
        
        # Payslips Tab
        payslips_tab = self._create_payslips_tab()
        tab_widget.addTab(payslips_tab, "Payslips")
        
        layout.addWidget(tab_widget)

    def _create_employees_tab(self):
        """Create employees masterfile tab - EMP-001 to EMP-006"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Employee Entry Group
        employee_group = QGroupBox("Employee Information")
        employee_group.setStyleSheet("""
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
        employee_layout = QGridLayout(employee_group)
        employee_layout.setSpacing(10)

        # Employee Code (auto-generated)
        employee_layout.addWidget(QLabel("Employee Code:"), 0, 0)
        self.employee_code_input = QLineEdit()
        self.employee_code_input.setReadOnly(True)
        self.employee_code_input.setStyleSheet("background: #F5F5F5;")
        employee_layout.addWidget(self.employee_code_input, 0, 1)

        # Employee Name
        employee_layout.addWidget(QLabel("Employee Name:"), 1, 0)
        self.employee_name_input = QLineEdit()
        self.employee_name_input.setPlaceholderText("Enter employee name...")
        employee_layout.addWidget(self.employee_name_input, 1, 1)

        # ID Number
        employee_layout.addWidget(QLabel("ID Number:"), 2, 0)
        self.employee_id_input = QLineEdit()
        self.employee_id_input.setPlaceholderText("Enter ID number...")
        employee_layout.addWidget(self.employee_id_input, 2, 1)

        # Position/Job Title
        employee_layout.addWidget(QLabel("Position:"), 3, 0)
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Enter position/job title...")
        employee_layout.addWidget(self.position_input, 3, 1)

        # Department
        employee_layout.addWidget(QLabel("Department:"), 4, 0)
        self.department_combo = QComboBox()
        self.department_combo.addItems([
            "Management", "Finance", "Sales", "Marketing", 
            "Operations", "IT", "Human Resources", "Administration"
        ])
        employee_layout.addWidget(self.department_combo, 4, 1)

        # Employment Date
        employee_layout.addWidget(QLabel("Employment Date:"), 5, 0)
        self.employment_date = QDateEdit()
        self.employment_date.setDate(QDate.currentDate())
        self.employment_date.setCalendarPopup(True)
        employee_layout.addWidget(self.employment_date, 5, 1)

        # Contact Number
        employee_layout.addWidget(QLabel("Contact Number:"), 6, 0)
        self.contact_number_input = QLineEdit()
        self.contact_number_input.setPlaceholderText("Enter contact number...")
        employee_layout.addWidget(self.contact_number_input, 6, 1)

        # Email Address
        employee_layout.addWidget(QLabel("Email Address:"), 7, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address...")
        employee_layout.addWidget(self.email_input, 7, 1)

        # Physical Address
        employee_layout.addWidget(QLabel("Physical Address:"), 8, 0)
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        self.address_input.setPlaceholderText("Enter physical address...")
        employee_layout.addWidget(self.address_input, 8, 1)

        # Monthly Salary
        employee_layout.addWidget(QLabel("Monthly Salary:"), 9, 0)
        self.monthly_salary_input = QDoubleSpinBox()
        self.monthly_salary_input.setRange(0, 999999999)
        self.monthly_salary_input.setDecimals(2)
        self.monthly_salary_input.setPrefix("R ")
        self.monthly_salary_input.setSingleStep(1000.00)
        employee_layout.addWidget(self.monthly_salary_input, 9, 1)

        # Bank Account
        employee_layout.addWidget(QLabel("Bank Account:"), 10, 0)
        self.bank_account_input = QLineEdit()
        self.bank_account_input.setPlaceholderText("Enter bank account number...")
        employee_layout.addWidget(self.bank_account_input, 10, 1)

        # Tax Number
        employee_layout.addWidget(QLabel("Tax Number:"), 11, 0)
        self.tax_number_input = QLineEdit()
        self.tax_number_input.setPlaceholderText("Enter tax number...")
        employee_layout.addWidget(self.tax_number_input, 11, 1)

        # Employment Status
        employee_layout.addWidget(QLabel("Status:"), 12, 0)
        self.employment_status_combo = QComboBox()
        self.employment_status_combo.addItems([
            "Full-time", "Part-time", "Contract", "Temporary"
        ])
        employee_layout.addWidget(self.employment_status_combo, 12, 1)

        # Active Status
        employee_layout.addWidget(QLabel("Current Status:"), 13, 0)
        self.active_checkbox = QCheckBox("Active Employee")
        self.active_checkbox.setChecked(True)
        employee_layout.addWidget(self.active_checkbox, 13, 1)

        layout.addWidget(employee_group)

        # Employee Buttons
        employee_button_layout = QHBoxLayout()
        self.add_employee_btn = QPushButton("Add Employee")
        self.add_employee_btn.clicked.connect(self._add_employee)
        self.add_employee_btn.setStyleSheet("""
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
        
        self.edit_employee_btn = QPushButton("Edit Employee")
        self.edit_employee_btn.clicked.connect(self._edit_employee)
        self.edit_employee_btn.setStyleSheet("""
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
        
        self.delete_employee_btn = QPushButton("Delete Employee")
        self.delete_employee_btn.clicked.connect(self._delete_employee)
        self.delete_employee_btn.setStyleSheet("""
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
        
        self.clear_employee_btn = QPushButton("Clear Form")
        self.clear_employee_btn.clicked.connect(self._clear_employee_form)
        self.clear_employee_btn.setStyleSheet("""
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
        
        employee_button_layout.addWidget(self.add_employee_btn)
        employee_button_layout.addWidget(self.edit_employee_btn)
        employee_button_layout.addWidget(self.delete_employee_btn)
        employee_button_layout.addWidget(self.clear_employee_btn)
        employee_button_layout.addStretch()
        layout.addLayout(employee_button_layout)

        # Employees Table
        employees_table_group = QGroupBox("Employees Masterfile")
        employees_table_layout = QVBoxLayout(employees_table_group)
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(7)
        self.employees_table.setHorizontalHeaderLabels([
            "Code", "Name", "Position", "Department", "Salary", "Status", "Actions"
        ])
        
        # Style table
        header = self.employees_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.employees_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.employees_table.verticalHeader().setDefaultSectionSize(40)
        employees_table_layout.addWidget(self.employees_table)
        
        layout.addWidget(employees_table_group)
        layout.addStretch()

        # Generate initial employee code
        self._generate_employee_code()

        return tab

    def _create_payroll_tab(self):
        """Create payroll processing tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Payroll Processing Group
        payroll_group = QGroupBox("Payroll Processing")
        payroll_layout = QGridLayout(payroll_group)
        payroll_layout.setSpacing(10)

        # Payroll Period
        payroll_layout.addWidget(QLabel("Payroll Period:"), 0, 0)
        self.payroll_period_combo = QComboBox()
        self.payroll_period_combo.addItems([
            "January 2024", "February 2024", "March 2024", "April 2024",
            "May 2024", "June 2024", "July 2024", "August 2024",
            "September 2024", "October 2024", "November 2024", "December 2024"
        ])
        payroll_layout.addWidget(self.payroll_period_combo, 0, 1)

        # Pay Date
        payroll_layout.addWidget(QLabel("Pay Date:"), 1, 0)
        self.pay_date = QDateEdit()
        self.pay_date.setDate(QDate.currentDate())
        self.pay_date.setCalendarPopup(True)
        payroll_layout.addWidget(self.pay_date, 1, 1)

        # Process All Button
        self.process_all_payroll_btn = QPushButton("Process All Payroll")
        self.process_all_payroll_btn.clicked.connect(self._process_all_payroll)
        self.process_all_payroll_btn.setStyleSheet("""
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
        payroll_layout.addWidget(self.process_all_payroll_btn, 2, 0, 1, 2)

        layout.addWidget(payroll_group)

        # Payroll Summary
        payroll_summary_group = QGroupBox("Payroll Summary")
        payroll_summary_layout = QVBoxLayout(payroll_summary_group)
        
        self.payroll_summary_table = QTableWidget()
        self.payroll_summary_table.setColumnCount(6)
        self.payroll_summary_table.setHorizontalHeaderLabels([
            "Employee", "Gross Salary", "PAYE", "UIF", "Net Salary", "Status"
        ])
        
        # Style table
        header = self.payroll_summary_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.payroll_summary_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.payroll_summary_table.verticalHeader().setDefaultSectionSize(40)
        payroll_summary_layout.addWidget(self.payroll_summary_table)
        
        layout.addWidget(payroll_summary_group)
        layout.addStretch()

        return tab

    def _create_payslips_tab(self):
        """Create payslips tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Payslip Generation Group
        payslip_group = QGroupBox("Generate Payslip")
        payslip_layout = QGridLayout(payslip_group)
        payslip_layout.setSpacing(10)

        # Employee Selection
        payslip_layout.addWidget(QLabel("Employee:"), 0, 0)
        self.payslip_employee_combo = QComboBox()
        self._populate_payslip_employee_combo()
        payslip_layout.addWidget(self.payslip_employee_combo, 0, 1)

        # Payroll Period
        payslip_layout.addWidget(QLabel("Payroll Period:"), 1, 0)
        self.payslip_period_combo = QComboBox()
        self.payslip_period_combo.addItems([
            "January 2024", "February 2024", "March 2024", "April 2024",
            "May 2024", "June 2024", "July 2024", "August 2024",
            "September 2024", "October 2024", "November 2024", "December 2024"
        ])
        payslip_layout.addWidget(self.payslip_period_combo, 1, 1)

        # Generate Button
        self.generate_payslip_btn = QPushButton("Generate Payslip")
        self.generate_payslip_btn.clicked.connect(self._generate_payslip)
        self.generate_payslip_btn.setStyleSheet("""
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
        payslip_layout.addWidget(self.generate_payslip_btn, 2, 0, 1, 2)

        layout.addWidget(payslip_group)

        # Payslip Preview
        payslip_preview_group = QGroupBox("Payslip Preview")
        payslip_preview_layout = QVBoxLayout(payslip_preview_group)
        
        self.payslip_preview = QTextEdit()
        self.payslip_preview.setReadOnly(True)
        self.payslip_preview.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                padding: 10px;
                font-family: 'Courier New', monospace;
            }
        """)
        payslip_preview_layout.addWidget(self.payslip_preview)
        
        layout.addWidget(payslip_preview_group)
        layout.addStretch()

        return tab

    def _generate_employee_code(self):
        """Generate unique employee code"""
        existing_codes = [e["code"] for e in self.employees_data]
        prefix = "EMP"
        counter = 1
        while f"{prefix}{counter:03d}" in existing_codes:
            counter += 1
        self.employee_code_input.setText(f"{prefix}{counter:03d}")

    def _populate_payslip_employee_combo(self):
        """Populate employee dropdown for payslips"""
        self.payslip_employee_combo.clear()
        for employee in self.employees_data:
            if employee["active"]:  # Only active employees
                self.payslip_employee_combo.addItem(f"{employee['code']} - {employee['name']}")

    def _add_employee(self):
        """Add new employee - EMP-002 to EMP-006"""
        try:
            employee_code = self.employee_code_input.text().strip()
            employee_name = self.employee_name_input.text().strip()
            employee_id = self.employee_id_input.text().strip()
            position = self.position_input.text().strip()
            department = self.department_combo.currentText()
            employment_date = self.employment_date.date().toString("yyyy-MM-dd")
            contact_number = self.contact_number_input.text().strip()
            email = self.email_input.text().strip()
            address = self.address_input.toPlainText().strip()
            monthly_salary = self.monthly_salary_input.value()
            bank_account = self.bank_account_input.text().strip()
            tax_number = self.tax_number_input.text().strip()
            employment_status = self.employment_status_combo.currentText()
            active = self.active_checkbox.isChecked()
            
            # Validation
            if not employee_name:
                QMessageBox.warning(self, "Validation Error", "Employee name is required")
                return
            
            if not employee_id:
                QMessageBox.warning(self, "Validation Error", "ID number is required")
                return
            
            if monthly_salary <= 0:
                QMessageBox.warning(self, "Validation Error", "Monthly salary must be greater than 0")
                return
            
            # Check for duplicates
            for employee in self.employees_data:
                if (employee["name"].lower() == employee_name.lower() and 
                    employee["code"] != employee_code):
                    QMessageBox.warning(self, "Duplicate Error", 
                                      "An employee with this name already exists")
                    return
                
                if employee["id_number"] == employee_id and employee["code"] != employee_code:
                    QMessageBox.warning(self, "Duplicate Error", 
                                      "An employee with this ID number already exists")
                    return
            
            # Create employee record
            employee = {
                "code": employee_code,
                "name": employee_name,
                "id_number": employee_id,
                "position": position,
                "department": department,
                "employment_date": employment_date,
                "contact_number": contact_number,
                "email": email,
                "address": address,
                "monthly_salary": monthly_salary,
                "bank_account": bank_account,
                "tax_number": tax_number,
                "employment_status": employment_status,
                "active": active,
                "date_created": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat()
            }
            
            self.employees_data.append(employee)
            self._save_data()
            self._refresh_employees_table()
            self._clear_employee_form()
            self._generate_employee_code()
            
            # Update payslip dropdown
            self._populate_payslip_employee_combo()
            
            QMessageBox.information(self, "Success", 
                                  f"Employee '{employee_name}' added successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add employee: {str(e)}")

    def _edit_employee(self):
        """Edit existing employee"""
        current_row = self.employees_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", 
                              "Please select an employee to edit")
            return
        
        if current_row >= len(self.employees_data):
            return
        
        # Load employee data into form
        employee = self.employees_data[current_row]
        self.employee_code_input.setText(employee["code"])
        self.employee_name_input.setText(employee["name"])
        self.employee_id_input.setText(employee["id_number"])
        self.position_input.setText(employee["position"])
        self.department_combo.setCurrentText(employee["department"])
        self.employment_date.setDate(QDate.fromString(employee["employment_date"], "yyyy-MM-dd"))
        self.contact_number_input.setText(employee["contact_number"])
        self.email_input.setText(employee["email"])
        self.address_input.setPlainText(employee["address"])
        self.monthly_salary_input.setValue(employee["monthly_salary"])
        self.bank_account_input.setText(employee["bank_account"])
        self.tax_number_input.setText(employee["tax_number"])
        self.employment_status_combo.setCurrentText(employee["employment_status"])
        self.active_checkbox.setChecked(employee["active"])
        
        # Change button text to update
        self.add_employee_btn.setText("Update Employee")
        self.editing_index = current_row

    def _delete_employee(self):
        """Delete employee"""
        current_row = self.employees_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", 
                              "Please select an employee to delete")
            return
        
        if current_row >= len(self.employees_data):
            return
        
        employee = self.employees_data[current_row]
        
        # Check if employee has payroll records
        employee_payroll = [p for p in self.payroll_data if p["employee_code"] == employee["code"]]
        if employee_payroll:
            QMessageBox.warning(self, "Cannot Delete", 
                              f"Employee '{employee['name']}' has {len(employee_payroll)} payroll records. Cannot delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete employee '{employee['name']}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.employees_data[current_row]
            self._save_data()
            self._refresh_employees_table()
            self._clear_employee_form()
            self._generate_employee_code()
            
            # Update payslip dropdown
            self._populate_payslip_employee_combo()

    def _process_all_payroll(self):
        """Process payroll for all active employees"""
        try:
            payroll_period = self.payroll_period_combo.currentText()
            pay_date = self.pay_date.date().toString("yyyy-MM-dd")
            
            if not payroll_period:
                QMessageBox.warning(self, "Validation Error", "Please select a payroll period")
                return
            
            # Check if payroll already processed for this period
            existing_payroll = [p for p in self.payroll_data if p["payroll_period"] == payroll_period]
            if existing_payroll:
                reply = QMessageBox.question(self, "Payroll Exists", 
                                          f"Payroll for {payroll_period} has already been processed. Do you want to reprocess?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply != QMessageBox.StandardButton.Yes:
                    return
                
                # Remove existing payroll for this period
                self.payroll_data = [p for p in self.payroll_data if p["payroll_period"] != payroll_period]
            
            total_gross_salary = 0.0
            total_paye = 0.0
            total_uif = 0.0
            total_net_salary = 0.0
            
            # Process payroll for each active employee
            for employee in self.employees_data:
                if not employee["active"]:
                    continue
                
                gross_salary = employee["monthly_salary"]
                
                # Calculate PAYE (simplified - actual calculation would be more complex)
                paye = self._calculate_paye(gross_salary)
                
                # Calculate UIF (2% of gross salary, capped at certain amount)
                uif = min(gross_salary * 0.02, 148.72)  # UIF capped amount
                
                # Calculate net salary
                net_salary = gross_salary - paye - uif
                
                # Create payroll record
                payroll_record = {
                    "employee_code": employee["code"],
                    "employee_name": employee["name"],
                    "payroll_period": payroll_period,
                    "pay_date": pay_date,
                    "gross_salary": gross_salary,
                    "paye": paye,
                    "uif": uif,
                    "net_salary": net_salary,
                    "status": "Processed",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Post to ledger
                if self.ledger:
                    # Create journal entry for payroll
                    lines = [
                        {
                            "account_code": "5100",  # Operating Expenses
                            "debit": gross_salary,
                            "credit": 0,
                            "notes": f"Salary - {employee['name']} - {payroll_period}"
                        },
                        {
                            "account_code": "1000",  # Bank FNB Cheque
                            "debit": 0,
                            "credit": net_salary,
                            "notes": f"Net salary payment - {employee['name']}"
                        },
                        {
                            "account_code": "2300",  # Accrued Expenses (PAYE payable)
                            "debit": 0,
                            "credit": paye,
                            "notes": f"PAYE deduction - {employee['name']}"
                        },
                        {
                            "account_code": "2300",  # Accrued Expenses (UIF payable)
                            "debit": 0,
                            "credit": uif,
                            "notes": f"UIF deduction - {employee['name']}"
                        }
                    ]
                    
                    journal_code = self.ledger.post_journal_entry(
                        date_str=pay_date,
                        reference=f"PAY{payroll_period.replace(' ', '')}",
                        description=f"Payroll Processing - {payroll_period}",
                        lines=lines,
                        auto_balance=False  # Already balanced
                    )
                    
                    payroll_record["journal_code"] = journal_code
                    
                    # Apply CCE cumulative update for net salary payments
                    self.ledger.update_cce(-net_salary, "payroll")
                
                self.payroll_data.append(payroll_record)
                
                # Update totals
                total_gross_salary += gross_salary
                total_paye += paye
                total_uif += uif
                total_net_salary += net_salary
            
            self._save_data()
            self._refresh_payroll_summary()
            
            # Request dashboard refresh
            self.dashboard_refresh_requested.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Payroll for {payroll_period} processed successfully\n"
                                  f"Total Gross Salary: {_fmt_amount(total_gross_salary)}\n"
                                  f"Total PAYE: {_fmt_amount(total_paye)}\n"
                                  f"Total UIF: {_fmt_amount(total_uif)}\n"
                                  f"Total Net Salary: {_fmt_amount(total_net_salary)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process payroll: {str(e)}")

    def _calculate_paye(self, gross_salary):
        """Calculate PAYE (simplified South African tax calculation)"""
        # This is a simplified calculation - actual PAYE calculation would be more complex
        # and would consider tax brackets, rebates, medical aid, etc.
        
        if gross_salary <= 25000:  # Monthly equivalent of annual tax threshold
            return 0.0
        elif gross_salary <= 50000:
            return gross_salary * 0.18
        elif gross_salary <= 75000:
            return gross_salary * 0.26
        elif gross_salary <= 100000:
            return gross_salary * 0.31
        else:
            return gross_salary * 0.36

    def _generate_payslip(self):
        """Generate payslip for selected employee"""
        try:
            employee_text = self.payslip_employee_combo.currentText()
            payroll_period = self.payslip_period_combo.currentText()
            
            if not employee_text or not payroll_period:
                QMessageBox.warning(self, "Validation Error", "Please select employee and payroll period")
                return
            
            employee_code = employee_text.split(" - ")[0]
            
            # Find employee
            employee = None
            for e in self.employees_data:
                if e["code"] == employee_code:
                    employee = e
                    break
            
            if not employee:
                QMessageBox.warning(self, "Error", "Employee not found")
                return
            
            # Find payroll record
            payroll_record = None
            for p in self.payroll_data:
                if p["employee_code"] == employee_code and p["payroll_period"] == payroll_period:
                    payroll_record = p
                    break
            
            if not payroll_record:
                QMessageBox.warning(self, "Error", f"No payroll record found for {payroll_period}")
                return
            
            # Generate payslip content
            payslip = f"""
{'='*60}
PAYSLIP
{'='*60}

Employee: {employee['name']} ({employee['code']})
ID Number: {employee['id_number']}
Position: {employee['position']}
Department: {employee['department']}

Payroll Period: {payroll_period}
Pay Date: {payroll_record['pay_date']}

{'='*60}
EARNINGS
{'='*60}

Basic Salary:                 {_fmt_amount(payroll_record['gross_salary']):>15}

{'='*60}
DEDUCTIONS
{'='*60}

PAYE (Tax):                    {_fmt_amount(payroll_record['paye']):>15}
UIF Contribution:              {_fmt_amount(payroll_record['uif']):>15}

{'='*60}
SUMMARY
{'='*60}

Gross Salary:                  {_fmt_amount(payroll_record['gross_salary']):>15}
Total Deductions:              {_fmt_amount(payroll_record['paye'] + payroll_record['uif']):>15}
Net Salary:                    {_fmt_amount(payroll_record['net_salary']):>15}

{'='*60}
PAYMENT DETAILS
{'='*60}

Bank Account: {employee['bank_account']}
Payment Method: EFT

{'='*60}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
            
            self.payslip_preview.setPlainText(payslip)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate payslip: {str(e)}")

    def _clear_employee_form(self):
        """Clear employee form"""
        self.employee_name_input.clear()
        self.employee_id_input.clear()
        self.position_input.clear()
        self.department_combo.setCurrentIndex(0)
        self.contact_number_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.monthly_salary_input.setValue(0)
        self.bank_account_input.clear()
        self.tax_number_input.clear()
        self.employment_status_combo.setCurrentIndex(0)
        self.active_checkbox.setChecked(True)
        self.add_employee_btn.setText("Add Employee")
        self.editing_index = None

    def _refresh_employees_table(self):
        """Refresh employees table"""
        self.employees_table.setRowCount(len(self.employees_data))
        
        for row, employee in enumerate(self.employees_data):
            self.employees_table.setItem(row, 0, QTableWidgetItem(employee["code"]))
            self.employees_table.setItem(row, 1, QTableWidgetItem(employee["name"]))
            self.employees_table.setItem(row, 2, QTableWidgetItem(employee["position"]))
            self.employees_table.setItem(row, 3, QTableWidgetItem(employee["department"]))
            self.employees_table.setItem(row, 4, QTableWidgetItem(_fmt_amount(employee["monthly_salary"])))
            
            # Status with color coding
            status_text = f"{employee['employment_status']} ({'Active' if employee['active'] else 'Inactive'})"
            status_item = QTableWidgetItem(status_text)
            if employee["active"]:
                status_item.setStyleSheet("color: #00B050; font-weight: bold;")
            else:
                status_item.setStyleSheet("color: #D32F2F; font-weight: bold;")
            
            self.employees_table.setItem(row, 5, status_item)
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_employee(r))
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
            self.employees_table.setCellWidget(row, 6, action_btn)

    def _refresh_payroll_summary(self):
        """Refresh payroll summary table"""
        payroll_period = self.payroll_period_combo.currentText()
        period_payroll = [p for p in self.payroll_data if p["payroll_period"] == payroll_period]
        
        self.payroll_summary_table.setRowCount(len(period_payroll))
        
        for row, payroll in enumerate(period_payroll):
            self.payroll_summary_table.setItem(row, 0, QTableWidgetItem(payroll["employee_name"]))
            self.payroll_summary_table.setItem(row, 1, QTableWidgetItem(_fmt_amount(payroll["gross_salary"])))
            self.payroll_summary_table.setItem(row, 2, QTableWidgetItem(_fmt_amount(payroll["paye"])))
            self.payroll_summary_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(payroll["uif"])))
            self.payroll_summary_table.setItem(row, 4, QTableWidgetItem(_fmt_amount(payroll["net_salary"])))
            
            # Status with color coding
            status_item = QTableWidgetItem(payroll["status"])
            status_item.setStyleSheet("color: #00B050; font-weight: bold;")
            self.payroll_summary_table.setItem(row, 5, status_item)

    def _select_employee(self, row):
        """Select employee row"""
        self.employees_table.selectRow(row)

    def _save_data(self):
        """Save all data to files"""
        try:
            with open(self.employees_file, 'w') as f:
                json.dump(self.employees_data, f, indent=2)
            with open(self.payroll_file, 'w') as f:
                json.dump(self.payroll_data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def _load_data(self):
        """Load all data from files"""
        try:
            if self.employees_file.exists():
                with open(self.employees_file, 'r') as f:
                    self.employees_data = json.load(f)
            
            if self.payroll_file.exists():
                with open(self.payroll_file, 'r') as f:
                    self.payroll_data = json.load(f)
                    
        except Exception as e:
            print(f"Error loading data: {e}")
            self.employees_data = []
            self.payroll_data = []

    def get_employees_data(self):
        """Get employees data"""
        return self.employees_data.copy()

    def get_payroll_total(self, payroll_period: str = None) -> float:
        """Get total payroll for period"""
        if payroll_period:
            period_payroll = [p for p in self.payroll_data if p["payroll_period"] == payroll_period]
            return sum(p["net_salary"] for p in period_payroll)
        else:
            return sum(p["net_salary"] for p in self.payroll_data)
