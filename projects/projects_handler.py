#!/usr/bin/env python3
"""
Projects Module Handler
Implements PRJ-001 to PRJ-005 test cases for project management functionality
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

class ProjectsHandler(QWidget):
    """Projects Module Handler - Implements PRJ-001 to PRJ-005"""
    
    # Signals for communication with main window
    dashboard_refresh_requested = pyqtSignal()
    navigation_requested = pyqtSignal(str)  # Page name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ledger = getattr(parent, 'ledger', None) if parent else None
        self.projects_data = []
        self.project_transactions_data = []
        self.editing_index = None
        
        # Data file paths
        self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.projects_file = self.data_dir / "projects.json"
        self.project_transactions_file = self.data_dir / "project_transactions.json"
        
        self._load_data()
        self._build_ui()

    def _build_ui(self):
        """Build projects UI - PRJ-001: Navigation to Projects"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Project Management")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Create tabbed interface
        tab_widget = QTabWidget()
        
        # Projects Masterfile Tab
        projects_tab = self._create_projects_tab()
        tab_widget.addTab(projects_tab, "Projects")
        
        # Project Transactions Tab
        transactions_tab = self._create_transactions_tab()
        tab_widget.addTab(transactions_tab, "Project Transactions")
        
        # Project Reports Tab
        reports_tab = self._create_reports_tab()
        tab_widget.addTab(reports_tab, "Reports")
        
        layout.addWidget(tab_widget)

    def _create_projects_tab(self):
        """Create projects masterfile tab - PRJ-001 to PRJ-003"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Project Entry Group
        project_group = QGroupBox("Project Information")
        project_group.setStyleSheet("""
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
        project_layout = QGridLayout(project_group)
        project_layout.setSpacing(10)

        # Project Code (auto-generated)
        project_layout.addWidget(QLabel("Project Code:"), 0, 0)
        self.project_code_input = QLineEdit()
        self.project_code_input.setReadOnly(True)
        self.project_code_input.setStyleSheet("background: #F5F5F5;")
        project_layout.addWidget(self.project_code_input, 0, 1)

        # Project Name
        project_layout.addWidget(QLabel("Project Name:"), 1, 0)
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Enter project name...")
        project_layout.addWidget(self.project_name_input, 1, 1)

        # Client/Customer
        project_layout.addWidget(QLabel("Client/Customer:"), 2, 0)
        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("Enter client/customer name...")
        project_layout.addWidget(self.client_input, 2, 1)

        # Project Type
        project_layout.addWidget(QLabel("Project Type:"), 3, 0)
        self.project_type_combo = QComboBox()
        self.project_type_combo.addItems([
            "Construction", "Software Development", "Consulting", 
            "Research & Development", "Marketing Campaign", "Other"
        ])
        project_layout.addWidget(self.project_type_combo, 3, 1)

        # Start Date
        project_layout.addWidget(QLabel("Start Date:"), 4, 0)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        project_layout.addWidget(self.start_date, 4, 1)

        # End Date
        project_layout.addWidget(QLabel("End Date:"), 5, 0)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate().addMonths(6))
        self.end_date.setCalendarPopup(True)
        project_layout.addWidget(self.end_date, 5, 1)

        # Contract Value
        project_layout.addWidget(QLabel("Contract Value:"), 6, 0)
        self.contract_value_input = QDoubleSpinBox()
        self.contract_value_input.setRange(0, 999999999)
        self.contract_value_input.setDecimals(2)
        self.contract_value_input.setPrefix("R ")
        self.contract_value_input.setSingleStep(10000.00)
        project_layout.addWidget(self.contract_value_input, 6, 1)

        # Project Manager
        project_layout.addWidget(QLabel("Project Manager:"), 7, 0)
        self.project_manager_input = QLineEdit()
        self.project_manager_input.setPlaceholderText("Enter project manager name...")
        project_layout.addWidget(self.project_manager_input, 7, 1)

        # Status
        project_layout.addWidget(QLabel("Status:"), 8, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "Planning", "In Progress", "On Hold", "Completed", "Cancelled"
        ])
        project_layout.addWidget(self.status_combo, 8, 1)

        # Description
        project_layout.addWidget(QLabel("Description:"), 9, 0)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Enter project description...")
        project_layout.addWidget(self.description_input, 9, 1)

        # Budget Allocated
        project_layout.addWidget(QLabel("Budget Allocated:"), 10, 0)
        self.budget_allocated_input = QDoubleSpinBox()
        self.budget_allocated_input.setRange(0, 999999999)
        self.budget_allocated_input.setDecimals(2)
        self.budget_allocated_input.setPrefix("R ")
        self.budget_allocated_input.setSingleStep(10000.00)
        project_layout.addWidget(self.budget_allocated_input, 10, 1)

        # Actual Cost to Date
        project_layout.addWidget(QLabel("Actual Cost to Date:"), 11, 0)
        self.actual_cost_input = QDoubleSpinBox()
        self.actual_cost_input.setRange(0, 999999999)
        self.actual_cost_input.setDecimals(2)
        self.actual_cost_input.setPrefix("R ")
        self.actual_cost_input.setReadOnly(True)
        self.actual_cost_input.setStyleSheet("background: #F5F5F5;")
        project_layout.addWidget(self.actual_cost_input, 11, 1)

        layout.addWidget(project_group)

        # Project Buttons
        project_button_layout = QHBoxLayout()
        self.add_project_btn = QPushButton("Add Project")
        self.add_project_btn.clicked.connect(self._add_project)
        self.add_project_btn.setStyleSheet("""
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
        
        self.edit_project_btn = QPushButton("Edit Project")
        self.edit_project_btn.clicked.connect(self._edit_project)
        self.edit_project_btn.setStyleSheet("""
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
        
        self.delete_project_btn = QPushButton("Delete Project")
        self.delete_project_btn.clicked.connect(self._delete_project)
        self.delete_project_btn.setStyleSheet("""
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
        
        self.clear_project_btn = QPushButton("Clear Form")
        self.clear_project_btn.clicked.connect(self._clear_project_form)
        self.clear_project_btn.setStyleSheet("""
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
        
        project_button_layout.addWidget(self.add_project_btn)
        project_button_layout.addWidget(self.edit_project_btn)
        project_button_layout.addWidget(self.delete_project_btn)
        project_button_layout.addWidget(self.clear_project_btn)
        project_button_layout.addStretch()
        layout.addLayout(project_button_layout)

        # Projects Table
        projects_table_group = QGroupBox("Projects Register")
        projects_table_layout = QVBoxLayout(projects_table_group)
        
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(8)
        self.projects_table.setHorizontalHeaderLabels([
            "Code", "Name", "Client", "Contract Value", "Budget", "Actual Cost", "Status", "Actions"
        ])
        
        # Style table
        header = self.projects_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.projects_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.projects_table.verticalHeader().setDefaultSectionSize(40)
        projects_table_layout.addWidget(self.projects_table)
        
        layout.addWidget(projects_table_group)
        layout.addStretch()

        # Generate initial project code
        self._generate_project_code()

        return tab

    def _create_transactions_tab(self):
        """Create project transactions tab - PRJ-004"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Transaction Entry Group
        transaction_group = QGroupBox("Project Transaction")
        transaction_layout = QGridLayout(transaction_group)
        transaction_layout.setSpacing(10)

        # Project Selection
        transaction_layout.addWidget(QLabel("Project:"), 0, 0)
        self.transaction_project_combo = QComboBox()
        self._populate_transaction_project_combo()
        transaction_layout.addWidget(self.transaction_project_combo, 0, 1)

        # Transaction Type
        transaction_layout.addWidget(QLabel("Transaction Type:"), 1, 0)
        self.transaction_type_combo = QComboBox()
        self.transaction_type_combo.addItems([
            "Material Cost", "Labor Cost", "Subcontractor Cost", 
            "Equipment Rental", "Overhead Allocation", "Other Expense"
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

        # Description
        transaction_layout.addWidget(QLabel("Description:"), 4, 0)
        self.transaction_description = QLineEdit()
        self.transaction_description.setPlaceholderText("Enter transaction description...")
        transaction_layout.addWidget(self.transaction_description, 4, 1)

        # Reference
        transaction_layout.addWidget(QLabel("Reference:"), 5, 0)
        self.transaction_reference = QLineEdit()
        self.transaction_reference.setPlaceholderText("Enter reference...")
        transaction_layout.addWidget(self.transaction_reference, 5, 1)

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
        transactions_table_group = QGroupBox("Project Transactions")
        transactions_table_layout = QVBoxLayout(transactions_table_group)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels([
            "Date", "Project", "Type", "Amount", "Description", "Reference"
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

    def _create_reports_tab(self):
        """Create reports tab - PRJ-005"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Report Generation Group
        report_group = QGroupBox("Generate Project Reports")
        report_layout = QGridLayout(report_group)
        report_layout.setSpacing(10)

        # Report Type
        report_layout.addWidget(QLabel("Report Type:"), 0, 0)
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Project Status Report", "Project Profitability Analysis", 
            "Project Cost Breakdown", "Project Timeline Summary"
        ])
        report_layout.addWidget(self.report_type_combo, 0, 1)

        # Project Selection
        report_layout.addWidget(QLabel("Project:"), 1, 0)
        self.report_project_combo = QComboBox()
        self._populate_report_project_combo()
        report_layout.addWidget(self.report_project_combo, 1, 1)

        # Report Period
        report_layout.addWidget(QLabel("From Date:"), 2, 0)
        self.report_from_date = QDateEdit()
        self.report_from_date.setDate(QDate.currentDate().addMonths(-6))
        self.report_from_date.setCalendarPopup(True)
        report_layout.addWidget(self.report_from_date, 2, 1)

        report_layout.addWidget(QLabel("To Date:"), 3, 0)
        self.report_to_date = QDateEdit()
        self.report_to_date.setDate(QDate.currentDate())
        self.report_to_date.setCalendarPopup(True)
        report_layout.addWidget(self.report_to_date, 3, 1)

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

    def _generate_project_code(self):
        """Generate unique project code"""
        existing_codes = [p["code"] for p in self.projects_data]
        prefix = "PRJ"
        counter = 1
        while f"{prefix}{counter:03d}" in existing_codes:
            counter += 1
        self.project_code_input.setText(f"{prefix}{counter:03d}")

    def _populate_transaction_project_combo(self):
        """Populate project dropdown for transactions"""
        self.transaction_project_combo.clear()
        for project in self.projects_data:
            if project["status"] not in ["Completed", "Cancelled"]:  # Only active projects
                self.transaction_project_combo.addItem(f"{project['code']} - {project['name']}")

    def _populate_report_project_combo(self):
        """Populate project dropdown for reports"""
        self.report_project_combo.clear()
        self.report_project_combo.addItem("All Projects")
        for project in self.projects_data:
            self.report_project_combo.addItem(f"{project['code']} - {project['name']}")

    def _add_project(self):
        """Add new project - PRJ-002 to PRJ-003"""
        try:
            project_code = self.project_code_input.text().strip()
            project_name = self.project_name_input.text().strip()
            client = self.client_input.text().strip()
            project_type = self.project_type_combo.currentText()
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            contract_value = self.contract_value_input.value()
            project_manager = self.project_manager_input.text().strip()
            status = self.status_combo.currentText()
            description = self.description_input.toPlainText().strip()
            budget_allocated = self.budget_allocated_input.value()
            
            # Validation
            if not project_name:
                QMessageBox.warning(self, "Validation Error", "Project name is required")
                return
            
            if not client:
                QMessageBox.warning(self, "Validation Error", "Client name is required")
                return
            
            if contract_value <= 0:
                QMessageBox.warning(self, "Validation Error", "Contract value must be greater than 0")
                return
            
            if budget_allocated <= 0:
                QMessageBox.warning(self, "Validation Error", "Budget allocated must be greater than 0")
                return
            
            if start_date > end_date:
                QMessageBox.warning(self, "Validation Error", "Start date cannot be after end date")
                return
            
            # Check for duplicates
            for project in self.projects_data:
                if (project["name"].lower() == project_name.lower() and 
                    project["code"] != project_code):
                    QMessageBox.warning(self, "Duplicate Error", 
                                      "A project with this name already exists")
                    return
            
            # Create project record
            project = {
                "code": project_code,
                "name": project_name,
                "client": client,
                "project_type": project_type,
                "start_date": start_date,
                "end_date": end_date,
                "contract_value": contract_value,
                "project_manager": project_manager,
                "status": status,
                "description": description,
                "budget_allocated": budget_allocated,
                "actual_cost": 0.0,
                "date_created": datetime.now().isoformat(),
                "date_modified": datetime.now().isoformat()
            }
            
            self.projects_data.append(project)
            self._save_data()
            self._refresh_projects_table()
            self._clear_project_form()
            self._generate_project_code()
            
            # Update dropdowns
            self._populate_transaction_project_combo()
            self._populate_report_project_combo()
            
            QMessageBox.information(self, "Success", 
                                  f"Project '{project_name}' added successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add project: {str(e)}")

    def _edit_project(self):
        """Edit existing project"""
        current_row = self.projects_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", 
                              "Please select a project to edit")
            return
        
        if current_row >= len(self.projects_data):
            return
        
        # Load project data into form
        project = self.projects_data[current_row]
        self.project_code_input.setText(project["code"])
        self.project_name_input.setText(project["name"])
        self.client_input.setText(project["client"])
        self.project_type_combo.setCurrentText(project["project_type"])
        self.start_date.setDate(QDate.fromString(project["start_date"], "yyyy-MM-dd"))
        self.end_date.setDate(QDate.fromString(project["end_date"], "yyyy-MM-dd"))
        self.contract_value_input.setValue(project["contract_value"])
        self.project_manager_input.setText(project["project_manager"])
        self.status_combo.setCurrentText(project["status"])
        self.description_input.setPlainText(project["description"])
        self.budget_allocated_input.setValue(project["budget_allocated"])
        self.actual_cost_input.setValue(project["actual_cost"])
        
        # Change button text to update
        self.add_project_btn.setText("Update Project")
        self.editing_index = current_row

    def _delete_project(self):
        """Delete project"""
        current_row = self.projects_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Required", 
                              "Please select a project to delete")
            return
        
        if current_row >= len(self.projects_data):
            return
        
        project = self.projects_data[current_row]
        
        # Check if project has transactions
        project_transactions = [t for t in self.project_transactions_data if t["project_code"] == project["code"]]
        if project_transactions:
            QMessageBox.warning(self, "Cannot Delete", 
                              f"Project '{project['name']}' has {len(project_transactions)} transactions. Cannot delete.")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   f"Are you sure you want to delete project '{project['name']}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.projects_data[current_row]
            self._save_data()
            self._refresh_projects_table()
            self._clear_project_form()
            self._generate_project_code()
            
            # Update dropdowns
            self._populate_transaction_project_combo()
            self._populate_report_project_combo()

    def _post_transaction(self):
        """Post project transaction - PRJ-004"""
        try:
            project_text = self.transaction_project_combo.currentText()
            if not project_text:
                QMessageBox.warning(self, "Validation Error", "Please select a project")
                return
            
            project_code = project_text.split(" - ")[0]
            transaction_type = self.transaction_type_combo.currentText()
            transaction_date = self.transaction_date.date().toString("yyyy-MM-dd")
            amount = self.transaction_amount.value()
            description = self.transaction_description.text().strip()
            reference = self.transaction_reference.text().strip()
            
            if amount <= 0:
                QMessageBox.warning(self, "Validation Error", "Amount must be greater than 0")
                return
            
            if not description:
                QMessageBox.warning(self, "Validation Error", "Transaction description is required")
                return
            
            # Find project
            project = None
            for p in self.projects_data:
                if p["code"] == project_code:
                    project = p
                    break
            
            if not project:
                QMessageBox.warning(self, "Error", "Project not found")
                return
            
            # Create transaction record
            transaction = {
                "project_code": project_code,
                "transaction_type": transaction_type,
                "transaction_date": transaction_date,
                "amount": amount,
                "description": description,
                "reference": reference,
                "timestamp": datetime.now().isoformat()
            }
            
            # Post to ledger
            if self.ledger:
                # Create journal entry for project cost
                lines = [
                    {
                        "account_code": "5200",  # Project Costs
                        "debit": amount,
                        "credit": 0,
                        "notes": f"Project cost - {project['name']} - {description}"
                    },
                    {
                        "account_code": "1000",  # Bank FNB Cheque
                        "debit": 0,
                        "credit": amount,
                        "notes": f"Payment for project cost - {reference}"
                    }
                ]
                
                journal_code = self.ledger.post_journal_entry(
                    date_str=transaction_date,
                    reference=reference or "PRJ",
                    description=f"Project Cost - {project['name']}",
                    lines=lines,
                    auto_balance=False  # Already balanced
                )
                
                transaction["journal_code"] = journal_code
                
                # Apply CCE cumulative update
                self.ledger.update_cce(-amount, "project_cost")
            
            self.project_transactions_data.append(transaction)
            
            # Update project actual cost
            project["actual_cost"] += amount
            
            self._save_data()
            self._refresh_projects_table()
            self._refresh_transactions_table()
            self._clear_transaction_form()
            
            # Request dashboard refresh
            self.dashboard_refresh_requested.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Transaction posted successfully. Project actual cost updated to {_fmt_amount(project['actual_cost'])}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to post transaction: {str(e)}")

    def _generate_report(self):
        """Generate project reports - PRJ-005"""
        try:
            report_type = self.report_type_combo.currentText()
            project_text = self.report_project_combo.currentText()
            from_date = self.report_from_date.date().toString("yyyy-MM-dd")
            to_date = self.report_to_date.date().toString("yyyy-MM-dd")
            
            if report_type == "Project Status Report":
                self._generate_status_report(project_text, from_date, to_date)
            elif report_type == "Project Profitability Analysis":
                self._generate_profitability_report(project_text, from_date, to_date)
            elif report_type == "Project Cost Breakdown":
                self._generate_cost_breakdown_report(project_text, from_date, to_date)
            elif report_type == "Project Timeline Summary":
                self._generate_timeline_report(project_text, from_date, to_date)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

    def _generate_status_report(self, project_text, from_date, to_date):
        """Generate project status report"""
        report = f"""
{'='*60}
PROJECT STATUS REPORT
{'='*60}

Report Period: {from_date} to {to_date}
{'='*60}
"""
        
        if project_text == "All Projects":
            # Generate status for all projects
            for project in self.projects_data:
                progress = (project["actual_cost"] / project["budget_allocated"] * 100) if project["budget_allocated"] > 0 else 0
                remaining_budget = project["budget_allocated"] - project["actual_cost"]
                
                report += f"""
PROJECT: {project['name']} ({project['code']})
Client: {project['client']}
Status: {project['status']}
Contract Value: {_fmt_amount(project['contract_value'])}
Budget Allocated: {_fmt_amount(project['budget_allocated'])}
Actual Cost to Date: {_fmt_amount(project['actual_cost'])}
Remaining Budget: {_fmt_amount(remaining_budget)}
Budget Utilization: {progress:.1f}%
Project Manager: {project['project_manager']}
Start Date: {project['start_date']}
End Date: {project['end_date']}

{'-'*60}
"""
        else:
            # Generate status for specific project
            project_code = project_text.split(" - ")[0]
            for project in self.projects_data:
                if project["code"] == project_code:
                    progress = (project["actual_cost"] / project["budget_allocated"] * 100) if project["budget_allocated"] > 0 else 0
                    remaining_budget = project["budget_allocated"] - project["actual_cost"]
                    
                    report += f"""
PROJECT: {project['name']} ({project['code']})
Client: {project['client']}
Status: {project['status']}
Contract Value: {_fmt_amount(project['contract_value'])}
Budget Allocated: {_fmt_amount(project['budget_allocated'])}
Actual Cost to Date: {_fmt_amount(project['actual_cost'])}
Remaining Budget: {_fmt_amount(remaining_budget)}
Budget Utilization: {progress:.1f}%
Project Manager: {project['project_manager']}
Start Date: {project['start_date']}
End Date: {project['end_date']}

{'='*60}
DESCRIPTION:
{project['description']}

{'='*60}
"""
                    break
        
        report += f"""
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _generate_profitability_report(self, project_text, from_date, to_date):
        """Generate project profitability analysis"""
        report = f"""
{'='*60}
PROJECT PROFITABILITY ANALYSIS
{'='*60}

