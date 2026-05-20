#!/usr/bin/env python3
"""
Adjustments Module Handler
Implements ADJ-001 to ADJ-006 test cases for accounting adjustments functionality
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

class AdjustmentsHandler(QWidget):
    """Adjustments Module Handler - Implements ADJ-001 to ADJ-006"""
    
    # Signals for communication with main window
    dashboard_refresh_requested = pyqtSignal()
    navigation_requested = pyqtSignal(str)  # Page name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ledger = getattr(parent, 'ledger', None) if parent else None
        self.adjustments_data = []
        self.editing_index = None
        
        # Data file paths
        self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.adjustments_file = self.data_dir / "adjustments.json"
        
        self._load_data()
        self._build_ui()

    def _build_ui(self):
        """Build adjustments UI - ADJ-001: Navigation to Adjustments"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("Accounting Adjustments")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(header)

        # Create tabbed interface
        tab_widget = QTabWidget()
        
        # Journal Adjustments Tab
        journal_tab = self._create_journal_adjustments_tab()
        tab_widget.addTab(journal_tab, "Journal Adjustments")
        
        # Year-End Adjustments Tab
        year_end_tab = self._create_year_end_adjustments_tab()
        tab_widget.addTab(year_end_tab, "Year-End Adjustments")
        
        # Adjustment History Tab
        history_tab = self._create_history_tab()
        tab_widget.addTab(history_tab, "Adjustment History")
        
        layout.addWidget(tab_widget)

    def _create_journal_adjustments_tab(self):
        """Create journal adjustments tab - ADJ-001 to ADJ-004"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Adjustment Entry Group
        adjustment_group = QGroupBox("Journal Adjustment")
        adjustment_group.setStyleSheet("""
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
        adjustment_layout = QGridLayout(adjustment_group)
        adjustment_layout.setSpacing(10)

        # Adjustment Number (auto-generated)
        adjustment_layout.addWidget(QLabel("Adjustment Number:"), 0, 0)
        self.adjustment_number_input = QLineEdit()
        self.adjustment_number_input.setReadOnly(True)
        self.adjustment_number_input.setStyleSheet("background: #F5F5F5;")
        adjustment_layout.addWidget(self.adjustment_number_input, 0, 1)

        # Adjustment Date
        adjustment_layout.addWidget(QLabel("Adjustment Date:"), 1, 0)
        self.adjustment_date = QDateEdit()
        self.adjustment_date.setDate(QDate.currentDate())
        self.adjustment_date.setCalendarPopup(True)
        adjustment_layout.addWidget(self.adjustment_date, 1, 1)

        # Adjustment Type
        adjustment_layout.addWidget(QLabel("Adjustment Type:"), 2, 0)
        self.adjustment_type_combo = QComboBox()
        self.adjustment_type_combo.addItems([
            "Accrual", "Prepayment", "Provision", "Depreciation", 
            "Bad Debt", "Correction", "Reclassification", "Other"
        ])
        adjustment_layout.addWidget(self.adjustment_type_combo, 2, 1)

        # Description
        adjustment_layout.addWidget(QLabel("Description:"), 3, 0)
        self.adjustment_description = QLineEdit()
        self.adjustment_description.setPlaceholderText("Enter adjustment description...")
        adjustment_layout.addWidget(self.adjustment_description, 3, 1)

        # Reference
        adjustment_layout.addWidget(QLabel("Reference:"), 4, 0)
        self.adjustment_reference = QLineEdit()
        self.adjustment_reference.setPlaceholderText("Enter reference...")
        adjustment_layout.addWidget(self.adjustment_reference, 4, 1)

        layout.addWidget(adjustment_group)

        # Journal Lines Group
        journal_lines_group = QGroupBox("Journal Entry Lines")
        journal_lines_layout = QVBoxLayout(journal_lines_group)
        
        # Journal Lines Table
        self.journal_lines_table = QTableWidget()
        self.journal_lines_table.setColumnCount(5)
        self.journal_lines_table.setHorizontalHeaderLabels([
            "Account Code", "Account Name", "Debit", "Credit", "Notes"
        ])
        
        # Style table
        header = self.journal_lines_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.journal_lines_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.journal_lines_table.verticalHeader().setDefaultSectionSize(40)
        journal_lines_layout.addWidget(self.journal_lines_table)
        
        # Journal Lines Buttons
        lines_button_layout = QHBoxLayout()
        self.add_line_btn = QPushButton("Add Line")
        self.add_line_btn.clicked.connect(self._add_journal_line)
        self.add_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B050;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00A040;
            }
        """)
        
        self.remove_line_btn = QPushButton("Remove Line")
        self.remove_line_btn.clicked.connect(self._remove_journal_line)
        self.remove_line_btn.setStyleSheet("""
            QPushButton {
                background-color: #E07B00;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #D06B00;
            }
        """)
        
        lines_button_layout.addWidget(self.add_line_btn)
        lines_button_layout.addWidget(self.remove_line_btn)
        lines_button_layout.addStretch()
        journal_lines_layout.addLayout(lines_button_layout)
        
        layout.addWidget(journal_lines_group)

        # Balance Display
        balance_group = QGroupBox("Balance Check")
        balance_layout = QHBoxLayout(balance_group)
        
        self.total_debit_label = QLabel("Total Debit: R 0.00")
        self.total_debit_label.setStyleSheet("font-weight: bold; color: #00B050;")
        balance_layout.addWidget(self.total_debit_label)
        
        self.total_credit_label = QLabel("Total Credit: R 0.00")
        self.total_credit_label.setStyleSheet("font-weight: bold; color: #E07B00;")
        balance_layout.addWidget(self.total_credit_label)
        
        self.balance_status_label = QLabel("Status: Balanced")
        self.balance_status_label.setStyleSheet("font-weight: bold; color: #00B050;")
        balance_layout.addWidget(self.balance_status_label)
        
        balance_layout.addStretch()
        layout.addWidget(balance_group)

        # Adjustment Buttons
        adjustment_button_layout = QHBoxLayout()
        self.post_adjustment_btn = QPushButton("Post Adjustment")
        self.post_adjustment_btn.clicked.connect(self._post_adjustment)
        self.post_adjustment_btn.setStyleSheet("""
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
        
        self.clear_adjustment_btn = QPushButton("Clear Form")
        self.clear_adjustment_btn.clicked.connect(self._clear_adjustment_form)
        self.clear_adjustment_btn.setStyleSheet("""
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
        
        adjustment_button_layout.addWidget(self.post_adjustment_btn)
        adjustment_button_layout.addWidget(self.clear_adjustment_btn)
        adjustment_button_layout.addStretch()
        layout.addLayout(adjustment_button_layout)

        layout.addStretch()

        # Initialize journal lines
        self.journal_lines = []
        self._add_journal_line()  # Add initial empty line
        self._generate_adjustment_number()

        return tab

    def _create_year_end_adjustments_tab(self):
        """Create year-end adjustments tab - ADJ-005"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Year-End Processing Group
        year_end_group = QGroupBox("Year-End Adjustments")
        year_end_layout = QGridLayout(year_end_group)
        year_end_layout.setSpacing(10)

        # Financial Year End
        year_end_layout.addWidget(QLabel("Financial Year End:"), 0, 0)
        self.year_end_date = QDateEdit()
        self.year_end_date.setDate(QDate.currentDate().addMonths(-QDate.currentDate().month() % 12))
        self.year_end_date.setCalendarPopup(True)
        year_end_layout.addWidget(self.year_end_date, 0, 1)

        # Auto-Generate Adjustments
        auto_adjustments_group = QGroupBox("Auto-Generate Year-End Adjustments")
        auto_layout = QVBoxLayout(auto_adjustments_group)
        
        self.depreciation_checkbox = QCheckBox("Depreciation Expense")
        self.depreciation_checkbox.setChecked(True)
        auto_layout.addWidget(self.depreciation_checkbox)
        
        self.accruals_checkbox = QCheckBox("Accruals & Prepayments")
        self.accruals_checkbox.setChecked(True)
        auto_layout.addWidget(self.accruals_checkbox)
        
        self.provisions_checkbox = QCheckBox("Provisions & Contingencies")
        self.provisions_checkbox.setChecked(True)
        auto_layout.addWidget(self.provisions_checkbox)
        
        self.bad_debts_checkbox = QCheckBox("Bad Debt Provision")
        self.bad_debts_checkbox.setChecked(True)
        auto_layout.addWidget(self.bad_debts_checkbox)
        
        year_end_layout.addWidget(auto_adjustments_group, 1, 0, 1, 2)

        # Process Year-End Button
        self.process_year_end_btn = QPushButton("Process Year-End Adjustments")
        self.process_year_end_btn.clicked.connect(self._process_year_end_adjustments)
        self.process_year_end_btn.setStyleSheet("""
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
        year_end_layout.addWidget(self.process_year_end_btn, 2, 0, 1, 2)

        layout.addWidget(year_end_group)

        # Year-End Summary
        year_end_summary_group = QGroupBox("Year-End Adjustments Summary")
        year_end_summary_layout = QVBoxLayout(year_end_summary_group)
        
        self.year_end_table = QTableWidget()
        self.year_end_table.setColumnCount(5)
        self.year_end_table.setHorizontalHeaderLabels([
            "Adjustment Number", "Date", "Type", "Amount", "Status"
        ])
        
        # Style table
        header = self.year_end_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.year_end_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.year_end_table.verticalHeader().setDefaultSectionSize(40)
        year_end_summary_layout.addWidget(self.year_end_table)
        
        layout.addWidget(year_end_summary_group)
        layout.addStretch()

        return tab

    def _create_history_tab(self):
        """Create adjustment history tab - ADJ-006"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # History Filter Group
        filter_group = QGroupBox("Filter Adjustments")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Period:"))
        self.history_from_date = QDateEdit()
        self.history_from_date.setDate(QDate.currentDate().addMonths(-12))
        self.history_from_date.setCalendarPopup(True)
        filter_layout.addWidget(self.history_from_date)
        
        filter_layout.addWidget(QLabel("to"))
        self.history_to_date = QDateEdit()
        self.history_to_date.setDate(QDate.currentDate())
        self.history_to_date.setCalendarPopup(True)
        filter_layout.addWidget(self.history_to_date)
        
        filter_layout.addWidget(QLabel("Type:"))
        self.history_type_combo = QComboBox()
        self.history_type_combo.addItems(["All Types", "Accrual", "Prepayment", "Provision", "Depreciation", "Bad Debt", "Correction", "Reclassification", "Other"])
        filter_layout.addWidget(self.history_type_combo)
        
        self.refresh_history_btn = QPushButton("Refresh")
        self.refresh_history_btn.clicked.connect(self._refresh_history)
        self.refresh_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #00B0F0;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0090E0;
            }
        """)
        filter_layout.addWidget(self.refresh_history_btn)
        
        filter_layout.addStretch()
        layout.addWidget(filter_group)

        # History Table
        history_table_group = QGroupBox("Adjustment History")
        history_table_layout = QVBoxLayout(history_table_group)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Adjustment No", "Date", "Type", "Description", "Total Amount", "Status", "Actions"
        ])
        
        # Style table
        header = self.history_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 8px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        self.history_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        
        self.history_table.verticalHeader().setDefaultSectionSize(40)
        history_table_layout.addWidget(self.history_table)
        
        layout.addWidget(history_table_group)
        layout.addStretch()

        # Load initial history
        self._refresh_history()

        return tab

    def _generate_adjustment_number(self):
        """Generate unique adjustment number"""
        existing_numbers = [a["adjustment_number"] for a in self.adjustments_data]
        prefix = "ADJ"
        counter = 1
        current_year = date.today().year
        while f"{prefix}{current_year}{counter:04d}" in existing_numbers:
            counter += 1
        self.adjustment_number_input.setText(f"{prefix}{current_year}{counter:04d}")

    def _add_journal_line(self):
        """Add journal entry line"""
        # Create a new row in the journal lines table
        row_count = self.journal_lines_table.rowCount()
        self.journal_lines_table.insertRow(row_count)
        
        # Account Code dropdown
        account_combo = QComboBox()
        for account_code, account_data in CHART_OF_ACCOUNTS.items():
            account_combo.addItem(f"{account_code} - {account_data['name']}")
        account_combo.currentTextChanged.connect(self._on_account_changed)
        self.journal_lines_table.setCellWidget(row_count, 0, account_combo)
        
        # Account Name (auto-populated)
        account_name_item = QTableWidgetItem("")
        account_name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.journal_lines_table.setItem(row_count, 1, account_name_item)
        
        # Debit amount
        debit_item = QTableWidgetItem("0.00")
        self.journal_lines_table.setItem(row_count, 2, debit_item)
        
        # Credit amount
        credit_item = QTableWidgetItem("0.00")
        self.journal_lines_table.setItem(row_count, 3, credit_item)
        
        # Notes
        notes_item = QTableWidgetItem("")
        self.journal_lines_table.setItem(row_count, 4, notes_item)
        
        # Add to journal lines list
        self.journal_lines.append({
            "row": row_count,
            "account_combo": account_combo,
            "account_name_item": account_name_item,
            "debit_item": debit_item,
            "credit_item": credit_item,
            "notes_item": notes_item
        })
        
        # Connect item changed signals
        self.journal_lines_table.itemChanged.connect(self._on_journal_item_changed)

    def _remove_journal_line(self):
        """Remove journal entry line"""
        current_row = self.journal_lines_table.currentRow()
        if current_row >= 0 and current_row < len(self.journal_lines):
            self.journal_lines_table.removeRow(current_row)
            del self.journal_lines[current_row]
            self._update_balance_check()

    def _on_account_changed(self):
        """Handle account selection change"""
        sender = self.sender()
        if isinstance(sender, QComboBox):
            # Find the row for this combo box
            for i, line in enumerate(self.journal_lines):
                if line["account_combo"] == sender:
                    account_text = sender.currentText()
                    if " - " in account_text:
                        account_name = account_text.split(" - ")[1]
                        line["account_name_item"].setText(account_name)
                    break

    def _on_journal_item_changed(self, item):
        """Handle journal item changes"""
        if item.column() in [2, 3]:  # Debit or Credit column
            # Ensure only one of debit or credit is entered
            if item.column() == 2 and item.text() != "":
                # Clear credit if debit is entered
                credit_item = self.journal_lines_table.item(item.row(), 3)
                if credit_item:
                    credit_item.setText("")
            elif item.column() == 3 and item.text() != "":
                # Clear debit if credit is entered
                debit_item = self.journal_lines_table.item(item.row(), 2)
                if debit_item:
                    debit_item.setText("")
            
            self._update_balance_check()

    def _update_balance_check(self):
        """Update balance check display"""
        total_debit = 0.0
        total_credit = 0.0
        
        for line in self.journal_lines:
            try:
                debit_text = line["debit_item"].text()
                credit_text = line["credit_item"].text()
                
                if debit_text:
                    total_debit += float(debit_text.replace("R", "").replace(",", ""))
                if credit_text:
                    total_credit += float(credit_text.replace("R", "").replace(",", ""))
            except ValueError:
                pass
        
        self.total_debit_label.setText(f"Total Debit: {_fmt_amount(total_debit)}")
        self.total_credit_label.setText(f"Total Credit: {_fmt_amount(total_credit)}")
        
        # Update balance status
        if abs(total_debit - total_credit) < 0.01:
            self.balance_status_label.setText("Status: Balanced")
            self.balance_status_label.setStyleSheet("font-weight: bold; color: #00B050;")
        else:
            difference = abs(total_debit - total_credit)
            self.balance_status_label.setText(f"Status: Unbalanced (Difference: {_fmt_amount(difference)})")
            self.balance_status_label.setStyleSheet("font-weight: bold; color: #D32F2F;")

    def _post_adjustment(self):
        """Post journal adjustment - ADJ-003 to ADJ-004"""
        try:
            adjustment_number = self.adjustment_number_input.text().strip()
            adjustment_date = self.adjustment_date.date().toString("yyyy-MM-dd")
            adjustment_type = self.adjustment_type_combo.currentText()
            description = self.adjustment_description.text().strip()
            reference = self.adjustment_reference.text().strip()
            
            if not description:
                QMessageBox.warning(self, "Validation Error", "Adjustment description is required")
                return
            
            # Check if journal is balanced
            total_debit = 0.0
            total_credit = 0.0
            journal_lines_data = []
            
            for line in self.journal_lines:
                try:
                    account_text = line["account_combo"].currentText()
                    if not account_text or " - " not in account_text:
                        continue
                    
                    account_code = account_text.split(" - ")[0]
                    debit_text = line["debit_item"].text()
                    credit_text = line["credit_item"].text()
                    notes = line["notes_item"].text()
                    
                    debit_amount = float(debit_text.replace("R", "").replace(",", "")) if debit_text else 0.0
                    credit_amount = float(credit_text.replace("R", "").replace(",", "")) if credit_text else 0.0
                    
                    if debit_amount > 0 or credit_amount > 0:
                        journal_lines_data.append({
                            "account_code": account_code,
                            "debit": debit_amount,
                            "credit": credit_amount,
                            "notes": notes
                        })
                        total_debit += debit_amount
                        total_credit += credit_amount
                        
                except ValueError:
                    pass
            
            if len(journal_lines_data) < 2:
                QMessageBox.warning(self, "Validation Error", "Journal entry must have at least 2 lines")
                return
            
            if abs(total_debit - total_credit) > 0.01:
                QMessageBox.warning(self, "Validation Error", "Journal entry must be balanced")
                return
            
            # Create adjustment record
            adjustment = {
                "adjustment_number": adjustment_number,
                "adjustment_date": adjustment_date,
                "adjustment_type": adjustment_type,
                "description": description,
                "reference": reference,
                "journal_lines": journal_lines_data,
                "total_amount": total_debit,
                "status": "Posted",
                "timestamp": datetime.now().isoformat()
            }
            
            # Post to ledger
            if self.ledger:
                journal_code = self.ledger.post_journal_entry(
                    date_str=adjustment_date,
                    reference=adjustment_number,
                    description=f"{adjustment_type} - {description}",
                    lines=journal_lines_data,
                    auto_balance=False  # Already balanced
                )
                
                adjustment["journal_code"] = journal_code
            
            self.adjustments_data.append(adjustment)
            self._save_data()
            self._clear_adjustment_form()
            
            # Refresh history and year-end tables
            self._refresh_history()
            self._refresh_year_end_table()
            
            # Request dashboard refresh
            self.dashboard_refresh_requested.emit()
            
            QMessageBox.information(self, "Success", 
                                  f"Adjustment {adjustment_number} posted successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to post adjustment: {str(e)}")

    def _process_year_end_adjustments(self):
        """Process year-end adjustments - ADJ-005"""
        try:
            year_end_date = self.year_end_date.date().toString("yyyy-MM-dd")
            
            adjustments_created = []
            
            # Generate depreciation adjustment if selected
            if self.depreciation_checkbox.isChecked():
                depreciation_adj = self._create_depreciation_adjustment(year_end_date)
                if depreciation_adj:
                    adjustments_created.append(depreciation_adj)
            
            # Generate accruals adjustment if selected
            if self.accruals_checkbox.isChecked():
                accrual_adj = self._create_accruals_adjustment(year_end_date)
                if accrual_adj:
                    adjustments_created.append(accrual_adj)
            
            # Generate provisions adjustment if selected
            if self.provisions_checkbox.isChecked():
                provision_adj = self._create_provisions_adjustment(year_end_date)
                if provision_adj:
                    adjustments_created.append(provision_adj)
            
            # Generate bad debt adjustment if selected
            if self.bad_debts_checkbox.isChecked():
                bad_debt_adj = self._create_bad_debt_adjustment(year_end_date)
                if bad_debt_adj:
                    adjustments_created.append(bad_debt_adj)
            
            if adjustments_created:
                QMessageBox.information(self, "Success", 
                                      f"Created {len(adjustments_created)} year-end adjustments")
                self._refresh_year_end_table()
                self._refresh_history()
                self.dashboard_refresh_requested.emit()
            else:
                QMessageBox.information(self, "Info", "No year-end adjustments were generated")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process year-end adjustments: {str(e)}")

    def _create_depreciation_adjustment(self, year_end_date):
        """Create depreciation adjustment"""
        # This is a simplified implementation
        # In a real system, this would calculate actual depreciation based on assets
        
        depreciation_amount = 50000.00  # Example amount
        adjustment_number = self._generate_unique_adjustment_number()
        
        adjustment = {
            "adjustment_number": adjustment_number,
            "adjustment_date": year_end_date,
            "adjustment_type": "Depreciation",
            "description": "Year-end depreciation expense",
            "reference": "AUTO-YE",
            "journal_lines": [
                {
                    "account_code": "5300",  # Depreciation Expense
                    "debit": depreciation_amount,
                    "credit": 0,
                    "notes": "Annual depreciation charge"
                },
                {
                    "account_code": "1300",  # Accumulated Depreciation
                    "debit": 0,
                    "credit": depreciation_amount,
                    "notes": "Accumulated depreciation"
                }
            ],
            "total_amount": depreciation_amount,
            "status": "Posted",
            "timestamp": datetime.now().isoformat()
        }
        
        # Post to ledger
        if self.ledger:
            journal_code = self.ledger.post_journal_entry(
                date_str=year_end_date,
                reference=adjustment_number,
                description="Year-end depreciation",
                lines=adjustment["journal_lines"],
                auto_balance=False
            )
            adjustment["journal_code"] = journal_code
        
        self.adjustments_data.append(adjustment)
        self._save_data()
        
        return adjustment

    def _create_accruals_adjustment(self, year_end_date):
        """Create accruals adjustment"""
        # Simplified accruals calculation
        accrual_amount = 25000.00  # Example amount
        adjustment_number = self._generate_unique_adjustment_number()
        
        adjustment = {
            "adjustment_number": adjustment_number,
            "adjustment_date": year_end_date,
            "adjustment_type": "Accrual",
            "description": "Year-end accruals",
            "reference": "AUTO-YE",
            "journal_lines": [
                {
                    "account_code": "5200",  # Operating Expenses
                    "debit": accrual_amount,
                    "credit": 0,
                    "notes": "Accrued expenses"
                },
                {
                    "account_code": "2100",  # Accrued Expenses
                    "debit": 0,
                    "credit": accrual_amount,
                    "notes": "Accrued expenses payable"
                }
            ],
            "total_amount": accrual_amount,
            "status": "Posted",
            "timestamp": datetime.now().isoformat()
        }
        
        # Post to ledger
        if self.ledger:
            journal_code = self.ledger.post_journal_entry(
                date_str=year_end_date,
                reference=adjustment_number,
                description="Year-end accruals",
                lines=adjustment["journal_lines"],
                auto_balance=False
            )
            adjustment["journal_code"] = journal_code
        
        self.adjustments_data.append(adjustment)
        self._save_data()
        
        return adjustment

    def _create_provisions_adjustment(self, year_end_date):
        """Create provisions adjustment"""
        # Simplified provisions calculation
        provision_amount = 15000.00  # Example amount
        adjustment_number = self._generate_unique_adjustment_number()
        
        adjustment = {
            "adjustment_number": adjustment_number,
            "adjustment_date": year_end_date,
            "adjustment_type": "Provision",
            "description": "Year-end provisions",
            "reference": "AUTO-YE",
            "journal_lines": [
                {
                    "account_code": "5400",  # Other Expenses
                    "debit": provision_amount,
                    "credit": 0,
                    "notes": "Provision for contingencies"
                },
                {
                    "account_code": "2200",  # Provisions
                    "debit": 0,
                    "credit": provision_amount,
                    "notes": "Provision for contingencies"
                }
            ],
            "total_amount": provision_amount,
            "status": "Posted",
            "timestamp": datetime.now().isoformat()
        }
        
        # Post to ledger
        if self.ledger:
            journal_code = self.ledger.post_journal_entry(
                date_str=year_end_date,
                reference=adjustment_number,
                description="Year-end provisions",
                lines=adjustment["journal_lines"],
                auto_balance=False
            )
            adjustment["journal_code"] = journal_code
        
        self.adjustments_data.append(adjustment)
        self._save_data()
        
        return adjustment

    def _create_bad_debt_adjustment(self, year_end_date):
        """Create bad debt adjustment"""
        # Simplified bad debt calculation
        bad_debt_amount = 10000.00  # Example amount
        adjustment_number = self._generate_unique_adjustment_number()
        
        adjustment = {
            "adjustment_number": adjustment_number,
            "adjustment_date": year_end_date,
            "adjustment_type": "Bad Debt",
            "description": "Year-end bad debt provision",
            "reference": "AUTO-YE",
            "journal_lines": [
                {
                    "account_code": "5500",  # Bad Debt Expense
                    "debit": bad_debt_amount,
                    "credit": 0,
                    "notes": "Bad debt provision"
                },
                {
                    "account_code": "1100",  # Allowance for Doubtful Accounts
                    "debit": 0,
                    "credit": bad_debt_amount,
                    "notes": "Allowance for doubtful accounts"
                }
            ],
            "total_amount": bad_debt_amount,
            "status": "Posted",
            "timestamp": datetime.now().isoformat()
        }
        
        # Post to ledger
        if self.ledger:
            journal_code = self.ledger.post_journal_entry(
                date_str=year_end_date,
                reference=adjustment_number,
                description="Year-end bad debt provision",
                lines=adjustment["journal_lines"],
                auto_balance=False
            )
            adjustment["journal_code"] = journal_code
        
        self.adjustments_data.append(adjustment)
        self._save_data()
        
        return adjustment

    def _generate_unique_adjustment_number(self):
        """Generate unique adjustment number for auto-generated adjustments"""
        existing_numbers = [a["adjustment_number"] for a in self.adjustments_data]
        prefix = "ADJ"
        counter = 1
        current_year = date.today().year
        while f"{prefix}{current_year}{counter:04d}" in existing_numbers:
            counter += 1
        return f"{prefix}{current_year}{counter:04d}"

    def _refresh_history(self):
        """Refresh adjustment history - ADJ-006"""
        try:
            from_date = self.history_from_date.date().toString("yyyy-MM-dd")
            to_date = self.history_to_date.date().toString("yyyy-MM-dd")
            filter_type = self.history_type_combo.currentText()
            
            # Filter adjustments
            filtered_adjustments = []
            for adjustment in self.adjustments_data:
                if from_date <= adjustment["adjustment_date"] <= to_date:
                    if filter_type == "All Types" or adjustment["adjustment_type"] == filter_type:
                        filtered_adjustments.append(adjustment)
            
            # Sort by date (most recent first)
            filtered_adjustments.sort(key=lambda x: x["adjustment_date"], reverse=True)
            
            # Update history table
            self.history_table.setRowCount(len(filtered_adjustments))
            
            for row, adjustment in enumerate(filtered_adjustments):
                self.history_table.setItem(row, 0, QTableWidgetItem(adjustment["adjustment_number"]))
                self.history_table.setItem(row, 1, QTableWidgetItem(adjustment["adjustment_date"]))
                self.history_table.setItem(row, 2, QTableWidgetItem(adjustment["adjustment_type"]))
                self.history_table.setItem(row, 3, QTableWidgetItem(adjustment["description"]))
                self.history_table.setItem(row, 4, QTableWidgetItem(_fmt_amount(adjustment["total_amount"])))
                
                # Status with color coding
                status_item = QTableWidgetItem(adjustment["status"])
                if adjustment["status"] == "Posted":
                    status_item.setStyleSheet("color: #00B050; font-weight: bold;")
                else:
                    status_item.setStyleSheet("color: #E07B00; font-weight: bold;")
                
                self.history_table.setItem(row, 5, status_item)
                
                # Add action button
                action_btn = QPushButton("View")
                action_btn.clicked.connect(lambda _, adj=adjustment: self._view_adjustment_details(adj))
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
                self.history_table.setCellWidget(row, 6, action_btn)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh history: {str(e)}")

    def _refresh_year_end_table(self):
        """Refresh year-end adjustments table"""
        try:
            # Filter year-end adjustments
            year_end_adjustments = [adj for adj in self.adjustments_data 
                                    if adj["reference"] == "AUTO-YE"]
            
            # Sort by date (most recent first)
            year_end_adjustments.sort(key=lambda x: x["adjustment_date"], reverse=True)
            
            # Update year-end table
            self.year_end_table.setRowCount(len(year_end_adjustments))
            
            for row, adjustment in enumerate(year_end_adjustments):
                self.year_end_table.setItem(row, 0, QTableWidgetItem(adjustment["adjustment_number"]))
                self.year_end_table.setItem(row, 1, QTableWidgetItem(adjustment["adjustment_date"]))
                self.year_end_table.setItem(row, 2, QTableWidgetItem(adjustment["adjustment_type"]))
                self.year_end_table.setItem(row, 3, QTableWidgetItem(_fmt_amount(adjustment["total_amount"])))
                
                # Status with color coding
                status_item = QTableWidgetItem(adjustment["status"])
                status_item.setStyleSheet("color: #00B050; font-weight: bold;")
                self.year_end_table.setItem(row, 4, status_item)
            
        except Exception as e:
            print(f"Error refreshing year-end table: {e}")

    def _view_adjustment_details(self, adjustment):
        """View adjustment details"""
        details = f"""
Adjustment Details

Number: {adjustment['adjustment_number']}
Date: {adjustment['adjustment_date']}
Type: {adjustment['adjustment_type']}
Description: {adjustment['description']}
Reference: {adjustment.get('reference', '')}
Total Amount: {_fmt_amount(adjustment['total_amount'])}
Status: {adjustment['status']}

Journal Lines:
"""
        
        for i, line in enumerate(adjustment["journal_lines"], 1):
            details += f"""
{i}. Account: {line['account_code']}
   Debit: {_fmt_amount(line['debit'])}
   Credit: {_fmt_amount(line['credit'])}
   Notes: {line.get('notes', '')}
"""
        
        QMessageBox.information(self, "Adjustment Details", details)

    def _clear_adjustment_form(self):
        """Clear adjustment form"""
        self.adjustment_date.setDate(QDate.currentDate())
        self.adjustment_type_combo.setCurrentIndex(0)
        self.adjustment_description.clear()
        self.adjustment_reference.clear()
        
        # Clear journal lines
        self.journal_lines_table.setRowCount(0)
        self.journal_lines = []
        self._add_journal_line()  # Add initial empty line
        self._update_balance_check()
        
        # Generate new adjustment number
        self._generate_adjustment_number()

    def _save_data(self):
        """Save adjustments data to file"""
        try:
            with open(self.adjustments_file, 'w') as f:
                json.dump(self.adjustments_data, f, indent=2)
        except Exception as e:
            print(f"Error saving adjustments data: {e}")

    def _load_data(self):
        """Load adjustments data from file"""
        try:
            if self.adjustments_file.exists():
                with open(self.adjustments_file, 'r') as f:
                    self.adjustments_data = json.load(f)
        except Exception as e:
            print(f"Error loading adjustments data: {e}")
            self.adjustments_data = []

    def get_adjustments_data(self):
        """Get adjustments data"""
        return self.adjustments_data.copy()
