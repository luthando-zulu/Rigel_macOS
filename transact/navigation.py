#!/usr/bin/env python3
"""
Transact Module Navigation Handler
Implements TRN-001 to TRN-004 test cases for navigation and session management
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QFrame, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

class NavigationHandler(QWidget):
    """Navigation Handler for Transact Module - Implements TRN-001 to TRN-004"""
    
    # Signals
    navigation_requested = pyqtSignal(str)  # Page name
    logout_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_page = "main_index"
        self.session_data = {}
        
        # Data file paths
        self.data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.data_dir / "session.json"
        
        self._build_ui()
        self._load_session()

    def _build_ui(self):
        """Build navigation UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def navigate_to_page(self, page_name: str):
        """TRN-001: Navigation routing from any screen"""
        try:
            # Validate page exists
            valid_pages = [
                "main_index", "registration", "index", "trial_balance",
                "general_ledger", "vat", "performance", "balance_sheet",
                "cash_book", "customers", "suppliers", "employees", "payslips",
                "inventories", "assets", "investments", "loans", "directors", "projects"
            ]
            
            if page_name not in valid_pages:
                raise ValueError(f"Invalid page: {page_name}")
            
            # Update current page
            self.current_page = page_name
            self.session_data['current_page'] = page_name
            self.session_data['last_navigation'] = datetime.now().isoformat()
            
            # Emit navigation signal
            self.navigation_requested.emit(page_name)
            
            # Save session
            self._save_session()
            
        except Exception as e:
            QMessageBox.critical(self, "Navigation Error", f"Failed to navigate to {page_name}: {str(e)}")

    def create_bottom_menu(self):
        """TRN-002: Left/Bottom Menu navigation"""
        bottom_menu = QFrame()
        bottom_menu.setFixedHeight(60)
        bottom_menu.setStyleSheet("""
            QFrame {
                background: #2A3638;
                border-top: 1px solid #1E2A2A;
            }
        """)
        
        layout = QHBoxLayout(bottom_menu)
        layout.setContentsMargins(20, 5, 20, 5)
        
        # Quick navigation buttons
        quick_nav_buttons = [
            ("🏠", "Home", "main_index"),
            ("📊", "Dashboard", "main_index"),
            ("💰", "Cash Book", "cash_book"),
            ("👥", "Customers", "customers"),
            ("📋", "Suppliers", "suppliers"),
            ("💼", "Payroll", "employees"),
            ("📦", "Inventory", "inventories"),
            ("🏗️", "Assets", "assets"),
            ("👔", "Directors", "directors"),
            ("📈", "Projects", "projects"),
            ("⚙️", "Settings", "settings"),
            ("🚪", "Logout", "logout")
        ]
        
        for icon, tooltip, page in quick_nav_buttons:
            btn = QPushButton(icon)
            btn.setFixedSize(40, 40)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 20px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
                QPushButton:pressed {
                    background: rgba(255, 255, 255, 0.2);
                }
            """)
            
            if page == "logout":
                btn.clicked.connect(self._logout)
            else:
                btn.clicked.connect(lambda checked, p=page: self.navigate_to_page(p))
            
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Session info
        session_label = QLabel("Session Active")
        session_label.setStyleSheet("color: #00B050; font-size: 12px;")
        layout.addWidget(session_label)
        
        return bottom_menu

    def create_left_menu(self):
        """TRN-002: Left/Bottom Menu navigation"""
        left_menu = QFrame()
        left_menu.setFixedWidth(200)
        left_menu.setStyleSheet("""
            QFrame {
                background: #1E2A2A;
                border-right: 1px solid #2A3638;
            }
        """)
        
        layout = QVBoxLayout(left_menu)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Logo
        logo_label = QLabel("RIGEL")
        logo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #00B050; padding: 10px;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Navigation sections
        sections = [
            ("Main", ["🏠 Dashboard", "📝 Registration", "📋 Index"]),
            ("Accounting", ["📊 Trial Balance", "📖 General Ledger", "🧾 VAT", 
                          "📈 Performance", "⚖️ Balance Sheet"]),
            ("Banking", ["💰 Cash Book"]),
            ("Business", ["👥 Customers", "📋 Suppliers", "💼 Payroll", "📦 Inventory"]),
            ("Finance", ["🏗️ Assets", "💎 Investments", "💸 Loans"]),
            ("Management", ["👔 Directors", "📈 Projects"]),
        ]
        
        for section_name, items in sections:
            # Section header
            section_label = QLabel(section_name)
            section_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            section_label.setStyleSheet("color: #6A7575; padding: 5px 0px;")
            layout.addWidget(section_label)
            
            # Section items
            for item in items:
                btn = QPushButton(item)
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        border: none;
                        color: #CCCCCC;
                        padding: 8px 12px;
                        text-align: left;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background: #2A3638;
                        color: white;
                    }
                """)
                
                # Extract page name from item
                page_map = {
                    "🏠 Dashboard": "main_index",
                    "📝 Registration": "registration",
                    "📋 Index": "index",
                    "📊 Trial Balance": "trial_balance",
                    "📖 General Ledger": "general_ledger",
                    "🧾 VAT": "vat",
                    "📈 Performance": "performance",
                    "⚖️ Balance Sheet": "balance_sheet",
                    "💰 Cash Book": "cash_book",
                    "👥 Customers": "customers",
                    "📋 Suppliers": "suppliers",
                    "💼 Payroll": "employees",
                    "📦 Inventory": "inventories",
                    "🏗️ Assets": "assets",
                    "💎 Investments": "investments",
                    "💸 Loans": "loans",
                    "👔 Directors": "directors",
                    "📈 Projects": "projects",
                }
                
                page_name = page_map.get(item, "main_index")
                btn.clicked.connect(lambda checked, p=page_name: self.navigate_to_page(p))
                
                layout.addWidget(btn)
            
            layout.addSpacing(10)
        
        layout.addStretch()
        
        return left_menu

    def refresh_dashboard_graphs(self):
        """TRN-003: Dashboard graph refresh logic"""
        try:
            # This would trigger dashboard refresh
            if hasattr(self.parent, 'main_index_panel'):
                # Refresh KPI cards
                if hasattr(self.parent.main_index_panel, 'refresh_kpis'):
                    self.parent.main_index_panel.refresh_kpis()
                
                # Refresh charts
                if hasattr(self.parent.main_index_panel, 'refresh_charts'):
                    self.parent.main_index_panel.refresh_charts()
            
            # Update session
            self.session_data['last_dashboard_refresh'] = datetime.now().isoformat()
            self._save_session()
            
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")

    def _logout(self):
        """TRN-004: Logout session management"""
        try:
            reply = QMessageBox.question(
                self, 
                "Confirm Logout", 
                "Are you sure you want to logout?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Clear session data
                self.session_data = {}
                self._save_session()
                
                # Emit logout signal
                self.logout_requested.emit()
                
        except Exception as e:
            QMessageBox.critical(self, "Logout Error", f"Failed to logout: {str(e)}")

    def get_current_page(self):
        """Get current page"""
        return self.current_page

    def get_session_data(self):
        """Get session data"""
        return self.session_data.copy()

    def _save_session(self):
        """Save session data to file"""
        try:
            session_info = {
                'session_data': self.session_data,
                'last_saved': datetime.now().isoformat()
            }
            with open(self.session_file, 'w') as f:
                json.dump(session_info, f, indent=2)
        except Exception as e:
            print(f"Error saving session: {e}")

    def _load_session(self):
        """Load session data from file"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    session_info = json.load(f)
                    self.session_data = session_info.get('session_data', {})
                    self.current_page = self.session_data.get('current_page', 'main_index')
        except Exception as e:
            print(f"Error loading session: {e}")
            self.session_data = {}
            self.current_page = "main_index"

    def create_navigation_toolbar(self):
        """Create navigation toolbar for main window"""
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border-bottom: 1px solid #E0E0E0;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Navigation buttons
        nav_buttons = [
            ("Home", "main_index"),
            ("Back", "back"),
            ("Forward", "forward"),
            ("Refresh", "refresh"),
        ]
        
        for text, action in nav_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: 1px solid #E0E0E0;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background: #F8F9FA;
                }
            """)
            
            if action == "back":
                btn.clicked.connect(self._navigate_back)
            elif action == "forward":
                btn.clicked.connect(self._navigate_forward)
            elif action == "refresh":
                btn.clicked.connect(self.refresh_dashboard_graphs)
            else:
                btn.clicked.connect(lambda checked, p="main_index": self.navigate_to_page(p))
            
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Current page indicator
        self.page_indicator = QLabel(f"Current: {self.current_page}")
        self.page_indicator.setStyleSheet("color: #6A7575; font-size: 12px;")
        layout.addWidget(self.page_indicator)
        
        return toolbar

    def _navigate_back(self):
        """Navigate to previous page"""
        # Simple back navigation - in a real app, this would maintain history
        self.navigate_to_page("main_index")

    def _navigate_forward(self):
        """Navigate to next page"""
        # Simple forward navigation
        self.navigate_to_page("main_index")

    def update_page_indicator(self, page_name: str):
        """Update the page indicator"""
        if hasattr(self, 'page_indicator'):
            self.page_indicator.setText(f"Current: {page_name}")