Report Period: {from_date} to {to_date}
{'='*60}
"""
        
        if project_text == "All Projects":
            total_contract = 0.0
            total_cost = 0.0
            total_profit = 0.0
            
            for project in self.projects_data:
                profit = project["contract_value"] - project["actual_cost"]
                margin = (profit / project["contract_value"] * 100) if project["contract_value"] > 0 else 0
                
                total_contract += project["contract_value"]
                total_cost += project["actual_cost"]
                total_profit += profit
                
                report += f"""
{project['name']} ({project['code']})
Contract Value: {_fmt_amount(project['contract_value'])}
Actual Cost: {_fmt_amount(project['actual_cost'])}
Gross Profit: {_fmt_amount(profit)}
Profit Margin: {margin:.1f}%

{'-'*60}
"""
            
            overall_margin = (total_profit / total_contract * 100) if total_contract > 0 else 0
            
            report += f"""
OVERALL SUMMARY:
Total Contract Value: {_fmt_amount(total_contract)}
Total Actual Cost: {_fmt_amount(total_cost)}
Total Gross Profit: {_fmt_amount(total_profit)}
Overall Profit Margin: {overall_margin:.1f}%
"""
        else:
            # Generate for specific project
            project_code = project_text.split(" - ")[0]
            for project in self.projects_data:
                if project["code"] == project_code:
                    profit = project["contract_value"] - project["actual_cost"]
                    margin = (profit / project["contract_value"] * 100) if project["contract_value"] > 0 else 0
                    
                    report += f"""
