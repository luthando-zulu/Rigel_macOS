#!/usr/bin/env python3
"""
RIGEL Business Reports Center
Categorized reports with professional cards and functional reports
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QGroupBox, QTableWidget,
    QTableWidgetItem, QComboBox, QDateEdit, QCheckBox, QMessageBox,
    QSplitter, QTabWidget, QProgressBar
)
from PyQt6.QtCore import Qt, QDate, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap

from core.chart_of_accounts import coa_manager

# ─────────────────────────────────────────────────────────────────────────────
#  REPORT TYPES AND CATEGORIES
# ─────────────────────────────────────────────────────────────────────────────
REPORT_CATEGORIES = {
    "Financial Reports": {
        "description": "Core financial statements and analysis",
        "reports": [
            {
                "name": "Balance Sheet",
                "description": "Assets, liabilities, and equity statement",
                "icon": "📊",
                "function": "balance_sheet"
            },
            {
                "name": "Income Statement",
                "description": "Revenue and expenses over a period",
                "icon": "💰",
                "function": "income_statement"
            },
            {
                "name": "Cash Flow Statement",
                "description": "Cash inflows and outflows",
                "icon": "💸",
                "function": "cash_flow"
            },
            {
                "name": "Trial Balance",
                "description": "List of all general ledger accounts",
                "icon": "⚖️",
                "function": "trial_balance"
            }
        ]
    },
    "Management Reports": {
        "description": "Operational and management insights",
        "reports": [
            {
                "name": "Profit & Loss",
                "description": "Detailed profit and loss analysis",
                "icon": "📈",
                "function": "profit_loss"
            },
            {
                "name": "Account Summary",
                "description": "Summary of account balances",
                "icon": "📋",
                "function": "account_summary"
            },
            {
                "name": "Transaction History",
                "description": "Historical transaction records",
                "icon": "📜",
                "function": "transaction_history"
            },
            {
                "name": "Budget vs Actual",
                "description": "Budget performance analysis",
                "icon": "🎯",
                "function": "budget_analysis"
            }
        ]
    },
    "Tax Reports": {
        "description": "Tax compliance and preparation reports",
        "reports": [
            {
                "name": "VAT Report",
                "description": "Value Added Tax summary and details",
                "icon": "🧾",
                "function": "vat_report"
            },
            {
                "name": "Tax Summary",
                "description": "Tax liabilities and payments",
                "icon": "💼",
                "function": "tax_summary"
            },
            {
                "name": "PAYE Report",
                "description": "Pay As You Earn tax report",
                "icon": "👥",
                "function": "paye_report"
            },
            {
                "name": "Annual Tax Return",
                "description": "Comprehensive annual tax filing",
                "icon": "📄",
                "function": "annual_tax"
            }
        ]
    },
    "Payroll Reports": {
        "description": "Employee compensation and payroll reports",
        "reports": [
            {
                "name": "Payroll Summary",
                "description": "Monthly payroll summary",
                "icon": "💵",
                "function": "payroll_summary"
            },
            {
                "name": "Employee Payslips",
                "description": "Individual employee payslips",
                "icon": "📝",
                "function": "payslips"
            },
            {
                "name": "Statutory Deductions",
                "description": "PAYE, UIF, SDL calculations",
                "icon": "🏛️",
                "function": "statutory_deductions"
            },
            {
                "name": "Leave Report",
                "description": "Employee leave balances and usage",
                "icon": "🏖️",
                "function": "leave_report"
            }
        ]
    }
}

# ─────────────────────────────────────────────────────────────────────────────
#  REPORTS CENTER MAIN WIDGET
# ─────────────────────────────────────────────────────────────────────────────
class ReportsCenter(QWidget):
    """Main reports center with categorized cards"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_report = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)

        title = QLabel("Reports Center")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2C3E50;
        """)

        subtitle = QLabel("Generate professional financial reports and statements")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #6A7575;
        """)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Create splitter for categories and report viewer
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E0E0E0;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #00A651;
            }
        """)

        # Left panel - Categories
        self.categories_panel = self.create_categories_panel()
        splitter.addWidget(self.categories_panel)

        # Right panel - Report viewer
        self.report_viewer = self.create_report_viewer()
        splitter.addWidget(self.report_viewer)

        # Set splitter proportions
        splitter.setSizes([400, 800])

        layout.addWidget(splitter)

    def create_categories_panel(self) -> QWidget:
        """Create categories panel with report cards"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #F8F9FA;
                border-right: 1px solid #E0E0E0;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Scroll area for categories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        categories_widget = QWidget()
        categories_layout = QVBoxLayout(categories_widget)
        categories_layout.setSpacing(25)

        # Create category sections
        for category_name, category_data in REPORT_CATEGORIES.items():
            category_section = self.create_category_section(category_name, category_data)
            categories_layout.addWidget(category_section)

        categories_layout.addStretch()
        scroll_area.setWidget(categories_widget)
        layout.addWidget(scroll_area)

        return panel

    def create_category_section(self, category_name: str, category_data: Dict) -> QWidget:
        """Create a category section with report cards"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Category header
        header = QLabel(category_name)
        header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2C3E50;
            padding-bottom: 5px;
            border-bottom: 2px solid #00A651;
        """)
        layout.addWidget(header)

        # Category description
        desc = QLabel(category_data["description"])
        desc.setStyleSheet("""
            font-size: 12px;
            color: #6A7575;
            margin-bottom: 10px;
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Reports grid
        reports_grid = QGridLayout()
        reports_grid.setSpacing(10)

        reports = category_data["reports"]
        for i, report in enumerate(reports):
            row = i // 2
            col = i % 2

            report_card = self.create_report_card(report)
            reports_grid.addWidget(report_card, row, col)

        layout.addLayout(reports_grid)

        return section

    def create_report_card(self, report_data: Dict) -> QPushButton:
        """Create a report card button"""
        card = QPushButton()
        card.setFixedSize(170, 100)
        card.setProperty("report_function", report_data["function"])

        # Card layout
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Icon
        icon = QLabel(report_data["icon"])
        icon.setStyleSheet("font-size: 24px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title = QLabel(report_data["name"])
        title.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #2C3E50;
            text-align: center;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)

        # Description
        desc = QLabel(report_data["description"])
        desc.setStyleSheet("""
            font-size: 10px;
            color: #6A7575;
            text-align: center;
        """)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(desc)

        # Styling
        card.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #F8F9FA;
                border-color: #00A651;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #E9ECEF;
                transform: translateY(0px);
            }
        """)

        card.clicked.connect(lambda: self.on_report_selected(report_data))
        return card

    def create_report_viewer(self) -> QWidget:
        """Create report viewer panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Report header
        self.report_header = QLabel("Select a report from the categories on the left")
        self.report_header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2C3E50;
            text-align: center;
        """)
        self.report_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.report_header)

        # Report controls (initially hidden)
        self.report_controls = self.create_report_controls()
        self.report_controls.hide()
        layout.addWidget(self.report_controls)

        # Report content area
        self.report_content = QWidget()
        self.report_content.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)

        content_layout = QVBoxLayout(self.report_content)
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.placeholder_label = QLabel("Report content will appear here")
        self.placeholder_label.setStyleSheet("""
            font-size: 16px;
            color: #6A7575;
            text-align: center;
        """)
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.placeholder_label)

        layout.addWidget(self.report_content)

        return panel

    def create_report_controls(self) -> QWidget:
        """Create report generation controls"""
        controls = QWidget()
        layout = QHBoxLayout(controls)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Date range controls
        date_layout = QHBoxLayout()
        date_layout.setSpacing(10)

        date_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.setCalendarPopup(True)
        date_layout.addWidget(self.from_date)

        date_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        date_layout.addWidget(self.to_date)

        layout.addLayout(date_layout)

        # Generate button
        self.generate_button = QPushButton("Generate Report")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #00A651;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #008a45;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_button.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_button)

        # Export button
        self.export_button = QPushButton("Export PDF")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.export_button.clicked.connect(self.export_report)
        self.export_button.setEnabled(False)
        layout.addWidget(self.export_button)

        layout.addStretch()

        return controls

    def on_report_selected(self, report_data: Dict):
        """Handle report selection"""
        self.current_report = report_data
        self.report_header.setText(f"{report_data['name']} - {report_data['description']}")
        self.report_controls.show()
        self.placeholder_label.setText(f"Click 'Generate Report' to create the {report_data['name']}")

        # Reset report content
        self.clear_report_content()
        self.export_button.setEnabled(False)

    def generate_report(self):
        """Generate the selected report"""
        if not self.current_report:
            return

        # Show loading state
        self.generate_button.setEnabled(False)
        self.generate_button.setText("Generating...")
        self.placeholder_label.setText("Generating report...")

        # Get date range
        from_date = self.from_date.date().toPyDate()
        to_date = self.to_date.date().toPyDate()

        # Generate report based on type
        report_function = self.current_report["function"]
        report_content = self.generate_report_content(report_function, from_date, to_date)

        # Display report
        self.display_report(report_content)

        # Reset button
        self.generate_button.setEnabled(True)
        self.generate_button.setText("Generate Report")
        self.export_button.setEnabled(True)

    def generate_report_content(self, report_type: str, from_date: date, to_date: date) -> Dict[str, Any]:
        """Generate report content based on type"""
        # This is a placeholder - in real implementation, this would query the database
        # and generate actual financial data

        if report_type == "balance_sheet":
            return self.generate_balance_sheet(from_date, to_date)
        elif report_type == "income_statement":
            return self.generate_income_statement(from_date, to_date)
        elif report_type == "trial_balance":
            return self.generate_trial_balance(from_date, to_date)
        elif report_type == "cash_flow":
            return self.generate_cash_flow(from_date, to_date)
        else:
            return {
                "title": f"{self.current_report['name']} Report",
                "date_range": f"{from_date} to {to_date}",
                "data": [["Feature", "Coming Soon"], ["Status", "Under Development"]],
                "headers": ["Item", "Value"]
            }

    def generate_balance_sheet(self, from_date: date, to_date: date) -> Dict[str, Any]:
        """Generate balance sheet data"""
        return {
            "title": "Balance Sheet",
            "date_range": f"As at {to_date}",
            "sections": [
                {
                    "title": "Assets",
                    "data": [
                        ["Bank — FNB Cheque", "R 150,000.00"],
                        ["Bank — FNB Savings", "R 50,000.00"],
                        ["Accounts Receivable", "R 25,000.00"],
                        ["Inventory", "R 75,000.00"],
                        ["Fixed Assets", "R 200,000.00"],
                        ["Total Assets", "R 500,000.00"]
                    ]
                },
                {
                    "title": "Liabilities",
                    "data": [
                        ["Accounts Payable", "R 30,000.00"],
                        ["VAT Output", "R 15,000.00"],
                        ["Total Liabilities", "R 45,000.00"]
                    ]
                },
                {
                    "title": "Equity",
                    "data": [
                        ["Share Capital", "R 400,000.00"],
                        ["Retained Earnings", "R 55,000.00"],
                        ["Total Equity", "R 455,000.00"]
                    ]
                }
            ]
        }

    def generate_income_statement(self, from_date: date, to_date: date) -> Dict[str, Any]:
        """Generate income statement data"""
        return {
            "title": "Income Statement",
            "date_range": f"For the period {from_date} to {to_date}",
            "sections": [
                {
                    "title": "Revenue",
                    "data": [
                        ["Sales Revenue", "R 300,000.00"],
                        ["Other Income", "R 10,000.00"],
                        ["Total Revenue", "R 310,000.00"]
                    ]
                },
                {
                    "title": "Expenses",
                    "data": [
                        ["Cost of Sales", "R 150,000.00"],
                        ["Operating Expenses", "R 80,000.00"],
                        ["Depreciation", "R 20,000.00"],
                        ["Total Expenses", "R 250,000.00"]
                    ]
                },
                {
                    "title": "Net Profit",
                    "data": [
                        ["Net Profit", "R 60,000.00"]
                    ]
                }
            ]
        }

    def generate_trial_balance(self, from_date: date, to_date: date) -> Dict[str, Any]:
        """Generate trial balance data"""
        return {
            "title": "Trial Balance",
            "date_range": f"As at {to_date}",
            "data": [
                ["1000", "Bank — FNB Cheque", "R 150,000.00", ""],
                ["1001", "Bank — FNB Savings", "R 50,000.00", ""],
                ["1100", "Accounts Receivable", "R 25,000.00", ""],
                ["4000", "Sales Revenue", "", "R 300,000.00"],
                ["5000", "Cost of Sales", "R 150,000.00", ""],
                ["5100", "Operating Expenses", "R 80,000.00", ""],
                ["3000", "Share Capital", "", "R 400,000.00"],
                ["2000", "Accounts Payable", "", "R 30,000.00"]
            ],
            "headers": ["Account Code", "Account Name", "Debit", "Credit"]
        }

    def generate_cash_flow(self, from_date: date, to_date: date) -> Dict[str, Any]:
        """Generate cash flow statement data"""
        return {
            "title": "Cash Flow Statement",
            "date_range": f"For the period {from_date} to {to_date}",
            "sections": [
                {
                    "title": "Operating Activities",
                    "data": [
                        ["Cash from Operations", "R 80,000.00"],
                        ["Changes in Working Capital", "R (10,000.00)"],
                        ["Net Cash from Operations", "R 70,000.00"]
                    ]
                },
                {
                    "title": "Investing Activities",
                    "data": [
                        ["Purchase of Fixed Assets", "R (50,000.00)"],
                        ["Net Cash from Investing", "R (50,000.00)"]
                    ]
                },
                {
                    "title": "Financing Activities",
                    "data": [
                        ["Share Capital Issued", "R 100,000.00"],
                        ["Net Cash from Financing", "R 100,000.00"]
                    ]
                },
                {
                    "title": "Net Cash Flow",
                    "data": [
                        ["Net Increase in Cash", "R 120,000.00"],
                        ["Cash at Beginning", "R 80,000.00"],
                        ["Cash at End", "R 200,000.00"]
                    ]
                }
            ]
        }

    def display_report(self, report_data: Dict[str, Any]):
        """Display the generated report"""
        self.clear_report_content()

        layout = self.report_content.layout()

        # Report title
        title = QLabel(report_data["title"])
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)

        # Date range
        date_range = QLabel(report_data.get("date_range", ""))
        date_range.setStyleSheet("""
            font-size: 14px;
            color: #6A7575;
            margin-bottom: 20px;
        """)
        layout.addWidget(date_range)

        # Report content
        if "sections" in report_data:
            # Multi-section report
            for section in report_data["sections"]:
                section_group = QGroupBox(section["title"])
                section_group.setStyleSheet("""
                    QGroupBox {
                        font-size: 16px;
                        font-weight: bold;
                        color: #2C3E50;
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

                section_layout = QVBoxLayout(section_group)

                # Create table for section data
                table = QTableWidget()
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(["Item", "Amount"])
                table.horizontalHeader().setStretchLastSection(True)
                table.setAlternatingRowColors(True)
                table.setStyleSheet("""
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

                table.setRowCount(len(section["data"]))
                for row, (item, amount) in enumerate(section["data"]):
                    table.setItem(row, 0, QTableWidgetItem(item))
                    table.setItem(row, 1, QTableWidgetItem(amount))

                table.resizeColumnsToContents()
                section_layout.addWidget(table)
                layout.addWidget(section_group)

        elif "data" in report_data:
            # Single table report
            table = QTableWidget()
            headers = report_data.get("headers", ["Column 1", "Column 2"])
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.horizontalHeader().setStretchLastSection(True)
            table.setAlternatingRowColors(True)
            table.setStyleSheet("""
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

            table.setRowCount(len(report_data["data"]))
            for row, row_data in enumerate(report_data["data"]):
                for col, cell_data in enumerate(row_data):
                    table.setItem(row, col, QTableWidgetItem(str(cell_data)))

            table.resizeColumnsToContents()
            layout.addWidget(table)

    def clear_report_content(self):
        """Clear the report content area"""
        layout = self.report_content.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Re-add placeholder
        self.placeholder_label = QLabel("Report content will appear here")
        self.placeholder_label.setStyleSheet("""
            font-size: 16px;
            color: #6A7575;
            text-align: center;
        """)
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.placeholder_label)

    def export_report(self):
        """Export report to PDF"""
        if not self.current_report:
            return

        # Placeholder for PDF export functionality
        QMessageBox.information(self, "Export",
                              "PDF export functionality will be implemented in the next version.")

# ─────────────────────────────────────────────────────────────────────────────
#  MODULE INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────
def create_reports_center(main_window) -> ReportsCenter:
    """Factory function to create reports center"""
    return ReportsCenter(main_window)

if __name__ == "__main__":
    # Test the reports center
    app = QApplication(sys.argv)

    # Mock main window
    class MockMainWindow:
        pass

    window = MockMainWindow()
    reports = create_reports_center(window)
    reports.show()

    sys.exit(app.exec())