PROJECT: {project['name']} ({project['code']})
Client: {project['client']}
Contract Value: {_fmt_amount(project['contract_value'])}
Budget Allocated: {_fmt_amount(project['budget_allocated'])}
Actual Cost: {_fmt_amount(project['actual_cost'])}
Gross Profit: {_fmt_amount(profit)}
Profit Margin: {margin:.1f}%
Budget Variance: {_fmt_amount(project['budget_allocated'] - project['actual_cost'])}
"""
                    break
        
        report += f"""

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _generate_cost_breakdown_report(self, project_text, from_date, to_date):
        """Generate project cost breakdown report"""
        report = f"""
{'='*60}
PROJECT COST BREAKDOWN REPORT
{'='*60}

Report Period: {from_date} to {to_date}
{'='*60}
"""
        
        if project_text == "All Projects":
            # Group costs by type across all projects
            cost_types = {}
            
            for transaction in self.project_transactions_data:
                if from_date <= transaction["transaction_date"] <= to_date:
                    cost_type = transaction["transaction_type"]
                    if cost_type not in cost_types:
                        cost_types[cost_type] = 0.0
                    cost_types[cost_type] += transaction["amount"]
            
            for cost_type, total in cost_types.items():
                report += f"{cost_type}: {_fmt_amount(total)}\n"
        else:
            # Generate for specific project
            project_code = project_text.split(" - ")[0]
            
            # Group costs by type for this project
            cost_types = {}
            
            for transaction in self.project_transactions_data:
                if (transaction["project_code"] == project_code and 
                    from_date <= transaction["transaction_date"] <= to_date):
                    cost_type = transaction["transaction_type"]
                    if cost_type not in cost_types:
                        cost_types[cost_type] = 0.0
                    cost_types[cost_type] += transaction["amount"]
            
            for cost_type, total in cost_types.items():
                report += f"{cost_type}: {_fmt_amount(total)}\n"
        
        report += f"""

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _generate_timeline_report(self, project_text, from_date, to_date):
        """Generate project timeline summary"""
        report = f"""
{'='*60}
PROJECT TIMELINE SUMMARY
{'='*60}

Report Period: {from_date} to {to_date}
{'='*60}
"""
        
        if project_text == "All Projects":
            for project in self.projects_data:
                start_dt = QDate.fromString(project["start_date"], "yyyy-MM-dd")
                end_dt = QDate.fromString(project["end_date"], "yyyy-MM-dd")
                current_dt = QDate.currentDate()
                
                total_days = start_dt.daysTo(end_dt)
                elapsed_days = start_dt.daysTo(current_dt)
                progress_pct = (elapsed_days / total_days * 100) if total_days > 0 else 0
                
                if current_dt > end_dt:
                    timeline_status = "Overdue"
                elif progress_pct >= 100:
                    timeline_status = "Completed"
                else:
                    timeline_status = "On Track"
                
                report += f"""
{project['name']} ({project['code']})
Start Date: {project['start_date']}
End Date: {project['end_date']}
Total Duration: {total_days} days
Elapsed: {elapsed_days} days
Progress: {progress_pct:.1f}%
Timeline Status: {timeline_status}

{'-'*60}
"""
        else:
            # Generate for specific project
            project_code = project_text.split(" - ")[0]
            for project in self.projects_data:
                if project["code"] == project_code:
                    start_dt = QDate.fromString(project["start_date"], "yyyy-MM-dd")
                    end_dt = QDate.fromString(project["end_date"], "yyyy-MM-dd")
                    current_dt = QDate.currentDate()
                    
                    total_days = start_dt.daysTo(end_dt)
                    elapsed_days = start_dt.daysTo(current_dt)
                    progress_pct = (elapsed_days / total_days * 100) if total_days > 0 else 0
                    
                    if current_dt > end_dt:
                        timeline_status = "Overdue"
                    elif progress_pct >= 100:
                        timeline_status = "Completed"
                    else:
                        timeline_status = "On Track"
                    
                    report += f"""
PROJECT: {project['name']} ({project['code']})
Start Date: {project['start_date']}
End Date: {project['end_date']}
Total Duration: {total_days} days
Elapsed: {elapsed_days} days
Progress: {progress_pct:.1f}%
Timeline Status: {timeline_status}
Project Manager: {project['project_manager']}

{'='*60}
"""
                    break
        
        report += f"""
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
"""
        
        self.report_preview.setPlainText(report)

    def _print_report(self):
        """Print project report"""
        report_text = self.report_preview.toPlainText()
        if not report_text.strip():
            QMessageBox.warning(self, "No Report", "Please generate a report first")
            return
        
        # In a real implementation, this would send to printer
        QMessageBox.information(self, "Print Report", 
                              "Report sent to printer (simulated)")

    def _clear_project_form(self):
        """Clear project form"""
        self.project_name_input.clear()
        self.client_input.clear()
        self.project_type_combo.setCurrentIndex(0)
        self.start_date.setDate(QDate.currentDate())
        self.end_date.setDate(QDate.currentDate().addMonths(6))
        self.contract_value_input.setValue(0)
        self.project_manager_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.description_input.clear()
        self.budget_allocated_input.setValue(0)
        self.actual_cost_input.setValue(0)
        self.add_project_btn.setText("Add Project")
        self.editing_index = None

    def _clear_transaction_form(self):
        """Clear transaction form"""
        self.transaction_project_combo.setCurrentIndex(0)
        self.transaction_type_combo.setCurrentIndex(0)
        self.transaction_amount.setValue(0)
        self.transaction_description.clear()
        self.transaction_reference.clear()

    def _refresh_projects_table(self):
        """Refresh projects table"""
        self.projects_table.setRowCount(len(self.projects_data))
        
        for row, project in enumerate(self.projects_data):
            self.projects_table.setItem(row, 0, QTableWidgetItem(project["code"]))
            self.projects_table.setItem(row, 1, QTableWidgetItem(project["name"]))
            self.projects_table.setItem(row, 2, QTableWidgetItem(project["client"]))
            self.projects_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(project["contract_value"])))
            self.projects_table.setItem(row, 4, QTableWidgetItem(_fmt_amount(project["budget_allocated"])))
            self.projects_table.setItem(row, 5, QTableWidgetItem(_fmt_amount(project["actual_cost"])))
            
            # Status with color coding
            status_item = QTableWidgetItem(project["status"])
            if project["status"] == "In Progress":
                status_item.setStyleSheet("color: #00B050; font-weight: bold;")
            elif project["status"] == "On Hold":
                status_item.setStyleSheet("color: #E07B00; font-weight: bold;")
            elif project["status"] == "Completed":
                status_item.setStyleSheet("color: #00B0F0; font-weight: bold;")
            elif project["status"] == "Cancelled":
                status_item.setStyleSheet("color: #D32F2F; font-weight: bold;")
            else:
                status_item.setStyleSheet("color: #6A7575; font-weight: bold;")
            
            self.projects_table.setItem(row, 6, status_item)
            
            # Add action button
            action_btn = QPushButton("Select")
            action_btn.clicked.connect(lambda _, r=row: self._select_project(r))
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
            self.projects_table.setCellWidget(row, 7, action_btn)

    def _refresh_transactions_table(self):
        """Refresh transactions table"""
        self.transactions_table.setRowCount(len(self.project_transactions_data))
        
        # Sort transactions by date (most recent first)
        sorted_transactions = sorted(self.project_transactions_data, 
                                    key=lambda x: x["transaction_date"], 
                                    reverse=True)
        
        for row, transaction in enumerate(sorted_transactions):
            # Find project name
            project_name = "Unknown"
            for project in self.projects_data:
                if project["code"] == transaction["project_code"]:
                    project_name = project["name"]
                    break
            
            self.transactions_table.setItem(row, 0, QTableWidgetItem(transaction["transaction_date"]))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(f"{transaction['project_code']} - {project_name}"))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(transaction["transaction_type"]))
            self.transactions_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(transaction["amount"])))
            self.transactions_table.setItem(row, 4, QTableWidgetItem(transaction["description"]))
            self.transactions_table.setItem(row, 5, QTableWidgetItem(transaction.get("reference", "")))

    def _select_project(self, row):
        """Select project row"""
        self.projects_table.selectRow(row)

    def _save_data(self):
        """Save all data to files"""
        try:
            with open(self.projects_file, 'w') as f:
                json.dump(self.projects_data, f, indent=2)
            with open(self.project_transactions_file, 'w') as f:
                json.dump(self.project_transactions_data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def _load_data(self):
        """Load all data from files"""
        try:
            if self.projects_file.exists():
                with open(self.projects_file, 'r') as f:
                    self.projects_data = json.load(f)
            
            if self.project_transactions_file.exists():
                with open(self.project_transactions_file, 'r') as f:
                    self.project_transactions_data = json.load(f)
                    
        except Exception as e:
            print(f"Error loading data: {e}")
            self.projects_data = []
            self.project_transactions_data = []

    def get_projects_data(self):
        """Get projects data"""
        return self.projects_data.copy()

    def get_total_project_value(self) -> float:
        """Get total project contract value"""
        return sum(project["contract_value"] for project in self.projects_data if project["status"] != "Cancelled")
