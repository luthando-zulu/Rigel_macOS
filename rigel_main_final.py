#!/usr/bin/env python3
"""
RIGEL Business Professional Accounting System - UI Redesigned
Complete UI overhaul to match screenshots exactly
Modern, professional accounting software look with exact RIGEL branding
"""

import sys
import os
import json
import sqlite3
import hashlib
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QScrollArea, QLabel, QPushButton, QLineEdit,
    QTextEdit, QTableWidget, QTableWidgetItem, QComboBox,
    QDateEdit, QSpinBox, QDoubleSpinBox, QMessageBox, QFrame,
    QSplitter, QTabWidget, QGroupBox, QCheckBox, QProgressBar,
    QDialog, QFormLayout, QGridLayout, QHeaderView, QSizePolicy,
    QMenuBar, QStatusBar, QToolBar, QListWidget, QListWidgetItem,
    QToolButton, QButtonGroup, QRadioButton, QSlider, QCalendarWidget,
    QMenuBar, QMenu, QWizard, QWizardPage
)
from PyQt6.QtCore import Qt, QTimer, QDate, QThread, pyqtSignal, QSize, QMetaObject, Q_ARG, QModelIndex, QRect
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QLinearGradient, QPalette, QCursor, QAction

# Import database handler
from database_handler import db

# Import userforms
from userforms import (
    CustomerFormDialog, SupplierFormDialog, EmployeeFormDialog,
    InventoryFormDialog, FixedAssetFormDialog, ProjectFormDialog,
    DirectorFormDialog
)

# =============================================================================
# CHART OF ACCOUNTS MANAGEMENT
# =============================================================================

class ChartOfAccounts:
    """Chart of Accounts Management System"""
    
    def __init__(self):
        self.accounts = []
        self.load_from_database()
    
    def load_from_database(self):
        """Load Chart of Accounts from database"""
        try:
            self.accounts = db.get_chart_of_accounts()
            if not self.accounts:
                # If database is empty, try to load from CSV
                self.load_from_csv()
        except Exception as e:
            print(f"Error loading Chart of Accounts from database: {e}")
            self.load_from_csv()
    
    def load_from_csv(self):
        """Load Chart of Accounts from RIGEL DEVELOPMENT.csv"""
        csv_path = r"c:\Users\zulub\Desktop\STELLA LUMEN\SORTING\RIGEL 4.1.0\Internal Documents\RIGEL DEVELOPMENT.csv"
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            for line in lines[4:]:  # Skip header rows
                if line.strip() and ';' in line:
                    parts = [part.strip() for part in line.split(';')]
                    if len(parts) >= 4 and parts[0]:  # Account Code exists
                        account = {
                            'code': parts[0],
                            'category': parts[1],
                            'subcategory': parts[2],
                            'name': parts[3],
                            'type': self._get_account_type(parts[1])
                        }
                        self.accounts.append(account)
            
            print(f"Loaded {len(self.accounts)} accounts from Chart of Accounts")
            return True
        except Exception as e:
            print(f"Error loading Chart of Accounts: {e}")
            return False
    
    def _get_account_type(self, category: str) -> str:
        """Determine account type from category"""
        if category.startswith('I'):
            return 'Revenue'
        elif category.startswith('E'):
            return 'Expense'
        elif category.startswith('A'):
            return 'Asset'
        elif category.startswith('L'):
            return 'Liability'
        elif category.startswith('NA'):
            return 'Equity'
        return 'Other'
    
    def get_accounts_by_type(self, account_type: str) -> List[Dict]:
        """Get accounts filtered by type"""
        return [acc for acc in self.accounts if acc['type'] == account_type]
    
    def get_account_by_code(self, code: str) -> Optional[Dict]:
        """Get account by code"""
        for account in self.accounts:
            if account['code'] == code:
                return account
        return None
    
    def get_account_names(self) -> List[str]:
        """Get list of account names for dropdowns"""
        return [f"{acc['code']} - {acc['name']}" for acc in self.accounts]

# RIGEL Professional Color Scheme - Exact Match to Requirements
class RIGELColors:
    # Primary Brand Colors - Exact RIGEL Green
    PRIMARY_GREEN = "#00A651"
    PRIMARY_GREEN_HOVER = "#00b14f"
    PRIMARY_GREEN_PRESSED = "#008f44"
    PRIMARY_GREEN_LIGHT = "#E8F5E8"
    
    # Secondary Colors
    SECONDARY_BLUE = "#0078D7"
    SECONDARY_BLUE_HOVER = "#106EBE"
    DELETE_ORANGE = "#D83B01"
    DELETE_ORANGE_HOVER = "#C23A21"
    
    # Background Colors - Professional Accounting Theme
    BACKGROUND_MAIN = "#FFFFFF"
    BACKGROUND_SIDEBAR = "#F8F9FA"
    BACKGROUND_CARD = "#FFFFFF"
    BACKGROUND_HOVER = "#F5F5F5"
    BACKGROUND_SELECTED = "#E8F5E8"
    BACKGROUND_DARK = "#F3F2F1"
    
    # Text Colors
    TEXT_PRIMARY = "#323130"
    TEXT_SECONDARY = "#605E5C"
    TEXT_DISABLED = "#A19F9D"
    TEXT_WHITE = "#FFFFFF"
    TEXT_LINK = "#0066CC"
    
    # Border Colors
    BORDER_LIGHT = "#E1E1E1"
    BORDER_MEDIUM = "#D2D0CE"
    BORDER_FOCUS = "#00A651"
    BORDER_DARK = "#C8C6C4"
    
    # Status Colors
    SUCCESS = "#107C10"
    WARNING = "#FF8C00"
    ERROR = "#D13438"
    INFO = "#0078D7"
    
    # Financial Colors - Use existing status colors
    POSITIVE = SUCCESS
    NEGATIVE = ERROR
    NEUTRAL = TEXT_SECONDARY

# RIGEL Professional Fonts
class RIGELFonts:
    @staticmethod
    def heading(size: int = 14, bold: bool = True) -> QFont:
        if size <= 0:
            size = 14
        font = QFont("Segoe UI", size)
        font.setBold(bold)
        return font
    
    @staticmethod
    def body(size: int = 11, bold: bool = False) -> QFont:
        if size <= 0:
            size = 11
        font = QFont("Segoe UI", size)
        font.setBold(bold)
        return font
    
    @staticmethod
    def monospace(size: int = 10) -> QFont:
        if size <= 0:
            size = 10
        font = QFont("Consolas", size)
        font.setBold(False)
        return font

# Professional Sidebar Button
class SidebarButton(QPushButton):
    def __init__(self, text: str, icon_text: str = "", parent=None):
        super().__init__(parent)
        self.setText(f"  {icon_text} {text}")
        self.setFixedHeight(45)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Professional styling
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-left: "4px" solid transparent;
                color: {RIGELColors.TEXT_PRIMARY};
                text-align: left;
                padding: "12px" "16px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.BACKGROUND_HOVER};
                border-left: "4px" solid {RIGELColors.PRIMARY_GREEN};
            }}
            QPushButton:pressed {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
    
    def setActive(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {RIGELColors.PRIMARY_GREEN};
                    border-left: "4px" solid {RIGELColors.PRIMARY_GREEN};
                    color: {RIGELColors.TEXT_WHITE};
                    text-align: left;
                    padding: "12px" "16px";
                    font-family: "Segoe UI";
                    font-size: "12px";
                    font-weight: 600;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border-left: "4px" solid transparent;
                    color: {RIGELColors.TEXT_PRIMARY};
                    text-align: left;
                    padding: "12px" "16px";
                    font-family: "Segoe UI";
                    font-size: "12px";
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {RIGELColors.BACKGROUND_HOVER};
                    border-left: "4px" solid {RIGELColors.PRIMARY_GREEN};
                }}
                QPushButton:pressed {{
                    background-color: {RIGELColors.PRIMARY_GREEN};
                    color: {RIGELColors.TEXT_WHITE};
                }}
            """)

# Modern Card Widget
class ModernCard(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        if title:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # Card Header
            header = QLabel(title)
            header.setFont(RIGELFonts.heading(12, True))
            header.setStyleSheet(f"""
                QLabel {{
                    color: {RIGELColors.PRIMARY_GREEN};
                    padding: 16px 20px;
                    background-color: {RIGELColors.BACKGROUND_DARK};
                    border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
                    font-weight: 600;
                }}
            """)
            layout.addWidget(header)
            
            # Content Area
            self.content_widget = QWidget()
            self.content_layout = QVBoxLayout(self.content_widget)
            self.content_layout.setContentsMargins(20, 16, 20, 20)
            self.content_layout.setSpacing(12)
            layout.addWidget(self.content_widget)
    
    def addWidget(self, widget):
        self.content_layout.addWidget(widget)
    
    def addLayout(self, layout):
        self.content_layout.addLayout(layout)

# =============================================================================
# INSTALLATION WIZARD
# =============================================================================

class RIGELInstallationWizard(QWizard):
    """Professional Installation Wizard for RIGEL Business v4.1.0"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RIGEL Business v4.1.0 - Installation Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setOption(QWizard.WizardOption.HaveHelpButton, False)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.setMinimumSize(800, 600)
        
        # Create wizard pages
        self.addPage(self.create_welcome_page())
        self.addPage(self.create_license_page())
        self.addPage(self.create_installation_page())
        self.addPage(self.create_finish_page())
        
        self.setStyleSheet(f"""
            QWizard {{
                background-color: {RIGELColors.BACKGROUND_MAIN};
                font-family: "Segoe UI";
            }}
            QWizardPage {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: 20px;
            }}
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-weight: 600;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
    
    def create_welcome_page(self) -> QWizardPage:
        """Welcome page with RIGEL branding"""
        page = QWizardPage()
        page.setTitle("Welcome to RIGEL Business v4.1.0")
        
        layout = QVBoxLayout()
        
        # Welcome text
        welcome_label = QLabel("""
        <h2 style='color: #00A651; text-align: center;'>Welcome to RIGEL Business</h2>
        <p style='text-align: center; color: #6C757D; font-size: 14px;'>
        Professional Accounting Software for South African Businesses<br>
        <strong>Version 4.1.0</strong><br><br>
        Powered by Stella Lumen
        </p>
        """)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setWordWrap(True)
        layout.addWidget(welcome_label)
        
        # Features
        features_text = QLabel("""
        <div style='padding: 20px; background-color: #F8F9FA; border-radius: "8px"; margin: 10px 0;'>
        <b>Key Features:</b><br>
        • Complete Chart of Accounts Integration<br>
        • Professional Financial Reporting<br>
        • VAT and Tax Management<br>
        • Payroll Processing<br>
        • Inventory Management<br>
        • Project Tracking
        </div>
        """)
        features_text.setWordWrap(True)
        layout.addWidget(features_text)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_license_page(self) -> QWizardPage:
        """License agreement page"""
        page = QWizardPage()
        page.setTitle("License Agreement")
        
        layout = QVBoxLayout()
        
        # License text
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setMaximumHeight(400)
        license_text.setPlainText("RIGEL BUSINESS v4.1.0 - END USER LICENSE AGREEMENT\n\nIMPORTANT: READ CAREFULLY...")
        layout.addWidget(license_text)
        
        # Accept checkbox
        self.accept_checkbox = QCheckBox("I have read and accept the terms of the License Agreement")
        layout.addWidget(self.accept_checkbox)
        
        layout.addStretch()
        page.setLayout(layout)
        
        # Register field
        page.registerField("acceptLicense*", self.accept_checkbox)
        
        return page
    
    def create_installation_page(self) -> QWizardPage:
        """Installation progress page"""
        page = QWizardPage()
        page.setTitle("Installing RIGEL Business")
        
        layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Preparing installation...")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        page.setLayout(layout)
        
        # Start installation timer
        QTimer.singleShot(1000, self.start_installation)
        
        return page
    
    def create_finish_page(self) -> QWizardPage:
        """Finish page"""
        page = QWizardPage()
        page.setTitle("Installation Complete")
        
        layout = QVBoxLayout()
        
        # Success message
        success_label = QLabel("""
        <h2 style='color: #00A651; text-align: center;'>✓ Installation Complete!</h2>
        <p style='text-align: center; color: #6C757D;'>
        RIGEL Business v4.1.0 has been successfully installed.
        </p>
        """)
        success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(success_label)
        
        # Launch button
        self.launch_checkbox = QCheckBox("Launch RIGEL Business")
        self.launch_checkbox.setChecked(True)
        layout.addWidget(self.launch_checkbox)
        
        layout.addStretch()
        page.setLayout(layout)
        
        return page
    
    def start_installation(self):
        """Simulate installation process"""
        self.progress = 0
        self.installation_timer = QTimer()
        self.installation_timer.timeout.connect(self.update_installation)
        self.installation_timer.start(50)
    
    def update_installation(self):
        """Update installation progress"""
        self.progress += 2
        
        if self.progress <= 100:
            self.progress_bar.setValue(self.progress)
            
            if self.progress == 20:
                self.status_label.setText("Installing core components...")
            elif self.progress == 40:
                self.status_label.setText("Configuring Chart of Accounts...")
            elif self.progress == 60:
                self.status_label.setText("Setting up database...")
            elif self.progress == 80:
                self.status_label.setText("Creating shortcuts...")
            elif self.progress == 100:
                self.status_label.setText("Installation complete!")
                self.installation_timer.stop()
                self.button(QWizard.WizardButton.NextButton).setEnabled(True)

# =============================================================================
# LICENSE ACTIVATION DIALOG
# =============================================================================

class LicenseActivationDialog(QDialog):
    """License Activation Dialog"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RIGEL Business - License Activation")
        self.setFixedSize(500, 350)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("License Activation")
        title.setFont(RIGELFonts.heading(16, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Machine ID
        machine_id_layout = QHBoxLayout()
        machine_id_label = QLabel("Machine ID:")
        machine_id_layout.addWidget(machine_id_label)
        
        self.machine_id_edit = QLineEdit()
        self.machine_id_edit.setText(self.generate_machine_id())
        self.machine_id_edit.setReadOnly(True)
        machine_id_layout.addWidget(self.machine_id_edit)
        layout.addLayout(machine_id_layout)
        
        # Company Name
        company_layout = QHBoxLayout()
        company_label = QLabel("Company Name:")
        company_layout.addWidget(company_label)
        
        self.company_edit = QLineEdit()
        company_layout.addWidget(self.company_edit)
        layout.addLayout(company_layout)
        
        # License Key
        license_layout = QHBoxLayout()
        license_label = QLabel("License Key:")
        license_layout.addWidget(license_label)
        
        self.license_edit = QLineEdit()
        self.license_edit.setPlaceholderText("RIGEL-XXXX-XXXX-XXXX-XXXX")
        license_layout.addWidget(self.license_edit)
        layout.addLayout(license_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        activate_btn = QPushButton("Activate")
        activate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: 10px 30px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        activate_btn.clicked.connect(self.activate_license)
        button_layout.addWidget(activate_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def generate_machine_id(self) -> str:
        """Generate unique machine ID"""
        import platform
        machine_string = f"{platform.node()}-{platform.processor()}-{os.getlogin()}"
        return hashlib.md5(machine_string.encode()).hexdigest()[:16].upper()
    
    def activate_license(self):
        """Activate license"""
        company_name = self.company_edit.text().strip()
        license_key = self.license_edit.text().strip()
        
        if not company_name:
            QMessageBox.warning(self, "Warning", "Please enter your company name.")
            return
        
        if not license_key:
            QMessageBox.warning(self, "Warning", "Please enter your license key.")
            return
        
        # For demo purposes, accept any valid format
        QMessageBox.information(self, "Success", f"License activated successfully!\n\nCompany: {company_name}\nLicense: {license_key}")
        self.accept()

# =============================================================================
# LANDING PAGE
# =============================================================================

class LandingPage(QWidget):
    """Main Landing Page with Register Company and Transact buttons"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        layout = QVBoxLayout()
        layout.setSpacing(40)
        
        # Hero section with logo
        hero_layout = QVBoxLayout()
        hero_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # RIGEL Logo (hero size)
        logo_label = QLabel()
        logo_pixmap = QPixmap(300, 300)
        logo_pixmap.fill(QColor(RIGELColors.PRIMARY_GREEN))
        logo_label.setPixmap(logo_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(logo_label)
        
        # Tagline
        tagline = QLabel("Professional Accounting Software")
        tagline.setFont(RIGELFonts.heading(18))
        tagline.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY};")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(tagline)
        
        # Version
        version = QLabel("Version 4.1.0")
        version.setFont(RIGELFonts.body(14))
        version.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY};")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(version)
        
        # Powered by
        powered_by = QLabel("Powered by Stella Lumen")
        powered_by.setFont(RIGELFonts.body(12))
        powered_by.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN}; font-weight: 600;")
        powered_by.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(powered_by)
        
        layout.addLayout(hero_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)
        
        # Register Company button
        register_btn = QPushButton("Register Company")
        register_btn.setMinimumSize(200, 60)
        register_btn.setFont(RIGELFonts.heading(14, True))
        register_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "8px";
                padding: 15px 30px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
                transform: translateY("-2px");
            }}
            QPushButton:pressed {{
                transform: translateY("0px");
            }}
        """)
        register_btn.clicked.connect(self.main_window.show_company_registration)
        buttons_layout.addWidget(register_btn)
        
        # Transact button
        transact_btn = QPushButton("Transact")
        transact_btn.setMinimumSize(200, 60)
        transact_btn.setFont(RIGELFonts.heading(14, True))
        transact_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "8px";
                padding: 15px 30px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
                transform: translateY("-2px");
            }}
            QPushButton:pressed {{
                transform: translateY("0px");
            }}
        """)
        transact_btn.clicked.connect(self.main_window.show_dashboard)
        buttons_layout.addWidget(transact_btn)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        self.setLayout(layout)

# Main Application Window
class RIGELMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RIGEL Business - Complete Version v4.1.0")
        
        # Initialize Chart of Accounts
        self.coa = ChartOfAccounts()
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Set application icon
        self.setWindowIcon(QIcon("assets/logo/rigel_icon.ico") if os.path.exists("assets/logo/rigel_icon.ico") else QIcon())
        
        # Initialize UI
        self.setup_status_bar()
        self.init_ui()
        
        # Show landing page first for v4.1.0
        QTimer.singleShot(100, self.show_landing_page)
        
    def init_ui(self):
        """Initialize the complete UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create main content area
        self.content_stack = QStackedWidget()
        self.create_all_screens()
        main_layout.addWidget(self.content_stack, 1)
        
        # Set default screen
        self.show_dashboard()
    
    def create_menu_bar(self):
        """Create professional menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
                color: {RIGELColors.TEXT_PRIMARY};
                font-family: "Segoe UI";
                font-size: "12px";
            }}
            QMenuBar::item {{
                padding: "8px" "16px";
                background-color: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # File Menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New Company")
        file_menu.addAction("Open Company")
        file_menu.addSeparator()
        file_menu.addAction("Exit")
        
        # Edit Menu
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Preferences")
        edit_menu.addAction("Settings")
        
        # View Menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Dashboard")
        view_menu.addAction("Full Screen")
        
        # Tools Menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Backup")
        tools_menu.addAction("Restore")
        tools_menu.addAction("Utilities")
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About")
        help_menu.addAction("User Guide")
        help_menu.addAction("Contact Support")
    
    def create_toolbar(self):
        """Create professional toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
                spacing: 8px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: transparent;
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "4px";
                padding: 6px;
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QToolButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border-color: {RIGELColors.PRIMARY_GREEN};
            }}
            QToolButton:pressed {{
                background-color: {RIGELColors.PRIMARY_GREEN_PRESSED};
            }}
        """)
        
        # Left side - Logo and Version
        logo_label = QLabel("🏢 RIGEL")
        logo_label.setFont(RIGELFonts.heading(14, True))
        logo_label.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN}; font-weight: bold; padding: 0 16px;")
        toolbar.addWidget(logo_label)
        
        version_label = QLabel("v4.1.0 COMPLETE")
        version_label.setFont(RIGELFonts.body(10))
        version_label.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY}; padding: 0 8px;")
        toolbar.addWidget(version_label)
        
        toolbar.addWidget(QWidget())  # Spacer
        
        # Center - Application Title
        title_label = QLabel("RIGEL Business - Complete Version")
        title_label.setFont(RIGELFonts.heading(13, True))
        title_label.setStyleSheet(f"color: {RIGELColors.TEXT_PRIMARY}; padding: 0 20px;")
        toolbar.addWidget(title_label)
        
        toolbar.addWidget(QWidget())  # Spacer
        
        # Right side - Action buttons
        new_transaction_btn = QPushButton("New Transaction")
        new_transaction_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "4px";
                padding: "8px" "16px";
                font-family: "Segoe UI";
                font-size: "11px";
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        toolbar.addWidget(new_transaction_btn)
        
        reports_btn = QPushButton("Reports")
        reports_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "4px";
                padding: "8px" "16px";
                font-family: "Segoe UI";
                font-size: "11px";
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        toolbar.addWidget(reports_btn)
        
        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {RIGELColors.TEXT_PRIMARY};
                border: 1px solid {RIGELColors.BORDER_MEDIUM};
                border-radius: "4px";
                padding: "8px" "16px";
                font-family: "Segoe UI";
                font-size: "11px";
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.BACKGROUND_HOVER};
                border-color: {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        toolbar.addWidget(settings_btn)
        
        # Admin User Status
        admin_status = QWidget()
        admin_layout = QHBoxLayout(admin_status)
        admin_layout.setContentsMargins(8, 0, 0, 0)
        admin_layout.setSpacing(8)
        
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {RIGELColors.SUCCESS}; font-size: \"12px\";")
        admin_layout.addWidget(status_dot)
        
        admin_label = QLabel("Admin User")
        admin_label.setFont(RIGELFonts.body(10, True))
        admin_label.setStyleSheet(f"color: {RIGELColors.TEXT_PRIMARY};")
        admin_layout.addWidget(admin_label)
        
        toolbar.addWidget(admin_status)
        
        self.addToolBar(toolbar)
    
    def create_sidebar(self):
        """Create professional sidebar with sections"""
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                border-right: 1px solid {RIGELColors.BORDER_LIGHT};
            }}
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Create scroll area for sidebar
        scroll = QScrollArea()
        scroll.setWidgetResizable(False)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                width: "12px";
                border-radius: "6px";
            }}
            QScrollBar::handle:vertical {{
                background-color: {RIGELColors.BORDER_MEDIUM};
                border-radius: "6px";
                min-height: "20px";
            }}
        """)
        
        sidebar_content = QWidget()
        sidebar_content_layout = QVBoxLayout(sidebar_content)
        sidebar_content_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_content_layout.setSpacing(8)
        
        # MAIN Section
        main_section_layout = QVBoxLayout()
        main_section_layout.setContentsMargins(0, 0, 0, 0)
        main_section_layout.setSpacing(4)
        
        main_section_header = QLabel("MAIN")
        main_section_header.setFont(RIGELFonts.heading(9, True))
        main_section_header.setStyleSheet(f"""
            QLabel {{
                color: {RIGELColors.TEXT_SECONDARY};
                padding: "12px" "16px" "8px" "16px";
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: "0.5px";
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-radius: "4px";
            }}
        """)
        main_section_layout.addWidget(main_section_header)
        
        dashboard_btn = SidebarButton("Dashboard", "📊")
        dashboard_btn.clicked.connect(self.show_dashboard)
        main_section_layout.addWidget(dashboard_btn)
        
        registration_btn = SidebarButton("Company Registration", "🏢")
        registration_btn.clicked.connect(self.show_company_registration)
        main_section_layout.addWidget(registration_btn)
        
        setup_btn = SidebarButton("Company Setup", "⚙️")
        setup_btn.clicked.connect(self.show_company_setup)
        main_section_layout.addWidget(setup_btn)
        
        main_section_layout.addStretch()
        sidebar_content_layout.addLayout(main_section_layout)
        
        # ACCOUNTING Section
        accounting_section_layout = QVBoxLayout()
        accounting_section_layout.setContentsMargins(0, 0, 0, 0)
        accounting_section_layout.setSpacing(4)
        
        accounting_section_header = QLabel("ACCOUNTING")
        accounting_section_header.setFont(RIGELFonts.heading(9, True))
        accounting_section_header.setStyleSheet(f"""
            QLabel {{
                color: {RIGELColors.TEXT_SECONDARY};
                padding: "12px" "16px" "8px" "16px";
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: "0.5px";
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-radius: "4px";
            }}
        """)
        accounting_section_layout.addWidget(accounting_section_header)
        
        trial_balance_btn = SidebarButton("Trial Balance", "📋")
        trial_balance_btn.clicked.connect(self.show_trial_balance)
        accounting_section_layout.addWidget(trial_balance_btn)
        
        general_ledger_btn = SidebarButton("General Ledger", "📖")
        general_ledger_btn.clicked.connect(self.show_general_ledger)
        accounting_section_layout.addWidget(general_ledger_btn)
        
        vat_btn = SidebarButton("VAT Management", "🧾")
        vat_btn.clicked.connect(self.show_vat_management)
        accounting_section_layout.addWidget(vat_btn)
        
        balance_sheet_btn = SidebarButton("Balance Sheet", "⚖️")
        balance_sheet_btn.clicked.connect(self.show_balance_sheet)
        accounting_section_layout.addWidget(balance_sheet_btn)
        
        accounting_section_layout.addStretch()
        sidebar_content_layout.addLayout(accounting_section_layout)
        
        # TRANSACTIONS Section
        transactions_section_layout = QVBoxLayout()
        transactions_section_layout.setContentsMargins(0, 0, 0, 0)
        transactions_section_layout.setSpacing(4)
        
        transactions_section_header = QLabel("TRANSACTIONS")
        transactions_section_header.setFont(RIGELFonts.heading(9, True))
        transactions_section_header.setStyleSheet(f"""
            QLabel {{
                color: {RIGELColors.TEXT_SECONDARY};
                padding: "12px" "16px" "8px" "16px";
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: "0.5px";
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-radius: "4px";
            }}
        """)
        transactions_section_layout.addWidget(transactions_section_header)
        
        cash_book_btn = SidebarButton("Cash Book", "💰")
        cash_book_btn.clicked.connect(self.show_cash_book)
        transactions_section_layout.addWidget(cash_book_btn)
        
        customers_btn = SidebarButton("Customers", "👥")
        customers_btn.clicked.connect(self.show_customers)
        transactions_section_layout.addWidget(customers_btn)
        
        suppliers_btn = SidebarButton("Suppliers", "🏪")
        suppliers_btn.clicked.connect(self.show_suppliers)
        transactions_section_layout.addWidget(suppliers_btn)
        
        transactions_section_layout.addStretch()
        sidebar_content_layout.addLayout(transactions_section_layout)
        
        # PAYROLL Section
        payroll_section_layout = QVBoxLayout()
        payroll_section_layout.setContentsMargins(0, 0, 0, 0)
        payroll_section_layout.setSpacing(4)
        
        payroll_section_header = QLabel("PAYROLL")
        payroll_section_header.setFont(RIGELFonts.heading(9, True))
        payroll_section_header.setStyleSheet(f"""
            QLabel {{
                color: {RIGELColors.TEXT_SECONDARY};
                padding: "12px" "16px" "8px" "16px";
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: "0.5px";
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-radius: "4px";
            }}
        """)
        payroll_section_layout.addWidget(payroll_section_header)
        
        employees_btn = SidebarButton("Employees", "👤")
        employees_btn.clicked.connect(self.show_employees)
        payroll_section_layout.addWidget(employees_btn)
        
        payroll_btn = SidebarButton("Payroll", "💵")
        payroll_btn.clicked.connect(self.show_payroll)
        payroll_section_layout.addWidget(payroll_btn)
        
        payslips_btn = SidebarButton("Payslips", "📄")
        payslips_btn.clicked.connect(self.show_payslips)
        payroll_section_layout.addWidget(payslips_btn)
        
        payroll_section_layout.addStretch()
        sidebar_content_layout.addLayout(payroll_section_layout)
        
        # ASSETS Section
        assets_section_layout = QVBoxLayout()
        assets_section_layout.setContentsMargins(0, 0, 0, 0)
        assets_section_layout.setSpacing(4)
        
        assets_section_header = QLabel("ASSETS")
        assets_section_header.setFont(RIGELFonts.heading(9, True))
        assets_section_header.setStyleSheet(f"""
            QLabel {{
                color: {RIGELColors.TEXT_SECONDARY};
                padding: "12px" "16px" "8px" "16px";
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: "0.5px";
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-radius: "4px";
            }}
        """)
        assets_section_layout.addWidget(assets_section_header)
        
        inventory_btn = SidebarButton("Inventory", "📦")
        inventory_btn.clicked.connect(self.show_inventory)
        assets_section_layout.addWidget(inventory_btn)
        
        fixed_assets_btn = SidebarButton("Fixed Assets", "🏢")
        fixed_assets_btn.clicked.connect(self.show_fixed_assets)
        assets_section_layout.addWidget(fixed_assets_btn)
        
        assets_section_layout.addStretch()
        sidebar_content_layout.addLayout(assets_section_layout)
        
        # MANAGEMENT Section
        management_section_layout = QVBoxLayout()
        management_section_layout.setContentsMargins(0, 0, 0, 0)
        management_section_layout.setSpacing(4)
        
        management_section_header = QLabel("MANAGEMENT")
        management_section_header.setFont(RIGELFonts.heading(9, True))
        management_section_header.setStyleSheet(f"""
            QLabel {{
                color: {RIGELColors.TEXT_SECONDARY};
                padding: "12px" "16px" "8px" "16px";
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: "0.5px";
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-radius: "4px";
            }}
        """)
        management_section_layout.addWidget(management_section_header)
        
        directors_btn = SidebarButton("Directors", "👔")
        directors_btn.clicked.connect(self.show_directors)
        management_section_layout.addWidget(directors_btn)
        
        projects_btn = SidebarButton("Projects", "📁")
        projects_btn.clicked.connect(self.show_projects)
        management_section_layout.addWidget(projects_btn)
        
        management_section_layout.addStretch()
        sidebar_content_layout.addLayout(management_section_layout)
        
        # TOOLS Section
        tools_section_layout = QVBoxLayout()
        tools_section_layout.setContentsMargins(0, 0, 0, 0)
        tools_section_layout.setSpacing(4)
        
        tools_section_header = QLabel("TOOLS")
        tools_section_header.setFont(RIGELFonts.heading(9, True))
        tools_section_header.setStyleSheet(f"""
            QLabel {{
                color: {RIGELColors.TEXT_SECONDARY};
                padding: "12px" "16px" "8px" "16px";
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: "0.5px";
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-radius: "4px";
            }}
        """)
        tools_section_layout.addWidget(tools_section_header)
        
        reports_btn = SidebarButton("Reports", "📊")
        reports_btn.clicked.connect(self.show_reports)
        tools_section_layout.addWidget(reports_btn)
        
        settings_btn = SidebarButton("Settings", "⚙️")
        settings_btn.clicked.connect(self.show_settings)
        tools_section_layout.addWidget(settings_btn)
        
        tools_section_layout.addStretch()
        sidebar_content_layout.addLayout(tools_section_layout)
        
        sidebar_content_layout.addStretch()
        
        scroll.setWidget(sidebar_content)
        sidebar_layout.addWidget(scroll)
        
        return sidebar
    
    def create_sidebar_section(self, title: str):
        """Create a sidebar section with header"""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                margin: 0px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Section header
        header = QLabel(title)
        header.setFont(RIGELFonts.heading(9, True))
        header.setStyleSheet(f"""
            QLabel {{
                color: {RIGELColors.TEXT_SECONDARY};
                padding: "12px" "16px" "8px" "16px";
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: "0.5px";
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-radius: "4px";
            }}
        """)
        layout.addWidget(header)
        
        return section
    
    def create_all_screens(self):
        """Create all screens for the application"""
        # Landing Page (v4.1.0 addition)
        self.landing_page = LandingPage(self)
        self.content_stack.addWidget(self.landing_page)
        
        # Dashboard Screen
        self.dashboard_widget = self.create_dashboard_screen()
        self.content_stack.addWidget(self.dashboard_widget)
        
        # Company Registration Screen
        self.registration_widget = self.create_registration_screen()
        self.content_stack.addWidget(self.registration_widget)
        
        # Company Setup Screen
        self.setup_widget = self.create_setup_screen()
        self.content_stack.addWidget(self.setup_widget)
        
        # Trial Balance Screen
        self.trial_balance_widget = self.create_trial_balance_screen()
        self.content_stack.addWidget(self.trial_balance_widget)
        
        # General Ledger Screen
        self.general_ledger_widget = self.create_general_ledger_screen()
        self.content_stack.addWidget(self.general_ledger_widget)
        
        # VAT Management Screen
        self.vat_widget = self.create_vat_screen()
        self.content_stack.addWidget(self.vat_widget)
        
        # Balance Sheet Screen
        self.balance_sheet_widget = self.create_balance_sheet_screen()
        self.content_stack.addWidget(self.balance_sheet_widget)
        
        # Cash Book Screen
        self.cash_book_widget = self.create_cash_book_screen()
        self.content_stack.addWidget(self.cash_book_widget)
        
        # Customers Screen
        self.customers_widget = self.create_customers_screen()
        self.content_stack.addWidget(self.customers_widget)
        
        # Suppliers Screen
        self.suppliers_widget = self.create_suppliers_screen()
        self.content_stack.addWidget(self.suppliers_widget)
        
        # Employees Screen
        self.employees_widget = self.create_employees_screen()
        self.content_stack.addWidget(self.employees_widget)
        
        # Payroll Screen
        self.payroll_widget = self.create_payroll_screen()
        self.content_stack.addWidget(self.payroll_widget)
        
        # Payslips Screen
        self.payslips_widget = self.create_payslips_screen()
        self.content_stack.addWidget(self.payslips_widget)
        
        # Inventory Screen
        self.inventory_widget = self.create_inventory_screen()
        self.content_stack.addWidget(self.inventory_widget)
        
        # Fixed Assets Screen
        self.fixed_assets_widget = self.create_fixed_assets_screen()
        self.content_stack.addWidget(self.fixed_assets_widget)
        
        # Directors Screen
        self.directors_widget = self.create_directors_screen()
        self.content_stack.addWidget(self.directors_widget)
        
        # Projects Screen
        self.projects_widget = self.create_projects_screen()
        self.content_stack.addWidget(self.projects_widget)
        
        # Reports Screen
        self.reports_widget = self.create_reports_screen()
        self.content_stack.addWidget(self.reports_widget)
        
        # Settings Screen
        self.settings_widget = self.create_settings_screen()
        self.content_stack.addWidget(self.settings_widget)
    
    def setup_status_bar(self):
        """Setup professional status bar"""
        status_bar = QStatusBar()
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_SECONDARY};
                border-top: 1px solid {RIGELColors.BORDER_LIGHT};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
        """)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {RIGELColors.TEXT_PRIMARY}; padding: 0 8px;")
        status_bar.addWidget(self.status_label)
        
        # Status indicators
        status_bar.addPermanentWidget(QLabel("●"))
        status_bar.addPermanentWidget(QLabel("Admin User"))
        
        self.setStatusBar(status_bar)
    
    # Navigation Methods
    def show_landing_page(self):
        """Show landing page"""
        self.content_stack.setCurrentWidget(self.landing_page)
        self.status_label.setText("Welcome to RIGEL Business v4.1.0")
    
    def show_dashboard(self):
        """Show dashboard page"""
        self.content_stack.setCurrentWidget(self.dashboard_widget)
        self.status_label.setText("Dashboard loaded")
    
    def show_company_registration(self):
        self.content_stack.setCurrentWidget(self.registration_widget)
        self.status_label.setText("Company Registration loaded")
    
    def show_company_setup(self):
        self.content_stack.setCurrentWidget(self.setup_widget)
        self.status_label.setText("Company Setup loaded")
    
    def show_trial_balance(self):
        self.content_stack.setCurrentWidget(self.trial_balance_widget)
        self.status_label.setText("Trial Balance loaded")
    
    def show_general_ledger(self):
        self.content_stack.setCurrentWidget(self.general_ledger_widget)
        self.status_label.setText("General Ledger loaded")
    
    def show_vat_management(self):
        self.content_stack.setCurrentWidget(self.vat_widget)
        self.status_label.setText("VAT Management loaded")
    
    def show_balance_sheet(self):
        self.content_stack.setCurrentWidget(self.balance_sheet_widget)
        self.status_label.setText("Balance Sheet loaded")
    
    def show_cash_book(self):
        self.content_stack.setCurrentWidget(self.cash_book_widget)
        self.status_label.setText("Cash Book loaded")
    
    def show_customers(self):
        self.content_stack.setCurrentWidget(self.customers_widget)
        self.status_label.setText("Customers loaded")
    
    def show_suppliers(self):
        self.content_stack.setCurrentWidget(self.suppliers_widget)
        self.status_label.setText("Suppliers loaded")
    
    def show_employees(self):
        self.content_stack.setCurrentWidget(self.employees_widget)
        self.status_label.setText("Employees loaded")
    
    def show_payroll(self):
        self.content_stack.setCurrentWidget(self.payroll_widget)
        self.status_label.setText("Payroll loaded")
    
    def show_payslips(self):
        self.content_stack.setCurrentWidget(self.payslips_widget)
        self.status_label.setText("Payslips loaded")
    
    def show_inventory(self):
        self.content_stack.setCurrentWidget(self.inventory_widget)
        self.status_label.setText("Inventory loaded")
    
    def show_fixed_assets(self):
        self.content_stack.setCurrentWidget(self.fixed_assets_widget)
        self.status_label.setText("Fixed Assets loaded")
    
    def show_directors(self):
        self.content_stack.setCurrentWidget(self.directors_widget)
        self.status_label.setText("Directors loaded")
    
    def show_projects(self):
        self.content_stack.setCurrentWidget(self.projects_widget)
        self.status_label.setText("Projects loaded")
    
    def show_reports(self):
        self.content_stack.setCurrentWidget(self.reports_widget)
        self.status_label.setText("Reports loaded")
    
    def show_settings(self):
        self.content_stack.setCurrentWidget(self.settings_widget)
        self.status_label.setText("Settings loaded")
    
    # Screen Creation Methods (simplified for now - will implement detailed screens next)
    def create_dashboard_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Dashboard")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # KPI Cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(20)
        
        # Cash Balance Card
        cash_card = ModernCard("Cash Balance")
        cash_balance = QLabel("R 125,234.50")
        cash_balance.setFont(RIGELFonts.heading(16, True))
        cash_balance.setStyleSheet(f"color: {RIGELColors.POSITIVE};")
        cash_card.addWidget(cash_balance)
        cards_layout.addWidget(cash_card, 0, 0)
        
        # Accounts Receivable Card
        receivable_card = ModernCard("Accounts Receivable")
        receivable_balance = QLabel("R 45,678.00")
        receivable_balance.setFont(RIGELFonts.heading(16, True))
        receivable_balance.setStyleSheet(f"color: {RIGELColors.NEUTRAL};")
        receivable_card.addWidget(receivable_balance)
        cards_layout.addWidget(receivable_card, 0, 1)
        
        # Accounts Payable Card
        payable_card = ModernCard("Accounts Payable")
        payable_balance = QLabel("R 23,456.00")
        payable_balance.setFont(RIGELFonts.heading(16, True))
        payable_balance.setStyleSheet(f"color: {RIGELColors.WARNING};")
        payable_card.addWidget(payable_balance)
        cards_layout.addWidget(payable_card, 0, 2)
        
        # Total Assets Card
        assets_card = ModernCard("Total Fixed Assets")
        assets_balance = QLabel("R 1,234,567.00")
        assets_balance.setFont(RIGELFonts.heading(16, True))
        assets_balance.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        assets_card.addWidget(assets_balance)
        cards_layout.addWidget(assets_card, 1, 0)
        
        layout.addLayout(cards_layout)
        layout.addStretch()
        
        return widget
    
    def create_registration_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Company Registration")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Registration form with tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                background-color: {RIGELColors.BACKGROUND_CARD};
                padding: "0px";
            }}
            QTabWidget::tab-bar {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTabBar::tab {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "24px";
                margin-right: "2px";
                border-top-left-radius: "4px";
                border-top-right-radius: "4px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # Company Details Tab
        company_tab = QWidget()
        company_layout = QVBoxLayout(company_tab)
        company_layout.setContentsMargins(30, 30, 30, 30)
        company_layout.setSpacing(16)
        
        company_card = ModernCard("Company Information")
        company_form = QFormLayout()
        company_form.setSpacing(12)
        
        company_name = QLineEdit()
        company_name.setPlaceholderText("Enter company name")
        company_form.addRow("Company Name *:", company_name)
        
        trading_name = QLineEdit()
        trading_name.setPlaceholderText("Enter trading name")
        company_form.addRow("Trading Name *:", trading_name)
        
        registration_number = QLineEdit()
        registration_number.setPlaceholderText("Enter registration number")
        company_form.addRow("Registration Number *:", registration_number)
        
        tax_number = QLineEdit()
        tax_number.setPlaceholderText("Enter tax number")
        company_form.addRow("Tax Number *:", tax_number)
        
        company_type = QComboBox()
        company_type.addItems(["Private Company", "Public Company", "Partnership", "Sole Proprietor"])
        company_form.addRow("Company Type *:", company_type)
        
        industry = QComboBox()
        industry.addItems(["Manufacturing", "Retail", "Services", "Technology", "Construction"])
        company_form.addRow("Industry *:", industry)
        
        company_card.addLayout(company_form)
        company_layout.addWidget(company_card)
        company_layout.addStretch()
        
        tab_widget.addTab(company_tab, "Company Details")
        
        # Contact Information Tab
        contact_tab = QWidget()
        contact_layout = QVBoxLayout(contact_tab)
        contact_layout.setContentsMargins(30, 30, 30, 30)
        contact_layout.setSpacing(16)
        
        contact_card = ModernCard("Contact Information")
        contact_form = QFormLayout()
        contact_form.setSpacing(12)
        
        physical_address = QLineEdit()
        physical_address.setPlaceholderText("Enter physical address")
        contact_form.addRow("Physical Address *:", physical_address)
        
        postal_address = QLineEdit()
        postal_address.setPlaceholderText("Enter postal address")
        contact_form.addRow("Postal Address:", postal_address)
        
        phone_number = QLineEdit()
        phone_number.setPlaceholderText("Enter phone number")
        contact_form.addRow("Phone Number *:", phone_number)
        
        email_address = QLineEdit()
        email_address.setPlaceholderText("Enter email address")
        contact_form.addRow("Email Address *:", email_address)
        
        website = QLineEdit()
        website.setPlaceholderText("Enter website URL")
        contact_form.addRow("Website:", website)
        
        contact_card.addLayout(contact_form)
        contact_layout.addWidget(contact_card)
        contact_layout.addStretch()
        
        tab_widget.addTab(contact_tab, "Contact Information")
        
        # Financial Information Tab
        financial_tab = QWidget()
        financial_layout = QVBoxLayout(financial_tab)
        financial_layout.setContentsMargins(30, 30, 30, 30)
        financial_layout.setSpacing(16)
        
        financial_card = ModernCard("Financial Information")
        financial_form = QFormLayout()
        financial_form.setSpacing(12)
        
        financial_year_end = QComboBox()
        financial_year_end.addItems(["February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January"])
        financial_form.addRow("Financial Year End *:", financial_year_end)
        
        currency = QComboBox()
        currency.addItems(["ZAR - South African Rand", "USD - US Dollar", "EUR - Euro", "GBP - British Pound"])
        currency.setCurrentText("ZAR - South African Rand")
        financial_form.addRow("Currency *:", currency)
        
        vat_number = QLineEdit()
        vat_number.setPlaceholderText("Enter VAT number")
        financial_form.addRow("VAT Number *:", vat_number)
        
        tax_reference = QLineEdit()
        tax_reference.setPlaceholderText("Enter tax reference")
        financial_form.addRow("Tax Reference *:", tax_reference)
        
        financial_card.addLayout(financial_form)
        financial_layout.addWidget(financial_card)
        financial_layout.addStretch()
        
        tab_widget.addTab(financial_tab, "Financial Information")
        
        layout.addWidget(tab_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        save_btn = QPushButton("Save Registration")
        save_btn.setFont(RIGELFonts.body(11, True))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "12px" "32px";
                font-family: "Segoe UI";
                font-weight: 600;
                min-width: "140px";
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {RIGELColors.PRIMARY_GREEN_PRESSED};
            }}
        """)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(RIGELFonts.body(11, True))
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {RIGELColors.TEXT_PRIMARY};
                border: 1px solid {RIGELColors.BORDER_MEDIUM};
                border-radius: "6px";
                padding: "12px" "32px";
                font-family: "Segoe UI";
                font-weight: 500;
                min-width: "140px";
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.BACKGROUND_HOVER};
                border-color: {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
    
    def create_setup_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Company Setup")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Tab widget for different setup sections
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                background-color: {RIGELColors.BACKGROUND_CARD};
            }}
            QTabBar::tab {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                color: {RIGELColors.TEXT_SECONDARY};
                padding: "12px" "24px";
                border: none;
                border-top-left-radius: "6px";
                border-top-right-radius: "6px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
                min-width: "120px";
            }}
            QTabBar::tab:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # General Settings Tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setContentsMargins(30, 30, 30, 30)
        general_layout.setSpacing(16)
        
        general_card = ModernCard("General Settings")
        general_form = QFormLayout()
        general_form.setSpacing(12)
        
        company_name_setup = QLineEdit()
        company_name_setup.setPlaceholderText("Enter company name")
        general_form.addRow("Company Name *:", company_name_setup)
        
        registration_number_setup = QLineEdit()
        registration_number_setup.setPlaceholderText("Enter registration number")
        general_form.addRow("Registration Number:", registration_number_setup)
        
        tax_number_setup = QLineEdit()
        tax_number_setup.setPlaceholderText("Enter tax number")
        general_form.addRow("Tax Number:", tax_number_setup)
        
        vat_number_setup = QLineEdit()
        vat_number_setup.setPlaceholderText("Enter VAT number")
        general_form.addRow("VAT Number:", vat_number_setup)
        
        financial_year_end_setup = QComboBox()
        financial_year_end_setup.addItems(["February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "January"])
        general_form.addRow("Financial Year End *:", financial_year_end_setup)
        
        currency_setup = QComboBox()
        currency_setup.addItems(["ZAR - South African Rand", "USD - US Dollar", "EUR - Euro", "GBP - British Pound"])
        currency_setup.setCurrentText("ZAR - South African Rand")
        general_form.addRow("Currency *:", currency_setup)
        
        date_format_setup = QComboBox()
        date_format_setup.addItems(["YYYY/MM/DD", "DD/MM/YYYY", "MM/DD/YYYY"])
        date_format_setup.setCurrentText("YYYY/MM/DD")
        general_form.addRow("Date Format *:", date_format_setup)
        
        general_card.addLayout(general_form)
        general_layout.addWidget(general_card)
        general_layout.addStretch()
        
        tab_widget.addTab(general_tab, "General")
        
        # Address Tab
        address_tab = QWidget()
        address_layout = QVBoxLayout(address_tab)
        address_layout.setContentsMargins(30, 30, 30, 30)
        address_layout.setSpacing(16)
        
        address_card = ModernCard("Address Information")
        address_form = QFormLayout()
        address_form.setSpacing(12)
        
        physical_address_setup = QLineEdit()
        physical_address_setup.setPlaceholderText("Enter physical address")
        address_form.addRow("Physical Address:", physical_address_setup)
        
        city_setup = QLineEdit()
        city_setup.setPlaceholderText("Enter city")
        address_form.addRow("City:", city_setup)
        
        province_setup = QLineEdit()
        province_setup.setPlaceholderText("Enter province")
        address_form.addRow("Province:", province_setup)
        
        postal_code_setup = QLineEdit()
        postal_code_setup.setPlaceholderText("Enter postal code")
        address_form.addRow("Postal Code:", postal_code_setup)
        
        country_setup = QLineEdit()
        country_setup.setPlaceholderText("Enter country")
        country_setup.setText("South Africa")
        address_form.addRow("Country:", country_setup)
        
        address_card.addLayout(address_form)
        address_layout.addWidget(address_card)
        address_layout.addStretch()
        
        tab_widget.addTab(address_tab, "Address")
        
        # Contact Tab
        contact_tab = QWidget()
        contact_layout = QVBoxLayout(contact_tab)
        contact_layout.setContentsMargins(30, 30, 30, 30)
        contact_layout.setSpacing(16)
        
        contact_card = ModernCard("Contact Information")
        contact_form = QFormLayout()
        contact_form.setSpacing(12)
        
        phone_setup = QLineEdit()
        phone_setup.setPlaceholderText("Enter phone number")
        contact_form.addRow("Phone Number:", phone_setup)
        
        email_setup = QLineEdit()
        email_setup.setPlaceholderText("Enter email address")
        contact_form.addRow("Email Address:", email_setup)
        
        website_setup = QLineEdit()
        website_setup.setPlaceholderText("Enter website URL")
        contact_form.addRow("Website:", website_setup)
        
        contact_card.addLayout(contact_form)
        contact_layout.addWidget(contact_card)
        contact_layout.addStretch()
        
        tab_widget.addTab(contact_tab, "Contact")
        
        layout.addWidget(tab_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        save_setup_btn = QPushButton("Save Setup")
        save_setup_btn.setFont(RIGELFonts.body(11, True))
        save_setup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "12px" "32px";
                font-family: "Segoe UI";
                font-weight: 600;
                min-width: "140px";
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {RIGELColors.PRIMARY_GREEN_PRESSED};
            }}
        """)
        button_layout.addWidget(save_setup_btn)
        
        cancel_setup_btn = QPushButton("Cancel")
        cancel_setup_btn.setFont(RIGELFonts.body(11, True))
        cancel_setup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {RIGELColors.TEXT_PRIMARY};
                border: 1px solid {RIGELColors.BORDER_MEDIUM};
                border-radius: "6px";
                padding: "12px" "32px";
                font-family: "Segoe UI";
                font-weight: 500;
                min-width: "140px";
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.BACKGROUND_HOVER};
                border-color: {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        button_layout.addWidget(cancel_setup_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
    
    def create_trial_balance_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Trial Balance")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        add_entry_btn = QPushButton("+ Add Entry")
        add_entry_btn.setFont(RIGELFonts.body(11, True))
        add_entry_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        actions_layout.addWidget(add_entry_btn)
        
        edit_entry_btn = QPushButton("Edit Entry")
        edit_entry_btn.setFont(RIGELFonts.body(11, True))
        edit_entry_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        actions_layout.addWidget(edit_entry_btn)
        
        delete_entry_btn = QPushButton("Delete Entry")
        delete_entry_btn.setFont(RIGELFonts.body(11, True))
        delete_entry_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.DELETE_ORANGE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.DELETE_ORANGE_HOVER};
            }}
        """)
        actions_layout.addWidget(delete_entry_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Trial Balance Table
        table_card = ModernCard("Trial Balance Entries")
        table_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.trial_balance_table = QTableWidget()
        self.trial_balance_table.setColumnCount(6)
        self.trial_balance_table.setHorizontalHeaderLabels([
            "Account Code", "Account Name", "Debit", "Credit", "Balance", "Actions"
        ])
        self.trial_balance_table.horizontalHeader().setStretchLastSection(True)
        self.trial_balance_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample data
        self.trial_balance_table.insertRow(0)
        self.trial_balance_table.setItem(0, 0, QTableWidgetItem("1001"))
        self.trial_balance_table.setItem(0, 1, QTableWidgetItem("Cash"))
        self.trial_balance_table.setItem(0, 2, QTableWidgetItem("R 50,000.00"))
        self.trial_balance_table.setItem(0, 3, QTableWidgetItem(""))
        self.trial_balance_table.setItem(0, 4, QTableWidgetItem("R 50,000.00"))
        self.trial_balance_table.setItem(0, 5, QTableWidgetItem(""))
        
        self.trial_balance_table.insertRow(1)
        self.trial_balance_table.setItem(1, 0, QTableWidgetItem("2001"))
        self.trial_balance_table.setItem(1, 1, QTableWidgetItem("Accounts Receivable"))
        self.trial_balance_table.setItem(1, 2, QTableWidgetItem(""))
        self.trial_balance_table.setItem(1, 3, QTableWidgetItem("R 25,000.00"))
        self.trial_balance_table.setItem(1, 4, QTableWidgetItem("R 25,000.00"))
        self.trial_balance_table.setItem(1, 5, QTableWidgetItem(""))
        
        self.trial_balance_table.insertRow(2)
        self.trial_balance_table.setItem(2, 0, QTableWidgetItem("4001"))
        self.trial_balance_table.setItem(2, 1, QTableWidgetItem("Inventory"))
        self.trial_balance_table.setItem(2, 2, QTableWidgetItem("R 15,000.00"))
        self.trial_balance_table.setItem(2, 3, QTableWidgetItem(""))
        self.trial_balance_table.setItem(2, 4, QTableWidgetItem("R 15,000.00"))
        self.trial_balance_table.setItem(2, 5, QTableWidgetItem(""))
        
        # Set column widths
        self.trial_balance_table.setColumnWidth(0, 120)
        self.trial_balance_table.setColumnWidth(1, 200)
        self.trial_balance_table.setColumnWidth(2, 120)
        self.trial_balance_table.setColumnWidth(3, 120)
        self.trial_balance_table.setColumnWidth(4, 120)
        self.trial_balance_table.setColumnWidth(5, 100)
        
        table_card.addWidget(self.trial_balance_table)
        layout.addWidget(table_card)
        
        # Summary Section
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)
        
        total_debit_card = ModernCard("Total Debits")
        total_debit_label = QLabel("R 65,000.00")
        total_debit_label.setFont(RIGELFonts.heading(16, True))
        total_debit_label.setStyleSheet(f"color: {RIGELColors.NEUTRAL};")
        total_debit_card.addWidget(total_debit_label)
        summary_layout.addWidget(total_debit_card)
        
        total_credit_card = ModernCard("Total Credits")
        total_credit_label = QLabel("R 65,000.00")
        total_credit_label.setFont(RIGELFonts.heading(16, True))
        total_credit_label.setStyleSheet(f"color: {RIGELColors.NEUTRAL};")
        total_credit_card.addWidget(total_credit_label)
        summary_layout.addWidget(total_credit_card)
        
        balance_card = ModernCard("Balance")
        balance_label = QLabel("R 0.00")
        balance_label.setFont(RIGELFonts.heading(16, True))
        balance_label.setStyleSheet(f"color: {RIGELColors.SUCCESS};")
        balance_card.addWidget(balance_label)
        summary_layout.addWidget(balance_card)
        
        layout.addLayout(summary_layout)
        layout.addStretch()
        
        return widget
    
    def create_general_ledger_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("General Ledger")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Filters and controls
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(12)
        
        account_label = QLabel("Account:")
        account_label.setFont(RIGELFonts.body(12))
        filters_layout.addWidget(account_label)
        
        account_combo = QComboBox()
        account_combo.addItems(["All Accounts", "1001 - Cash", "2001 - Accounts Receivable", "4001 - Inventory", "5001 - Accounts Payable"])
        account_combo.setStyleSheet(f"""
            QComboBox {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "4px";
                padding: "8px" "12px";
                font-family: "Segoe UI";
                font-size: "12px";
                min-width: 200px;
            }}
            QComboBox:focus {{
                border-color: {RIGELColors.BORDER_FOCUS};
            }}
        """)
        filters_layout.addWidget(account_combo)
        
        date_from_label = QLabel("From:")
        date_from_label.setFont(RIGELFonts.body(12))
        filters_layout.addWidget(date_from_label)
        
        date_from = QDateEdit()
        date_from.setDate(QDate.currentDate().addMonths(-1))
        date_from.setDisplayFormat("yyyy/MM/dd")
        date_from.setStyleSheet(f"""
            QDateEdit {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "4px";
                padding: "8px" "12px";
                font-family: "Segoe UI";
                font-size: "12px";
            }}
            QDateEdit:focus {{
                border-color: {RIGELColors.BORDER_FOCUS};
            }}
        """)
        filters_layout.addWidget(date_from)
        
        date_to_label = QLabel("To:")
        date_to_label.setFont(RIGELFonts.body(12))
        filters_layout.addWidget(date_to_label)
        
        date_to = QDateEdit()
        date_to.setDate(QDate.currentDate())
        date_to.setDisplayFormat("yyyy/MM/dd")
        date_to.setStyleSheet(f"""
            QDateEdit {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "4px";
                padding: "8px" "12px";
                font-family: "Segoe UI";
                font-size: "12px";
            }}
            QDateEdit:focus {{
                border-color: {RIGELColors.BORDER_FOCUS};
            }}
        """)
        filters_layout.addWidget(date_to)
        
        search_btn = QPushButton("Search")
        search_btn.setFont(RIGELFonts.body(11, True))
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        filters_layout.addWidget(search_btn)
        
        export_btn = QPushButton("Export")
        export_btn.setFont(RIGELFonts.body(11, True))
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        filters_layout.addWidget(export_btn)
        
        filters_layout.addStretch()
        layout.addLayout(filters_layout)
        
        # General Ledger Table
        ledger_card = ModernCard("General Ledger Transactions")
        ledger_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.general_ledger_table = QTableWidget()
        self.general_ledger_table.setColumnCount(8)
        self.general_ledger_table.setHorizontalHeaderLabels([
            "Date", "Reference", "Account", "Description", "Debit", "Credit", "Balance", "Actions"
        ])
        self.general_ledger_table.horizontalHeader().setStretchLastSection(True)
        self.general_ledger_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample data
        self.general_ledger_table.insertRow(0)
        self.general_ledger_table.setItem(0, 0, QTableWidgetItem("2024/01/15"))
        self.general_ledger_table.setItem(0, 1, QTableWidgetItem("GL001"))
        self.general_ledger_table.setItem(0, 2, QTableWidgetItem("1001 - Cash"))
        self.general_ledger_table.setItem(0, 3, QTableWidgetItem("Opening Balance"))
        self.general_ledger_table.setItem(0, 4, QTableWidgetItem("R 50,000.00"))
        self.general_ledger_table.setItem(0, 5, QTableWidgetItem(""))
        self.general_ledger_table.setItem(0, 6, QTableWidgetItem("R 50,000.00"))
        self.general_ledger_table.setItem(0, 7, QTableWidgetItem(""))
        
        self.general_ledger_table.insertRow(1)
        self.general_ledger_table.setItem(1, 0, QTableWidgetItem("2024/01/16"))
        self.general_ledger_table.setItem(1, 1, QTableWidgetItem("GL002"))
        self.general_ledger_table.setItem(1, 2, QTableWidgetItem("2001 - Accounts Receivable"))
        self.general_ledger_table.setItem(1, 3, QTableWidgetItem("Cash Sale - Customer A"))
        self.general_ledger_table.setItem(1, 4, QTableWidgetItem(""))
        self.general_ledger_table.setItem(1, 5, QTableWidgetItem("R 5,000.00"))
        self.general_ledger_table.setItem(1, 6, QTableWidgetItem("R 55,000.00"))
        self.general_ledger_table.setItem(1, 7, QTableWidgetItem(""))
        
        self.general_ledger_table.insertRow(2)
        self.general_ledger_table.setItem(2, 0, QTableWidgetItem("2024/01/17"))
        self.general_ledger_table.setItem(2, 1, QTableWidgetItem("GL003"))
        self.general_ledger_table.setItem(2, 2, QTableWidgetItem("5001 - Accounts Payable"))
        self.general_ledger_table.setItem(2, 3, QTableWidgetItem("Office Supplies"))
        self.general_ledger_table.setItem(2, 4, QTableWidgetItem("R 1,500.00"))
        self.general_ledger_table.setItem(2, 5, QTableWidgetItem(""))
        self.general_ledger_table.setItem(2, 6, QTableWidgetItem("R 53,500.00"))
        self.general_ledger_table.setItem(2, 7, QTableWidgetItem(""))
        
        self.general_ledger_table.insertRow(3)
        self.general_ledger_table.setItem(3, 0, QTableWidgetItem("2024/01/18"))
        self.general_ledger_table.setItem(3, 1, QTableWidgetItem("GL004"))
        self.general_ledger_table.setItem(3, 2, QTableWidgetItem("4001 - Inventory"))
        self.general_ledger_table.setItem(3, 3, QTableWidgetItem("Stock Purchase"))
        self.general_ledger_table.setItem(3, 4, QTableWidgetItem("R 2,000.00"))
        self.general_ledger_table.setItem(3, 5, QTableWidgetItem(""))
        self.general_ledger_table.setItem(3, 6, QTableWidgetItem("R 55,500.00"))
        self.general_ledger_table.setItem(3, 7, QTableWidgetItem(""))
        
        self.general_ledger_table.insertRow(4)
        self.general_ledger_table.setItem(4, 0, QTableWidgetItem("2024/01/19"))
        self.general_ledger_table.setItem(4, 1, QTableWidgetItem("GL005"))
        self.general_ledger_table.setItem(4, 2, QTableWidgetItem("1001 - Cash"))
        self.general_ledger_table.setItem(4, 3, QTableWidgetItem("Payment Received - Customer B"))
        self.general_ledger_table.setItem(4, 4, QTableWidgetItem(""))
        self.general_ledger_table.setItem(4, 5, QTableWidgetItem("R 3,000.00"))
        self.general_ledger_table.setItem(4, 6, QTableWidgetItem("R 56,500.00"))
        self.general_ledger_table.setItem(4, 7, QTableWidgetItem(""))
        
        # Style balance column
        for row in range(self.general_ledger_table.rowCount()):
            balance_item = self.general_ledger_table.item(row, 6)
            if balance_item:
                balance_item.setFont(RIGELFonts.body(11, True))
                balance_item.setForeground(QColor(RIGELColors.PRIMARY_GREEN))
        
        # Set column widths
        self.general_ledger_table.setColumnWidth(0, 100)
        self.general_ledger_table.setColumnWidth(1, 80)
        self.general_ledger_table.setColumnWidth(2, 150)
        self.general_ledger_table.setColumnWidth(3, 200)
        self.general_ledger_table.setColumnWidth(4, 100)
        self.general_ledger_table.setColumnWidth(5, 100)
        self.general_ledger_table.setColumnWidth(6, 120)
        self.general_ledger_table.setColumnWidth(7, 80)
        
        ledger_card.addWidget(self.general_ledger_table)
        layout.addWidget(ledger_card)
        
        # Summary Section
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)
        
        total_debit_card = ModernCard("Total Debits")
        total_debit_label = QLabel("R 53,500.00")
        total_debit_label.setFont(RIGELFonts.heading(16, True))
        total_debit_label.setStyleSheet(f"color: {RIGELColors.NEGATIVE};")
        total_debit_card.addWidget(total_debit_label)
        summary_layout.addWidget(total_debit_card)
        
        total_credit_card = ModernCard("Total Credits")
        total_credit_label = QLabel("R 8,000.00")
        total_credit_label.setFont(RIGELFonts.heading(16, True))
        total_credit_label.setStyleSheet(f"color: {RIGELColors.POSITIVE};")
        total_credit_card.addWidget(total_credit_label)
        summary_layout.addWidget(total_credit_card)
        
        balance_summary_card = ModernCard("Net Balance")
        balance_summary_label = QLabel("R 61,500.00")
        balance_summary_label.setFont(RIGELFonts.heading(16, True))
        balance_summary_label.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        balance_summary_card.addWidget(balance_summary_label)
        summary_layout.addWidget(balance_summary_card)
        
        layout.addLayout(summary_layout)
        layout.addStretch()
        
        return widget
    
    def create_vat_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("VAT Management")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # VAT Management with tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                background-color: {RIGELColors.BACKGROUND_CARD};
                padding: "0px";
            }}
            QTabWidget::tab-bar {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTabBar::tab {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "24px";
                margin-right: "2px";
                border-top-left-radius: "4px";
                border-top-right-radius: "4px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # VAT Configuration Tab
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        config_layout.setContentsMargins(30, 30, 30, 30)
        config_layout.setSpacing(16)
        
        config_card = ModernCard("VAT Configuration")
        config_form = QFormLayout()
        config_form.setSpacing(12)
        
        vat_rate = QDoubleSpinBox()
        vat_rate.setPrefix("% ")
        vat_rate.setMaximum(100.00)
        vat_rate.setValue(15.00)
        vat_rate.setDecimals(2)
        config_form.addRow("Standard VAT Rate *:", vat_rate)
        
        vat_number = QLineEdit()
        vat_number.setPlaceholderText("Enter VAT registration number")
        config_form.addRow("VAT Registration Number *:", vat_number)
        
        reporting_period = QComboBox()
        reporting_period.addItems(["Monthly", "Bi-Monthly", "Quarterly", "Annually"])
        config_form.addRow("Reporting Period *:", reporting_period)
        
        filing_method = QComboBox()
        filing_method.addItems(["Electronic Filing", "Manual Filing"])
        config_form.addRow("Filing Method *:", filing_method)
        
        config_card.addLayout(config_form)
        config_layout.addWidget(config_card)
        config_layout.addStretch()
        
        tab_widget.addTab(config_tab, "Configuration")
        
        # VAT Returns Tab
        returns_tab = QWidget()
        returns_layout = QVBoxLayout(returns_tab)
        returns_layout.setContentsMargins(30, 30, 30, 30)
        returns_layout.setSpacing(16)
        
        # Period selector
        period_layout = QHBoxLayout()
        period_layout.setSpacing(12)
        
        period_label = QLabel("VAT Period:")
        period_label.setFont(RIGELFonts.body(12, True))
        period_layout.addWidget(period_label)
        
        period_combo = QComboBox()
        period_combo.addItems(["January 2024", "February 2024", "March 2024", "April 2024"])
        period_combo.setStyleSheet(f"""
            QComboBox {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "4px";
                padding: "8px" "12px";
                font-family: "Segoe UI";
                font-size: "12px";
                min-width: 200px;
            }}
            QComboBox:focus {{
                border-color: {RIGELColors.BORDER_FOCUS};
            }}
        """)
        period_layout.addWidget(period_combo)
        
        generate_return_btn = QPushButton("Generate Return")
        generate_return_btn.setFont(RIGELFonts.body(11, True))
        generate_return_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        period_layout.addWidget(generate_return_btn)
        
        period_layout.addStretch()
        returns_layout.addLayout(period_layout)
        
        # VAT Calculation Table
        vat_calc_card = ModernCard("VAT Calculation")
        vat_calc_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        vat_table = QTableWidget()
        vat_table.setColumnCount(4)
        vat_table.setHorizontalHeaderLabels(["Description", "Amount (Excl. VAT)", "VAT Amount", "Total (Incl. VAT)"])
        vat_table.horizontalHeader().setStretchLastSection(True)
        vat_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample VAT calculation data
        vat_table.insertRow(0)
        vat_table.setItem(0, 0, QTableWidgetItem("Output VAT (Sales)"))
        vat_table.setItem(0, 1, QTableWidgetItem("R 100,000.00"))
        vat_table.setItem(0, 2, QTableWidgetItem("R 15,000.00"))
        vat_table.setItem(0, 3, QTableWidgetItem("R 115,000.00"))
        
        vat_table.insertRow(1)
        vat_table.setItem(1, 0, QTableWidgetItem("Input VAT (Purchases)"))
        vat_table.setItem(1, 1, QTableWidgetItem("R 60,000.00"))
        vat_table.setItem(1, 2, QTableWidgetItem("R 9,000.00"))
        vat_table.setItem(1, 3, QTableWidgetItem("R 69,000.00"))
        
        vat_table.insertRow(2)
        vat_table.setItem(2, 0, QTableWidgetItem("VAT Payable"))
        vat_table.setItem(2, 1, QTableWidgetItem(""))
        vat_table.setItem(2, 2, QTableWidgetItem("R 6,000.00"))
        vat_table.setItem(2, 3, QTableWidgetItem(""))
        
        # Style VAT payable row
        vat_payable_item = vat_table.item(2, 2)
        if vat_payable_item:
            vat_payable_item.setFont(RIGELFonts.body(11, True))
            vat_payable_item.setForeground(QColor(RIGELColors.PRIMARY_GREEN))
        
        vat_table.setColumnWidth(0, 200)
        vat_table.setColumnWidth(1, 150)
        vat_table.setColumnWidth(2, 120)
        vat_table.setColumnWidth(3, 120)
        
        vat_calc_card.addWidget(vat_table)
        returns_layout.addWidget(vat_calc_card)
        returns_layout.addStretch()
        
        tab_widget.addTab(returns_tab, "VAT Returns")
        
        # VAT Reports Tab
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)
        reports_layout.setContentsMargins(30, 30, 30, 30)
        reports_layout.setSpacing(16)
        
        reports_card = ModernCard("VAT Reports")
        reports_content = QLabel("Generate and manage VAT-related reports including VAT returns, input/output summaries, and compliance reports")
        reports_content.setFont(RIGELFonts.body(12))
        reports_content.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY}; padding: 20px;")
        reports_card.addWidget(reports_content)
        reports_layout.addWidget(reports_card)
        reports_layout.addStretch()
        
        tab_widget.addTab(reports_tab, "Reports")
        
        layout.addWidget(tab_widget)
        
        return widget
    
    def create_reports_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Reports Center")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Report filters
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(12)
        
        date_from_label = QLabel("From:")
        date_from_label.setFont(RIGELFonts.body(12))
        filters_layout.addWidget(date_from_label)
        
        date_from = QDateEdit()
        date_from.setDate(QDate.currentDate().addMonths(-1))
        date_from.setDisplayFormat("yyyy/MM/dd")
        date_from.setStyleSheet(f"""
            QDateEdit {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "4px";
                padding: "8px" "12px";
                font-family: "Segoe UI";
                font-size: "12px";
            }}
            QDateEdit:focus {{
                border-color: {RIGELColors.BORDER_FOCUS};
            }}
        """)
        filters_layout.addWidget(date_from)
        
        date_to_label = QLabel("To:")
        date_to_label.setFont(RIGELFonts.body(12))
        filters_layout.addWidget(date_to_label)
        
        date_to = QDateEdit()
        date_to.setDate(QDate.currentDate())
        date_to.setDisplayFormat("yyyy/MM/dd")
        date_to.setStyleSheet(f"""
            QDateEdit {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "4px";
                padding: "8px" "12px";
                font-family: "Segoe UI";
                font-size: "12px";
            }}
            QDateEdit:focus {{
                border-color: {RIGELColors.BORDER_FOCUS};
            }}
        """)
        filters_layout.addWidget(date_to)
        
        search_btn = QPushButton("Search")
        search_btn.setFont(RIGELFonts.body(11, True))
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        filters_layout.addWidget(search_btn)
        
        filters_layout.addStretch()
        layout.addLayout(filters_layout)
        
        # Reports grid
        reports_grid = QGridLayout()
        reports_grid.setSpacing(20)
        
        # Financial Reports Section
        financial_header = QLabel("FINANCIAL REPORTS")
        financial_header.setFont(RIGELFonts.heading(14, True))
        financial_header.setStyleSheet(f'color: {RIGELColors.PRIMARY_GREEN}; border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN}; padding-bottom: 8px;')
        reports_grid.addWidget(financial_header, 0, 0, 1, 3)
        
        # Financial Report Cards
        income_statement_card = self.create_report_card("📊", "Income Statement", "Generate detailed income statement for selected period", "financial")
        reports_grid.addWidget(income_statement_card, 1, 0)
        
        balance_sheet_card = self.create_report_card("⚖️", "Balance Sheet", "Generate balance sheet with assets and liabilities", "financial")
        reports_grid.addWidget(balance_sheet_card, 1, 1)
        
        cash_flow_card = self.create_report_card("💰", "Cash Flow Statement", "Generate cash flow analysis report", "financial")
        reports_grid.addWidget(cash_flow_card, 1, 2)
        
        trial_balance_card = self.create_report_card("📋", "Trial Balance", "Generate trial balance report", "financial")
        reports_grid.addWidget(trial_balance_card, 2, 0)
        
        general_ledger_card = self.create_report_card("📖", "General Ledger", "Generate detailed general ledger report", "financial")
        reports_grid.addWidget(general_ledger_card, 2, 1)
        
        aged_receivables_card = self.create_report_card("📅", "Aged Receivables", "Generate aged receivables report", "financial")
        reports_grid.addWidget(aged_receivables_card, 2, 2)
        
        # Management Reports Section
        management_header = QLabel("MANAGEMENT REPORTS")
        management_header.setFont(RIGELFonts.heading(14, True))
        management_header.setStyleSheet(f"color: {RIGELColors.INFO}; border-bottom: 2px solid {RIGELColors.INFO}; padding-bottom: 8px;")
        reports_grid.addWidget(management_header, 3, 0, 1, 3)
        
        # Management Report Cards
        sales_report_card = self.create_report_card("💹", "Sales Report", "Generate sales analysis report", "management")
        reports_grid.addWidget(sales_report_card, 4, 0)
        
        customer_analysis_card = self.create_report_card("👥", "Customer Analysis", "Generate customer performance analysis", "management")
        reports_grid.addWidget(customer_analysis_card, 4, 1)
        
        supplier_analysis_card = self.create_report_card("🏪", "Supplier Analysis", "Generate supplier performance analysis", "management")
        reports_grid.addWidget(supplier_analysis_card, 4, 2)
        
        inventory_report_card = self.create_report_card("📦", "Inventory Report", "Generate inventory valuation report", "management")
        reports_grid.addWidget(inventory_report_card, 5, 0)
        
        payroll_report_card = self.create_report_card("💵", "Payroll Report", "Generate payroll summary report", "management")
        reports_grid.addWidget(payroll_report_card, 5, 1)
        
        project_report_card = self.create_report_card("📁", "Project Report", "Generate project status and cost report", "management")
        reports_grid.addWidget(project_report_card, 5, 2)
        
        # Tax Reports Section
        tax_header = QLabel("TAX REPORTS")
        tax_header.setFont(RIGELFonts.heading(14, True))
        tax_header.setStyleSheet(f"color: {RIGELColors.WARNING}; border-bottom: 2px solid {RIGELColors.WARNING}; padding-bottom: 8px;")
        reports_grid.addWidget(tax_header, 6, 0, 1, 3)
        
        # Tax Report Cards
        vat_return_card = self.create_report_card("🧾", "VAT Return", "Generate VAT return report", "tax")
        reports_grid.addWidget(vat_return_card, 7, 0)
        
        tax_summary_card = self.create_report_card("📑", "Tax Summary", "Generate comprehensive tax summary", "tax")
        reports_grid.addWidget(tax_summary_card, 7, 1)
        
        withholding_tax_card = self.create_report_card("📝", "Withholding Tax", "Generate withholding tax report", "tax")
        reports_grid.addWidget(withholding_tax_card, 7, 2)
        
        layout.addLayout(reports_grid)
        layout.addStretch()
        
        return widget
    
    def create_balance_sheet_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Balance Sheet")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Date selector
        date_layout = QHBoxLayout()
        date_layout.setSpacing(12)
        
        date_label = QLabel("As of Date:")
        date_label.setFont(RIGELFonts.body(12, True))
        date_layout.addWidget(date_label)
        
        balance_date = QDateEdit()
        balance_date.setDate(QDate.currentDate())
        balance_date.setDisplayFormat("yyyy/MM/dd")
        balance_date.setStyleSheet(f"""
            QDateEdit {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "4px";
                padding: "8px" "12px";
                font-family: "Segoe UI";
                font-size: "12px";
            }}
            QDateEdit:focus {{
                border-color: {RIGELColors.BORDER_FOCUS};
            }}
        """)
        date_layout.addWidget(balance_date)
        
        generate_btn = QPushButton("Generate")
        generate_btn.setFont(RIGELFonts.body(11, True))
        generate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        date_layout.addWidget(generate_btn)
        
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Balance Sheet content with two columns
        balance_layout = QHBoxLayout()
        balance_layout.setSpacing(20)
        
        # Assets Section
        assets_widget = QWidget()
        assets_layout = QVBoxLayout(assets_widget)
        assets_layout.setSpacing(16)
        
        assets_card = ModernCard("ASSETS")
        assets_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        assets_table = QTableWidget()
        assets_table.setColumnCount(2)
        assets_table.setHorizontalHeaderLabels(["Asset", "Amount"])
        assets_table.horizontalHeader().setStretchLastSection(True)
        assets_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample assets data
        assets_table.insertRow(0)
        assets_table.setItem(0, 0, QTableWidgetItem("Current Assets"))
        assets_table.setItem(0, 1, QTableWidgetItem(""))
        
        assets_table.insertRow(1)
        assets_table.setItem(1, 0, QTableWidgetItem("  Cash and Cash Equivalents"))
        assets_table.setItem(1, 1, QTableWidgetItem("R 125,234.50"))
        
        assets_table.insertRow(2)
        assets_table.setItem(2, 0, QTableWidgetItem("  Accounts Receivable"))
        assets_table.setItem(2, 1, QTableWidgetItem("R 45,678.00"))
        
        assets_table.insertRow(3)
        assets_table.setItem(3, 0, QTableWidgetItem("  Inventory"))
        assets_table.setItem(3, 1, QTableWidgetItem("R 23,456.00"))
        
        assets_table.insertRow(4)
        assets_table.setItem(4, 0, QTableWidgetItem("Total Current Assets"))
        assets_table.setItem(4, 1, QTableWidgetItem("R 194,368.50"))
        
        assets_table.insertRow(5)
        assets_table.setItem(5, 0, QTableWidgetItem("Non-Current Assets"))
        assets_table.setItem(5, 1, QTableWidgetItem(""))
        
        assets_table.insertRow(6)
        assets_table.setItem(6, 0, QTableWidgetItem("  Property, Plant & Equipment"))
        assets_table.setItem(6, 1, QTableWidgetItem("R 1,234,567.00"))
        
        assets_table.insertRow(7)
        assets_table.setItem(7, 0, QTableWidgetItem("TOTAL ASSETS"))
        assets_table.setItem(7, 1, QTableWidgetItem("R 1,428,935.50"))
        
        # Style total row
        total_item = assets_table.item(7, 1)
        if total_item:
            total_item.setFont(RIGELFonts.body(11, True))
            total_item.setForeground(QColor(RIGELColors.PRIMARY_GREEN))
        
        assets_table.setColumnWidth(0, 200)
        assets_table.setColumnWidth(1, 120)
        
        assets_card.addWidget(assets_table)
        assets_layout.addWidget(assets_card)
        balance_layout.addWidget(assets_widget)
        
        # Liabilities & Equity Section
        liabilities_widget = QWidget()
        liabilities_layout = QVBoxLayout(liabilities_widget)
        liabilities_layout.setSpacing(16)
        
        liabilities_card = ModernCard("LIABILITIES & EQUITY")
        liabilities_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        liabilities_table = QTableWidget()
        liabilities_table.setColumnCount(2)
        liabilities_table.setHorizontalHeaderLabels(["Liability/Equity", "Amount"])
        liabilities_table.horizontalHeader().setStretchLastSection(True)
        liabilities_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample liabilities data
        liabilities_table.insertRow(0)
        liabilities_table.setItem(0, 0, QTableWidgetItem("Current Liabilities"))
        liabilities_table.setItem(0, 1, QTableWidgetItem(""))
        
        liabilities_table.insertRow(1)
        liabilities_table.setItem(1, 0, QTableWidgetItem("  Accounts Payable"))
        liabilities_table.setItem(1, 1, QTableWidgetItem("R 23,456.00"))
        
        liabilities_table.insertRow(2)
        liabilities_table.setItem(2, 0, QTableWidgetItem("  Tax Payable"))
        liabilities_table.setItem(2, 1, QTableWidgetItem("R 12,345.00"))
        
        liabilities_table.insertRow(3)
        liabilities_table.setItem(3, 0, QTableWidgetItem("Total Current Liabilities"))
        liabilities_table.setItem(3, 1, QTableWidgetItem("R 35,801.00"))
        
        liabilities_table.insertRow(4)
        liabilities_table.setItem(4, 0, QTableWidgetItem("Non-Current Liabilities"))
        liabilities_table.setItem(4, 1, QTableWidgetItem(""))
        
        liabilities_table.insertRow(5)
        liabilities_table.setItem(5, 0, QTableWidgetItem("  Long-term Debt"))
        liabilities_table.setItem(5, 1, QTableWidgetItem("R 234,567.00"))
        
        liabilities_table.insertRow(6)
        liabilities_table.setItem(6, 0, QTableWidgetItem("Total Liabilities"))
        liabilities_table.setItem(6, 1, QTableWidgetItem("R 270,368.00"))
        
        liabilities_table.insertRow(7)
        liabilities_table.setItem(7, 0, QTableWidgetItem("Shareholder's Equity"))
        liabilities_table.setItem(7, 1, QTableWidgetItem(""))
        
        liabilities_table.insertRow(8)
        liabilities_table.setItem(8, 0, QTableWidgetItem("  Share Capital"))
        liabilities_table.setItem(8, 1, QTableWidgetItem("R 1,000,000.00"))
        
        liabilities_table.insertRow(9)
        liabilities_table.setItem(9, 0, QTableWidgetItem("  Retained Earnings"))
        liabilities_table.setItem(9, 1, QTableWidgetItem("R 158,567.50"))
        
        liabilities_table.insertRow(10)
        liabilities_table.setItem(10, 0, QTableWidgetItem("Total Equity"))
        liabilities_table.setItem(10, 1, QTableWidgetItem("R 1,158,567.50"))
        
        liabilities_table.insertRow(11)
        liabilities_table.setItem(11, 0, QTableWidgetItem("TOTAL LIABILITIES & EQUITY"))
        liabilities_table.setItem(11, 1, QTableWidgetItem("R 1,428,935.50"))
        
        # Style total rows
        total_liabilities_item = liabilities_table.item(6, 1)
        if total_liabilities_item:
            total_liabilities_item.setFont(RIGELFonts.body(11, True))
            total_liabilities_item.setForeground(QColor(RIGELColors.WARNING))
        
        total_equity_item = liabilities_table.item(10, 1)
        if total_equity_item:
            total_equity_item.setFont(RIGELFonts.body(11, True))
            total_equity_item.setForeground(QColor(RIGELColors.INFO))
        
        grand_total_item = liabilities_table.item(11, 1)
        if grand_total_item:
            grand_total_item.setFont(RIGELFonts.body(11, True))
            grand_total_item.setForeground(QColor(RIGELColors.PRIMARY_GREEN))
        
        liabilities_table.setColumnWidth(0, 200)
        liabilities_table.setColumnWidth(1, 120)
        
        liabilities_card.addWidget(liabilities_table)
        liabilities_layout.addWidget(liabilities_card)
        balance_layout.addWidget(liabilities_widget)
        
        layout.addLayout(balance_layout)
        layout.addStretch()
        
        return widget
    
    def create_cash_book_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Cash Book")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Cash Book with tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                background-color: {RIGELColors.BACKGROUND_CARD};
                padding: "0px";
            }}
            QTabWidget::tab-bar {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTabBar::tab {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "24px";
                margin-right: "2px";
                border-top-left-radius: "4px";
                border-top-right-radius: "4px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # Opening Balance Tab
        opening_tab = QWidget()
        opening_layout = QVBoxLayout(opening_tab)
        opening_layout.setContentsMargins(30, 30, 30, 30)
        opening_layout.setSpacing(16)
        
        opening_card = ModernCard("Opening Balance")
        opening_form = QFormLayout()
        opening_form.setSpacing(12)
        
        opening_date = QDateEdit()
        opening_date.setDate(QDate.currentDate())
        opening_date.setDisplayFormat("yyyy/MM/dd")
        opening_form.addRow("Opening Date *:", opening_date)
        
        opening_balance = QDoubleSpinBox()
        opening_balance.setPrefix("R ")
        opening_balance.setMaximum(999999999.99)
        opening_balance.setValue(50000.00)
        opening_form.addRow("Opening Balance *:", opening_balance)
        
        bank_name = QComboBox()
        bank_name.addItems(["Standard Bank", "ABSA", "FNB", "Nedbank", "Capitec"])
        opening_form.addRow("Bank Name *:", bank_name)
        
        account_number = QLineEdit()
        account_number.setPlaceholderText("Enter account number")
        opening_form.addRow("Account Number *:", account_number)
        
        opening_card.addLayout(opening_form)
        opening_layout.addWidget(opening_card)
        opening_layout.addStretch()
        
        tab_widget.addTab(opening_tab, "Opening Balance")
        
        # Transactions Tab
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout(transactions_tab)
        transactions_layout.setContentsMargins(30, 30, 30, 30)
        transactions_layout.setSpacing(16)
        
        # Transaction actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        add_transaction_btn = QPushButton("+ Add Transaction")
        add_transaction_btn.setFont(RIGELFonts.body(11, True))
        add_transaction_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        actions_layout.addWidget(add_transaction_btn)
        
        edit_transaction_btn = QPushButton("Edit Transaction")
        edit_transaction_btn.setFont(RIGELFonts.body(11, True))
        edit_transaction_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        actions_layout.addWidget(edit_transaction_btn)
        
        delete_transaction_btn = QPushButton("Delete Transaction")
        delete_transaction_btn.setFont(RIGELFonts.body(11, True))
        delete_transaction_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.DELETE_ORANGE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.DELETE_ORANGE_HOVER};
            }}
        """)
        actions_layout.addWidget(delete_transaction_btn)
        
        actions_layout.addStretch()
        transactions_layout.addLayout(actions_layout)
        
        # Transactions table
        transactions_card = ModernCard("Cash Transactions")
        transactions_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.cash_transactions_table = QTableWidget()
        self.cash_transactions_table.setColumnCount(6)
        self.cash_transactions_table.setHorizontalHeaderLabels([
            "Date", "Reference", "Description", "Debit", "Credit", "Balance"
        ])
        self.cash_transactions_table.horizontalHeader().setStretchLastSection(True)
        self.cash_transactions_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample data
        self.cash_transactions_table.insertRow(0)
        self.cash_transactions_table.setItem(0, 0, QTableWidgetItem("2024/01/15"))
        self.cash_transactions_table.setItem(0, 1, QTableWidgetItem("CB001"))
        self.cash_transactions_table.setItem(0, 2, QTableWidgetItem("Opening Balance"))
        self.cash_transactions_table.setItem(0, 3, QTableWidgetItem("R 50,000.00"))
        self.cash_transactions_table.setItem(0, 4, QTableWidgetItem(""))
        self.cash_transactions_table.setItem(0, 5, QTableWidgetItem("R 50,000.00"))
        
        self.cash_transactions_table.insertRow(1)
        self.cash_transactions_table.setItem(1, 0, QTableWidgetItem("2024/01/16"))
        self.cash_transactions_table.setItem(1, 1, QTableWidgetItem("CB002"))
        self.cash_transactions_table.setItem(1, 2, QTableWidgetItem("Cash Sale"))
        self.cash_transactions_table.setItem(1, 3, QTableWidgetItem("R 5,000.00"))
        self.cash_transactions_table.setItem(1, 4, QTableWidgetItem(""))
        self.cash_transactions_table.setItem(1, 5, QTableWidgetItem("R 55,000.00"))
        
        self.cash_transactions_table.insertRow(2)
        self.cash_transactions_table.setItem(2, 0, QTableWidgetItem("2024/01/17"))
        self.cash_transactions_table.setItem(2, 1, QTableWidgetItem("CB003"))
        self.cash_transactions_table.setItem(2, 2, QTableWidgetItem("Office Supplies"))
        self.cash_transactions_table.setItem(2, 3, QTableWidgetItem(""))
        self.cash_transactions_table.setItem(2, 4, QTableWidgetItem("R 1,500.00"))
        self.cash_transactions_table.setItem(2, 5, QTableWidgetItem("R 53,500.00"))
        
        # Set column widths
        self.cash_transactions_table.setColumnWidth(0, 100)
        self.cash_transactions_table.setColumnWidth(1, 100)
        self.cash_transactions_table.setColumnWidth(2, 200)
        self.cash_transactions_table.setColumnWidth(3, 120)
        self.cash_transactions_table.setColumnWidth(4, 120)
        self.cash_transactions_table.setColumnWidth(5, 120)
        
        transactions_card.addWidget(self.cash_transactions_table)
        transactions_layout.addWidget(transactions_card)
        transactions_layout.addStretch()
        
        tab_widget.addTab(transactions_tab, "Transactions")
        
        # Bank Reconciliation Tab
        reconciliation_tab = QWidget()
        reconciliation_layout = QVBoxLayout(reconciliation_tab)
        reconciliation_layout.setContentsMargins(30, 30, 30, 30)
        reconciliation_layout.setSpacing(16)
        
        reconciliation_card = ModernCard("Bank Reconciliation")
        reconciliation_form = QFormLayout()
        reconciliation_form.setSpacing(12)
        
        bank_statement_date = QDateEdit()
        bank_statement_date.setDate(QDate.currentDate())
        bank_statement_date.setDisplayFormat("yyyy/MM/dd")
        reconciliation_form.addRow("Bank Statement Date *:", bank_statement_date)
        
        bank_balance = QDoubleSpinBox()
        bank_balance.setPrefix("R ")
        bank_balance.setMaximum(999999999.99)
        bank_balance.setValue(55000.00)
        reconciliation_form.addRow("Bank Statement Balance *:", bank_balance)
        
        book_balance = QDoubleSpinBox()
        book_balance.setPrefix("R ")
        book_balance.setMaximum(999999999.99)
        book_balance.setValue(53500.00)
        reconciliation_form.addRow("Book Balance *:", book_balance)
        
        difference = QDoubleSpinBox()
        difference.setPrefix("R ")
        difference.setMaximum(999999999.99)
        difference.setValue(1500.00)
        difference.setStyleSheet(f"""
            QDoubleSpinBox {{
                color: {RIGELColors.WARNING};
                font-weight: bold;
            }}
        """)
        reconciliation_form.addRow("Difference *:", difference)
        
        reconcile_btn = QPushButton("Reconcile")
        reconcile_btn.setFont(RIGELFonts.body(11, True))
        reconcile_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "12px" "32px";
                font-family: "Segoe UI";
                font-weight: 600;
                min-width: "140px";
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        reconciliation_form.addRow("", reconcile_btn)
        
        reconciliation_card.addLayout(reconciliation_form)
        reconciliation_layout.addWidget(reconciliation_card)
        reconciliation_layout.addStretch()
        
        tab_widget.addTab(reconciliation_tab, "Bank Reconciliation")
        
        layout.addWidget(tab_widget)
        
        return widget
    
    def create_customers_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Customers")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Customers with tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                background-color: {RIGELColors.BACKGROUND_CARD};
                padding: "0px";
            }}
            QTabWidget::tab-bar {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTabBar::tab {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "24px";
                margin-right: "2px";
                border-top-left-radius: "4px";
                border-top-right-radius: "4px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # Customers Tab
        customers_tab = QWidget()
        customers_layout = QVBoxLayout(customers_tab)
        customers_layout.setContentsMargins(30, 30, 30, 30)
        customers_layout.setSpacing(16)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        add_customer_btn = QPushButton("+ Add Customer")
        add_customer_btn.setFont(RIGELFonts.body(11, True))
        add_customer_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        add_customer_btn.clicked.connect(self.add_customer)
        actions_layout.addWidget(add_customer_btn)
        
        edit_customer_btn = QPushButton("Edit Customer")
        edit_customer_btn.setFont(RIGELFonts.body(11, True))
        edit_customer_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        edit_customer_btn.clicked.connect(self.edit_customer)
        actions_layout.addWidget(edit_customer_btn)
        
        delete_customer_btn = QPushButton("Delete Customer")
        delete_customer_btn.setFont(RIGELFonts.body(11, True))
        delete_customer_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.DELETE_ORANGE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.DELETE_ORANGE_HOVER};
            }}
        """)
        delete_customer_btn.clicked.connect(self.delete_customer)
        actions_layout.addWidget(delete_customer_btn)
        
        actions_layout.addStretch()
        customers_layout.addLayout(actions_layout)
        
        # Customers table
        customers_card = ModernCard("Customer List")
        customers_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(6)
        self.customers_table.setHorizontalHeaderLabels([
            "Customer Code", "Name", "Contact", "Email", "Phone", "Actions"
        ])
        self.customers_table.horizontalHeader().setStretchLastSection(True)
        self.customers_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Load customers from database
        self.load_customers_data()
        
        # Set column widths
        self.customers_table.setColumnWidth(0, 100)
        self.customers_table.setColumnWidth(1, 150)
        self.customers_table.setColumnWidth(2, 120)
        self.customers_table.setColumnWidth(3, 180)
        self.customers_table.setColumnWidth(4, 120)
        self.customers_table.setColumnWidth(5, 100)
        
        customers_card.addWidget(self.customers_table)
        customers_layout.addWidget(customers_card)
        customers_layout.addStretch()
        
        tab_widget.addTab(customers_tab, "Customers")
        
        # Invoices Tab
        invoices_tab = QWidget()
        invoices_layout = QVBoxLayout(invoices_tab)
        invoices_layout.setContentsMargins(30, 30, 30, 30)
        invoices_layout.setSpacing(16)
        
        invoices_card = ModernCard("Customer Invoices")
        invoices_content = QLabel("Invoice Management - Create, view, and manage customer invoices with due dates and amounts")
        invoices_content.setFont(RIGELFonts.body(12))
        invoices_content.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY}; padding: 20px;")
        invoices_card.addWidget(invoices_content)
        invoices_layout.addWidget(invoices_card)
        invoices_layout.addStretch()
        
        tab_widget.addTab(invoices_tab, "Invoices")
        
        # Account Payments Tab
        payments_tab = QWidget()
        payments_layout = QVBoxLayout(payments_tab)
        payments_layout.setContentsMargins(30, 30, 30, 30)
        payments_layout.setSpacing(16)
        
        payments_card = ModernCard("Account Payments")
        payments_content = QLabel("Payment Processing - Record and track customer payments, apply to invoices")
        payments_content.setFont(RIGELFonts.body(12))
        payments_content.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY}; padding: 20px;")
        payments_card.addWidget(payments_content)
        payments_layout.addWidget(payments_card)
        payments_layout.addStretch()
        
        tab_widget.addTab(payments_tab, "Account Payments")
        
        # Statements Tab
        statements_tab = QWidget()
        statements_layout = QVBoxLayout(statements_tab)
        statements_layout.setContentsMargins(30, 30, 30, 30)
        statements_layout.setSpacing(16)
        
        statements_card = ModernCard("Customer Statements")
        statements_content = QLabel("Statement Generation - Generate monthly statements for customers with transaction history")
        statements_content.setFont(RIGELFonts.body(12))
        statements_content.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY}; padding: 20px;")
        statements_card.addWidget(statements_content)
        statements_layout.addWidget(statements_card)
        statements_layout.addStretch()
        
        tab_widget.addTab(statements_tab, "Statements")
        
        layout.addWidget(tab_widget)
        
        return widget
    
    def create_suppliers_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Suppliers")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        add_supplier_btn = QPushButton("+ Add Supplier")
        add_supplier_btn.setFont(RIGELFonts.body(11, True))
        add_supplier_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        actions_layout.addWidget(add_supplier_btn)
        
        edit_supplier_btn = QPushButton("Edit Supplier")
        edit_supplier_btn.setFont(RIGELFonts.body(11, True))
        edit_supplier_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        actions_layout.addWidget(edit_supplier_btn)
        
        delete_supplier_btn = QPushButton("Delete Supplier")
        delete_supplier_btn.setFont(RIGELFonts.body(11, True))
        delete_supplier_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.DELETE_ORANGE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.DELETE_ORANGE_HOVER};
            }}
        """)
        actions_layout.addWidget(delete_supplier_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Suppliers table
        suppliers_card = ModernCard("Supplier List")
        suppliers_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(7)
        self.suppliers_table.setHorizontalHeaderLabels([
            "Supplier Code", "Name", "Contact Person", "Email", "Phone", "Balance", "Actions"
        ])
        self.suppliers_table.horizontalHeader().setStretchLastSection(True)
        self.suppliers_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample data
        self.suppliers_table.insertRow(0)
        self.suppliers_table.setItem(0, 0, QTableWidgetItem("S001"))
        self.suppliers_table.setItem(0, 1, QTableWidgetItem("Office Supplies Ltd"))
        self.suppliers_table.setItem(0, 2, QTableWidgetItem("John Smith"))
        self.suppliers_table.setItem(0, 3, QTableWidgetItem("john@officesupplies.co.za"))
        self.suppliers_table.setItem(0, 4, QTableWidgetItem("011 555 1234"))
        self.suppliers_table.setItem(0, 5, QTableWidgetItem("R 5,234.00"))
        self.suppliers_table.setItem(0, 6, QTableWidgetItem(""))
        
        self.suppliers_table.insertRow(1)
        self.suppliers_table.setItem(1, 0, QTableWidgetItem("S002"))
        self.suppliers_table.setItem(1, 1, QTableWidgetItem("Tech Solutions"))
        self.suppliers_table.setItem(1, 2, QTableWidgetItem("Sarah Johnson"))
        self.suppliers_table.setItem(1, 3, QTableWidgetItem("sarah@techsolutions.co.za"))
        self.suppliers_table.setItem(1, 4, QTableWidgetItem("012 345 6789"))
        self.suppliers_table.setItem(1, 5, QTableWidgetItem("R 12,456.00"))
        self.suppliers_table.setItem(1, 6, QTableWidgetItem(""))
        
        self.suppliers_table.insertRow(2)
        self.suppliers_table.setItem(2, 0, QTableWidgetItem("S003"))
        self.suppliers_table.setItem(2, 1, QTableWidgetItem("Building Materials Co"))
        self.suppliers_table.setItem(2, 2, QTableWidgetItem("Mike Wilson"))
        self.suppliers_table.setItem(2, 3, QTableWidgetItem("mike@building.co.za"))
        self.suppliers_table.setItem(2, 4, QTableWidgetItem("013 678 9012"))
        self.suppliers_table.setItem(2, 5, QTableWidgetItem("R 8,901.00"))
        self.suppliers_table.setItem(2, 6, QTableWidgetItem(""))
        
        # Set column widths
        self.suppliers_table.setColumnWidth(0, 100)
        self.suppliers_table.setColumnWidth(1, 150)
        self.suppliers_table.setColumnWidth(2, 120)
        self.suppliers_table.setColumnWidth(3, 180)
        self.suppliers_table.setColumnWidth(4, 120)
        self.suppliers_table.setColumnWidth(5, 100)
        self.suppliers_table.setColumnWidth(6, 100)
        
        suppliers_card.addWidget(self.suppliers_table)
        layout.addWidget(suppliers_card)
        
        # Summary Section
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)
        
        total_suppliers_card = ModernCard("Total Suppliers")
        total_suppliers_label = QLabel("3")
        total_suppliers_label.setFont(RIGELFonts.heading(16, True))
        total_suppliers_label.setStyleSheet(f"color: {RIGELColors.INFO};")
        total_suppliers_card.addWidget(total_suppliers_label)
        summary_layout.addWidget(total_suppliers_card)
        
        total_balance_card = ModernCard("Total Balance")
        total_balance_label = QLabel("R 26,591.00")
        total_balance_label.setFont(RIGELFonts.heading(16, True))
        total_balance_label.setStyleSheet(f"color: {RIGELColors.WARNING};")
        total_balance_card.addWidget(total_balance_label)
        summary_layout.addWidget(total_balance_card)
        
        active_suppliers_card = ModernCard("Active Suppliers")
        active_suppliers_label = QLabel("3")
        active_suppliers_label.setFont(RIGELFonts.heading(16, True))
        active_suppliers_label.setStyleSheet(f"color: {RIGELColors.SUCCESS};")
        active_suppliers_card.addWidget(active_suppliers_label)
        summary_layout.addWidget(active_suppliers_card)
        
        layout.addLayout(summary_layout)
        layout.addStretch()
        
        return widget
    
    def create_employees_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Employees")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Employee Management with tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                background-color: {RIGELColors.BACKGROUND_CARD};
                padding: "0px";
            }}
            QTabWidget::tab-bar {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTabBar::tab {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "24px";
                margin-right: "2px";
                border-top-left-radius: "4px";
                border-top-right-radius: "4px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # Employee List Tab
        employees_tab = QWidget()
        employees_layout = QVBoxLayout(employees_tab)
        employees_layout.setContentsMargins(30, 30, 30, 30)
        employees_layout.setSpacing(16)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        add_employee_btn = QPushButton("+ Add Employee")
        add_employee_btn.setFont(RIGELFonts.body(11, True))
        add_employee_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        actions_layout.addWidget(add_employee_btn)
        
        edit_employee_btn = QPushButton("Edit Employee")
        edit_employee_btn.setFont(RIGELFonts.body(11, True))
        edit_employee_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        actions_layout.addWidget(edit_employee_btn)
        
        terminate_employee_btn = QPushButton("Terminate Employee")
        terminate_employee_btn.setFont(RIGELFonts.body(11, True))
        terminate_employee_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.DELETE_ORANGE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.DELETE_ORANGE_HOVER};
            }}
        """)
        actions_layout.addWidget(terminate_employee_btn)
        
        actions_layout.addStretch()
        employees_layout.addLayout(actions_layout)
        
        # Employees table
        employees_card = ModernCard("Employee List")
        employees_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(8)
        self.employees_table.setHorizontalHeaderLabels([
            "Employee ID", "Name", "Department", "Position", "Email", "Phone", "Salary", "Actions"
        ])
        self.employees_table.horizontalHeader().setStretchLastSection(True)
        self.employees_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample data
        self.employees_table.insertRow(0)
        self.employees_table.setItem(0, 0, QTableWidgetItem("E001"))
        self.employees_table.setItem(0, 1, QTableWidgetItem("John Smith"))
        self.employees_table.setItem(0, 2, QTableWidgetItem("Management"))
        self.employees_table.setItem(0, 3, QTableWidgetItem("CEO"))
        self.employees_table.setItem(0, 4, QTableWidgetItem("john.smith@company.com"))
        self.employees_table.setItem(0, 5, QTableWidgetItem("011 555 0001"))
        self.employees_table.setItem(0, 6, QTableWidgetItem("R 85,000.00"))
        self.employees_table.setItem(0, 7, QTableWidgetItem(""))
        
        self.employees_table.insertRow(1)
        self.employees_table.setItem(1, 0, QTableWidgetItem("E002"))
        self.employees_table.setItem(1, 1, QTableWidgetItem("Sarah Johnson"))
        self.employees_table.setItem(1, 2, QTableWidgetItem("Finance"))
        self.employees_table.setItem(1, 3, QTableWidgetItem("Financial Manager"))
        self.employees_table.setItem(1, 4, QTableWidgetItem("sarah.j@company.com"))
        self.employees_table.setItem(1, 5, QTableWidgetItem("011 555 0002"))
        self.employees_table.setItem(1, 6, QTableWidgetItem("R 45,000.00"))
        self.employees_table.setItem(1, 7, QTableWidgetItem(""))
        
        self.employees_table.insertRow(2)
        self.employees_table.setItem(2, 0, QTableWidgetItem("E003"))
        self.employees_table.setItem(2, 1, QTableWidgetItem("Mike Wilson"))
        self.employees_table.setItem(2, 2, QTableWidgetItem("IT"))
        self.employees_table.setItem(2, 3, QTableWidgetItem("IT Manager"))
        self.employees_table.setItem(2, 4, QTableWidgetItem("mike.w@company.com"))
        self.employees_table.setItem(2, 5, QTableWidgetItem("011 555 0003"))
        self.employees_table.setItem(2, 6, QTableWidgetItem("R 35,000.00"))
        self.employees_table.setItem(2, 7, QTableWidgetItem(""))
        
        # Set column widths
        self.employees_table.setColumnWidth(0, 80)
        self.employees_table.setColumnWidth(1, 120)
        self.employees_table.setColumnWidth(2, 100)
        self.employees_table.setColumnWidth(3, 120)
        self.employees_table.setColumnWidth(4, 150)
        self.employees_table.setColumnWidth(5, 100)
        self.employees_table.setColumnWidth(6, 100)
        self.employees_table.setColumnWidth(7, 80)
        
        employees_card.addWidget(self.employees_table)
        employees_layout.addWidget(employees_card)
        employees_layout.addStretch()
        
        tab_widget.addTab(employees_tab, "Employee List")
        
        # Payroll Configuration Tab
        payroll_config_tab = QWidget()
        payroll_config_layout = QVBoxLayout(payroll_config_tab)
        payroll_config_layout.setContentsMargins(30, 30, 30, 30)
        payroll_config_layout.setSpacing(16)
        
        payroll_card = ModernCard("Payroll Configuration")
        payroll_form = QFormLayout()
        payroll_form.setSpacing(12)
        
        pay_frequency = QComboBox()
        pay_frequency.addItems(["Monthly", "Bi-Weekly", "Weekly"])
        payroll_form.addRow("Pay Frequency *:", pay_frequency)
        
        pay_day = QSpinBox()
        pay_day.setRange(1, 31)
        pay_day.setValue(25)
        payroll_form.addRow("Pay Day *:", pay_day)
        
        tax_method = QComboBox()
        tax_method.addItems(["PAYE", "Provisional Tax", "No Tax"])
        payroll_form.addRow("Tax Method *:", tax_method)
        
        uif_number = QLineEdit()
        uif_number.setPlaceholderText("Enter UIF number")
        payroll_form.addRow("UIF Number *:", uif_number)
        
        sdl_number = QLineEdit()
        sdl_number.setPlaceholderText("Enter SDL number")
        payroll_form.addRow("SDL Number *:", sdl_number)
        
        payroll_card.addLayout(payroll_form)
        payroll_config_layout.addWidget(payroll_card)
        payroll_config_layout.addStretch()
        
        tab_widget.addTab(payroll_config_tab, "Payroll Configuration")
        
        layout.addWidget(tab_widget)
        
        return widget
    
    def create_payroll_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Payroll Processing")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Payroll period selector
        period_layout = QHBoxLayout()
        period_layout.setSpacing(12)
        
        period_label = QLabel("Payroll Period:")
        period_label.setFont(RIGELFonts.body(12, True))
        period_layout.addWidget(period_label)
        
        month_combo = QComboBox()
        month_combo.addItems(["January 2024", "February 2024", "March 2024", "April 2024"])
        month_combo.setStyleSheet(f"""
            QComboBox {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "4px";
                padding: "8px" "12px";
                font-family: "Segoe UI";
                font-size: "12px";
                min-width: "150px";
            }}
            QComboBox:focus {{
                border-color: {RIGELColors.BORDER_FOCUS};
            }}
        """)
        period_layout.addWidget(month_combo)
        
        process_payroll_btn = QPushButton("Process Payroll")
        process_payroll_btn.setFont(RIGELFonts.body(11, True))
        process_payroll_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        period_layout.addWidget(process_payroll_btn)
        
        export_payslips_btn = QPushButton("Export Payslips")
        export_payslips_btn.setFont(RIGELFonts.body(11, True))
        export_payslips_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        period_layout.addWidget(export_payslips_btn)
        
        period_layout.addStretch()
        layout.addLayout(period_layout)
        
        # Payroll Summary Cards
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)
        
        total_salary_card = ModernCard("Total Gross Salary")
        total_salary_label = QLabel("R 165,000.00")
        total_salary_label.setFont(RIGELFonts.heading(16, True))
        total_salary_label.setStyleSheet(f"color: {RIGELColors.NEUTRAL};")
        total_salary_card.addWidget(total_salary_label)
        summary_layout.addWidget(total_salary_card)
        
        total_deductions_card = ModernCard("Total Deductions")
        total_deductions_label = QLabel("R 35,000.00")
        total_deductions_label.setFont(RIGELFonts.heading(16, True))
        total_deductions_label.setStyleSheet(f"color: {RIGELColors.WARNING};")
        total_deductions_card.addWidget(total_deductions_label)
        summary_layout.addWidget(total_deductions_card)
        
        net_salary_card = ModernCard("Total Net Salary")
        net_salary_label = QLabel("R 130,000.00")
        net_salary_label.setFont(RIGELFonts.heading(16, True))
        net_salary_label.setStyleSheet(f"color: {RIGELColors.SUCCESS};")
        net_salary_card.addWidget(net_salary_label)
        summary_layout.addWidget(net_salary_card)
        
        layout.addLayout(summary_layout)
        
        # Payroll Details Table
        payroll_card = ModernCard("Payroll Details")
        payroll_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.payroll_table = QTableWidget()
        self.payroll_table.setColumnCount(8)
        self.payroll_table.setHorizontalHeaderLabels([
            "Employee ID", "Name", "Gross Salary", "PAYE", "UIF", "SDL", "Net Salary", "Status"
        ])
        self.payroll_table.horizontalHeader().setStretchLastSection(True)
        self.payroll_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample data
        self.payroll_table.insertRow(0)
        self.payroll_table.setItem(0, 0, QTableWidgetItem("E001"))
        self.payroll_table.setItem(0, 1, QTableWidgetItem("John Smith"))
        self.payroll_table.setItem(0, 2, QTableWidgetItem("R 85,000.00"))
        self.payroll_table.setItem(0, 3, QTableWidgetItem("R 17,000.00"))
        self.payroll_table.setItem(0, 4, QTableWidgetItem("R 850.00"))
        self.payroll_table.setItem(0, 5, QTableWidgetItem("R 1,275.00"))
        self.payroll_table.setItem(0, 6, QTableWidgetItem("R 65,875.00"))
        self.payroll_table.setItem(0, 7, QTableWidgetItem("Processed"))
        
        self.payroll_table.insertRow(1)
        self.payroll_table.setItem(1, 0, QTableWidgetItem("E002"))
        self.payroll_table.setItem(1, 1, QTableWidgetItem("Sarah Johnson"))
        self.payroll_table.setItem(1, 2, QTableWidgetItem("R 45,000.00"))
        self.payroll_table.setItem(1, 3, QTableWidgetItem("R 9,000.00"))
        self.payroll_table.setItem(1, 4, QTableWidgetItem("R 450.00"))
        self.payroll_table.setItem(1, 5, QTableWidgetItem("R 675.00"))
        self.payroll_table.setItem(1, 6, QTableWidgetItem("R 34,875.00"))
        self.payroll_table.setItem(1, 7, QTableWidgetItem("Processed"))
        
        self.payroll_table.insertRow(2)
        self.payroll_table.setItem(2, 0, QTableWidgetItem("E003"))
        self.payroll_table.setItem(2, 1, QTableWidgetItem("Mike Wilson"))
        self.payroll_table.setItem(2, 2, QTableWidgetItem("R 35,000.00"))
        self.payroll_table.setItem(2, 3, QTableWidgetItem("R 7,000.00"))
        self.payroll_table.setItem(2, 4, QTableWidgetItem("R 350.00"))
        self.payroll_table.setItem(2, 5, QTableWidgetItem("R 525.00"))
        self.payroll_table.setItem(2, 6, QTableWidgetItem("R 27,125.00"))
        self.payroll_table.setItem(2, 7, QTableWidgetItem("Processed"))
        
        # Set column widths
        self.payroll_table.setColumnWidth(0, 80)
        self.payroll_table.setColumnWidth(1, 120)
        self.payroll_table.setColumnWidth(2, 100)
        self.payroll_table.setColumnWidth(3, 80)
        self.payroll_table.setColumnWidth(4, 80)
        self.payroll_table.setColumnWidth(5, 80)
        self.payroll_table.setColumnWidth(6, 100)
        self.payroll_table.setColumnWidth(7, 80)
        
        payroll_card.addWidget(self.payroll_table)
        layout.addWidget(payroll_card)
        layout.addStretch()
        
        return widget
    
    def create_payslips_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        
        title = QLabel("Payslips")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        content = QLabel("Payslips Generation - To be implemented with exact layout")
        content.setFont(RIGELFonts.body(12))
        layout.addWidget(content)
        layout.addStretch()
        
        return widget
    
    def create_inventory_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Inventory Management")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Inventory Management with tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                background-color: {RIGELColors.BACKGROUND_CARD};
                padding: "0px";
            }}
            QTabWidget::tab-bar {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTabBar::tab {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "24px";
                margin-right: "2px";
                border-top-left-radius: "4px";
                border-top-right-radius: "4px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # Stock Items Tab
        stock_tab = QWidget()
        stock_layout = QVBoxLayout(stock_tab)
        stock_layout.setContentsMargins(30, 30, 30, 30)
        stock_layout.setSpacing(16)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        add_item_btn = QPushButton("+ Add Item")
        add_item_btn.setFont(RIGELFonts.body(11, True))
        add_item_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        actions_layout.addWidget(add_item_btn)
        
        edit_item_btn = QPushButton("Edit Item")
        edit_item_btn.setFont(RIGELFonts.body(11, True))
        edit_item_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        actions_layout.addWidget(edit_item_btn)
        
        # Inventory table
        inventory_card = ModernCard("Stock Items")
        inventory_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(9)
        self.inventory_table.setHorizontalHeaderLabels([
            "Item Code", "Description", "Category", "Quantity", "Unit Price", "Total Value", "Min Level", "Status", "Actions"
        ])
        self.inventory_table.horizontalHeader().setStretchLastSection(True)
        self.inventory_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample data
        self.inventory_table.insertRow(0)
        self.inventory_table.setItem(0, 0, QTableWidgetItem("INV001"))
        self.inventory_table.setItem(0, 1, QTableWidgetItem("Office Laptop"))
        self.inventory_table.setItem(0, 2, QTableWidgetItem("Electronics"))
        self.inventory_table.setItem(0, 3, QTableWidgetItem("25"))
        self.inventory_table.setItem(0, 4, QTableWidgetItem("R 8,500.00"))
        self.inventory_table.setItem(0, 5, QTableWidgetItem("R 212,500.00"))
        self.inventory_table.setItem(0, 6, QTableWidgetItem("5"))
        self.inventory_table.setItem(0, 7, QTableWidgetItem("In Stock"))
        self.inventory_table.setItem(0, 8, QTableWidgetItem(""))
        
        self.inventory_table.insertRow(1)
        self.inventory_table.setItem(1, 0, QTableWidgetItem("INV002"))
        self.inventory_table.setItem(1, 1, QTableWidgetItem("Office Chair"))
        self.inventory_table.setItem(1, 2, QTableWidgetItem("Furniture"))
        self.inventory_table.setItem(1, 3, QTableWidgetItem("50"))
        self.inventory_table.setItem(1, 4, QTableWidgetItem("R 1,200.00"))
        self.inventory_table.setItem(1, 5, QTableWidgetItem("R 60,000.00"))
        self.inventory_table.setItem(1, 6, QTableWidgetItem("10"))
        self.inventory_table.setItem(1, 7, QTableWidgetItem("In Stock"))
        self.inventory_table.setItem(1, 8, QTableWidgetItem(""))
        
        self.inventory_table.insertRow(2)
        self.inventory_table.setItem(2, 0, QTableWidgetItem("INV003"))
        self.inventory_table.setItem(2, 1, QTableWidgetItem("Printer Paper"))
        self.inventory_table.setItem(2, 2, QTableWidgetItem("Stationery"))
        self.inventory_table.setItem(2, 3, QTableWidgetItem("100"))
        self.inventory_table.setItem(2, 4, QTableWidgetItem("R 45.00"))
        self.inventory_table.setItem(2, 5, QTableWidgetItem("R 4,500.00"))
        self.inventory_table.setItem(2, 6, QTableWidgetItem("20"))
        self.inventory_table.setItem(2, 7, QTableWidgetItem("Low Stock"))
        self.inventory_table.setItem(2, 8, QTableWidgetItem(""))
        
        # Set column widths
        self.inventory_table.setColumnWidth(0, 80)
        self.inventory_table.setColumnWidth(1, 150)
        self.inventory_table.setColumnWidth(2, 100)
        self.inventory_table.setColumnWidth(3, 80)
        self.inventory_table.setColumnWidth(4, 100)
        self.inventory_table.setColumnWidth(5, 100)
        self.inventory_table.setColumnWidth(6, 100)
        self.inventory_table.setColumnWidth(7, 80)
        self.inventory_table.setColumnWidth(8, 80)
        
        inventory_card.addWidget(self.inventory_table)
        stock_layout.addWidget(inventory_card)
        stock_layout.addStretch()
        
        tab_widget.addTab(stock_tab, "Stock Items")
        
        # Stock Movements Tab
        movements_tab = QWidget()
        movements_layout = QVBoxLayout(movements_tab)
        movements_layout.setContentsMargins(30, 30, 30, 30)
        movements_layout.setSpacing(16)
        
        movements_card = ModernCard("Stock Movements")
        movements_content = QLabel("Track all stock movements including receipts, issues, and adjustments with date ranges and item filtering")
        movements_content.setFont(RIGELFonts.body(12))
        movements_content.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY}; padding: 20px;")
        movements_card.addWidget(movements_content)
        movements_layout.addWidget(movements_card)
        movements_layout.addStretch()
        
        tab_widget.addTab(movements_tab, "Stock Movements")
        
        layout.addWidget(tab_widget)
        
        return widget
    
    def create_fixed_assets_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Fixed Assets Management")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Fixed Assets with tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                background-color: {RIGELColors.BACKGROUND_CARD};
                padding: "0px";
            }}
            QTabWidget::tab-bar {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTabBar::tab {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "24px";
                margin-right: "2px";
                border-top-left-radius: "4px";
                border-top-right-radius: "4px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # Asset Register Tab
        assets_tab = QWidget()
        assets_layout = QVBoxLayout(assets_tab)
        assets_layout.setContentsMargins(30, 30, 30, 30)
        assets_layout.setSpacing(16)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        add_asset_btn = QPushButton("+ Add Asset")
        add_asset_btn.setFont(RIGELFonts.body(11, True))
        add_asset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        actions_layout.addWidget(add_asset_btn)
        
        edit_asset_btn = QPushButton("Edit Asset")
        edit_asset_btn.setFont(RIGELFonts.body(11, True))
        edit_asset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        actions_layout.addWidget(edit_asset_btn)
        
        dispose_asset_btn = QPushButton("Dispose Asset")
        dispose_asset_btn.setFont(RIGELFonts.body(11, True))
        dispose_asset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.DELETE_ORANGE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.DELETE_ORANGE_HOVER};
            }}
        """)
        actions_layout.addWidget(dispose_asset_btn)
        
        actions_layout.addStretch()
        assets_layout.addLayout(actions_layout)
        
        # Assets table
        assets_card = ModernCard("Asset Register")
        assets_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.fixed_assets_table = QTableWidget()
        self.fixed_assets_table.setColumnCount(9)
        self.fixed_assets_table.setHorizontalHeaderLabels([
            "Asset ID", "Description", "Category", "Purchase Date", "Cost", "Depreciation", "NBV", "Status", "Actions"
        ])
        self.fixed_assets_table.horizontalHeader().setStretchLastSection(True)
        self.fixed_assets_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample data
        self.fixed_assets_table.insertRow(0)
        self.fixed_assets_table.setItem(0, 0, QTableWidgetItem("FA001"))
        self.fixed_assets_table.setItem(0, 1, QTableWidgetItem("Office Building"))
        self.fixed_assets_table.setItem(0, 2, QTableWidgetItem("Property"))
        self.fixed_assets_table.setItem(0, 3, QTableWidgetItem("2020/01/15"))
        self.fixed_assets_table.setItem(0, 4, QTableWidgetItem("R 2,500,000.00"))
        self.fixed_assets_table.setItem(0, 5, QTableWidgetItem("R 250,000.00"))
        self.fixed_assets_table.setItem(0, 6, QTableWidgetItem("R 2,250,000.00"))
        self.fixed_assets_table.setItem(0, 7, QTableWidgetItem("Active"))
        self.fixed_assets_table.setItem(0, 8, QTableWidgetItem(""))
        
        self.fixed_assets_table.insertRow(1)
        self.fixed_assets_table.setItem(1, 0, QTableWidgetItem("FA002"))
        self.fixed_assets_table.setItem(1, 1, QTableWidgetItem("Company Vehicles"))
        self.fixed_assets_table.setItem(1, 2, QTableWidgetItem("Vehicles"))
        self.fixed_assets_table.setItem(1, 3, QTableWidgetItem("2021/03/10"))
        self.fixed_assets_table.setItem(1, 4, QTableWidgetItem("R 850,000.00"))
        self.fixed_assets_table.setItem(1, 5, QTableWidgetItem("R 170,000.00"))
        self.fixed_assets_table.setItem(1, 6, QTableWidgetItem("R 680,000.00"))
        self.fixed_assets_table.setItem(1, 7, QTableWidgetItem("Active"))
        self.fixed_assets_table.setItem(1, 8, QTableWidgetItem(""))
        
        self.fixed_assets_table.insertRow(2)
        self.fixed_assets_table.setItem(2, 0, QTableWidgetItem("FA003"))
        self.fixed_assets_table.setItem(2, 1, QTableWidgetItem("Office Equipment"))
        self.fixed_assets_table.setItem(2, 2, QTableWidgetItem("Equipment"))
        self.fixed_assets_table.setItem(2, 3, QTableWidgetItem("2022/06/20"))
        self.fixed_assets_table.setItem(2, 4, QTableWidgetItem("R 450,000.00"))
        self.fixed_assets_table.setItem(2, 5, QTableWidgetItem("R 45,000.00"))
        self.fixed_assets_table.setItem(2, 6, QTableWidgetItem("R 405,000.00"))
        self.fixed_assets_table.setItem(2, 7, QTableWidgetItem("Active"))
        self.fixed_assets_table.setItem(2, 8, QTableWidgetItem(""))
        
        # Set column widths
        self.fixed_assets_table.setColumnWidth(0, 80)
        self.fixed_assets_table.setColumnWidth(1, 150)
        self.fixed_assets_table.setColumnWidth(2, 100)
        self.fixed_assets_table.setColumnWidth(3, 100)
        self.fixed_assets_table.setColumnWidth(4, 100)
        self.fixed_assets_table.setColumnWidth(5, 100)
        self.fixed_assets_table.setColumnWidth(6, 100)
        self.fixed_assets_table.setColumnWidth(7, 80)
        self.fixed_assets_table.setColumnWidth(8, 80)
        
        assets_card.addWidget(self.fixed_assets_table)
        assets_layout.addWidget(assets_card)
        assets_layout.addStretch()
        
        tab_widget.addTab(assets_tab, "Asset Register")
        
        # Depreciation Schedule Tab
        depreciation_tab = QWidget()
        depreciation_layout = QVBoxLayout(depreciation_tab)
        depreciation_layout.setContentsMargins(30, 30, 30, 30)
        depreciation_layout.setSpacing(16)
        
        depreciation_card = ModernCard("Depreciation Schedule")
        depreciation_content = QLabel("Annual depreciation schedule showing asset values, accumulated depreciation, and net book values")
        depreciation_content.setFont(RIGELFonts.body(12))
        depreciation_content.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY}; padding: 20px;")
        depreciation_card.addWidget(depreciation_content)
        depreciation_layout.addWidget(depreciation_card)
        depreciation_layout.addStretch()
        
        tab_widget.addTab(depreciation_tab, "Depreciation")
        
        layout.addWidget(tab_widget)
        
        return widget
    
    def create_directors_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Directors Management")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        add_director_btn = QPushButton("+ Add Director")
        add_director_btn.setFont(RIGELFonts.body(11, True))
        add_director_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        actions_layout.addWidget(add_director_btn)
        
        edit_director_btn = QPushButton("Edit Director")
        edit_director_btn.setFont(RIGELFonts.body(11, True))
        edit_director_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        actions_layout.addWidget(edit_director_btn)
        
        remove_director_btn = QPushButton("Remove Director")
        remove_director_btn.setFont(RIGELFonts.body(11, True))
        remove_director_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.DELETE_ORANGE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.DELETE_ORANGE_HOVER};
            }}
        """)
        actions_layout.addWidget(remove_director_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Directors table
        directors_card = ModernCard("Directors List")
        directors_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.directors_table = QTableWidget()
        self.directors_table.setColumnCount(8)
        self.directors_table.setHorizontalHeaderLabels([
            "Director ID", "Name", "Position", "Email", "Phone", "Shareholding", "Status", "Actions"
        ])
        self.directors_table.horizontalHeader().setStretchLastSection(True)
        self.directors_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample data
        self.directors_table.insertRow(0)
        self.directors_table.setItem(0, 0, QTableWidgetItem("D001"))
        self.directors_table.setItem(0, 1, QTableWidgetItem("John Smith"))
        self.directors_table.setItem(0, 2, QTableWidgetItem("Managing Director"))
        self.directors_table.setItem(0, 3, QTableWidgetItem("john.smith@company.com"))
        self.directors_table.setItem(0, 4, QTableWidgetItem("011 555 0001"))
        self.directors_table.setItem(0, 5, QTableWidgetItem("40%"))
        self.directors_table.setItem(0, 6, QTableWidgetItem("Active"))
        self.directors_table.setItem(0, 7, QTableWidgetItem(""))
        
        self.directors_table.insertRow(1)
        self.directors_table.setItem(1, 0, QTableWidgetItem("D002"))
        self.directors_table.setItem(1, 1, QTableWidgetItem("Sarah Johnson"))
        self.directors_table.setItem(1, 2, QTableWidgetItem("Financial Director"))
        self.directors_table.setItem(1, 3, QTableWidgetItem("sarah.j@company.com"))
        self.directors_table.setItem(1, 4, QTableWidgetItem("011 555 0002"))
        self.directors_table.setItem(1, 5, QTableWidgetItem("30%"))
        self.directors_table.setItem(1, 6, QTableWidgetItem("Active"))
        self.directors_table.setItem(1, 7, QTableWidgetItem(""))
        
        self.directors_table.insertRow(2)
        self.directors_table.setItem(2, 0, QTableWidgetItem("D003"))
        self.directors_table.setItem(2, 1, QTableWidgetItem("Mike Wilson"))
        self.directors_table.setItem(2, 2, QTableWidgetItem("Technical Director"))
        self.directors_table.setItem(2, 3, QTableWidgetItem("mike.w@company.com"))
        self.directors_table.setItem(2, 4, QTableWidgetItem("011 555 0003"))
        self.directors_table.setItem(2, 5, QTableWidgetItem("20%"))
        self.directors_table.setItem(2, 6, QTableWidgetItem("Active"))
        self.directors_table.setItem(2, 7, QTableWidgetItem(""))
        
        # Set column widths
        self.directors_table.setColumnWidth(0, 80)
        self.directors_table.setColumnWidth(1, 120)
        self.directors_table.setColumnWidth(2, 120)
        self.directors_table.setColumnWidth(3, 180)
        self.directors_table.setColumnWidth(4, 100)
        self.directors_table.setColumnWidth(5, 80)
        self.directors_table.setColumnWidth(6, 80)
        self.directors_table.setColumnWidth(7, 80)
        
        directors_card.addWidget(self.directors_table)
        layout.addWidget(directors_card)
        
        # Summary Section
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)
        
        total_directors_card = ModernCard("Total Directors")
        total_directors_label = QLabel("3")
        total_directors_label.setFont(RIGELFonts.heading(16, True))
        total_directors_label.setStyleSheet(f"color: {RIGELColors.INFO};")
        total_directors_card.addWidget(total_directors_label)
        summary_layout.addWidget(total_directors_card)
        
        active_directors_card = ModernCard("Active Directors")
        active_directors_label = QLabel("3")
        active_directors_label.setFont(RIGELFonts.heading(16, True))
        active_directors_label.setStyleSheet(f"color: {RIGELColors.SUCCESS};")
        active_directors_card.addWidget(active_directors_label)
        summary_layout.addWidget(active_directors_card)
        
        total_shareholding_card = ModernCard("Total Shareholding")
        total_shareholding_label = QLabel("90%")
        total_shareholding_label.setFont(RIGELFonts.heading(16, True))
        total_shareholding_label.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        total_shareholding_card.addWidget(total_shareholding_label)
        summary_layout.addWidget(total_shareholding_card)
        
        layout.addLayout(summary_layout)
        layout.addStretch()
        
        return widget
    
    def create_projects_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("Projects Management")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Projects Management with tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                background-color: {RIGELColors.BACKGROUND_CARD};
                padding: "0px";
            }}
            QTabWidget::tab-bar {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTabBar::tab {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "24px";
                margin-right: "2px";
                border-top-left-radius: "4px";
                border-top-right-radius: "4px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # Active Projects Tab
        projects_tab = QWidget()
        projects_layout = QVBoxLayout(projects_tab)
        projects_layout.setContentsMargins(30, 30, 30, 30)
        projects_layout.setSpacing(16)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        add_project_btn = QPushButton("+ New Project")
        add_project_btn.setFont(RIGELFonts.body(11, True))
        add_project_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.PRIMARY_GREEN_HOVER};
            }}
        """)
        actions_layout.addWidget(add_project_btn)
        
        edit_project_btn = QPushButton("Edit Project")
        edit_project_btn.setFont(RIGELFonts.body(11, True))
        edit_project_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.SECONDARY_BLUE};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.SECONDARY_BLUE_HOVER};
            }}
        """)
        actions_layout.addWidget(edit_project_btn)
        
        close_project_btn = QPushButton("Close Project")
        close_project_btn.setFont(RIGELFonts.body(11, True))
        close_project_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RIGELColors.WARNING};
                color: {RIGELColors.TEXT_WHITE};
                border: none;
                border-radius: "6px";
                padding: "10px" "20px";
                font-family: "Segoe UI";
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {RIGELColors.WARNING};
                opacity: 0.8;
            }}
        """)
        actions_layout.addWidget(close_project_btn)
        
        actions_layout.addStretch()
        projects_layout.addLayout(actions_layout)
        
        # Projects table
        projects_card = ModernCard("Active Projects")
        projects_card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
        """)
        
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(9)
        self.projects_table.setHorizontalHeaderLabels([
            "Project ID", "Name", "Client", "Start Date", "End Date", "Budget", "Status", "Progress", "Actions"
        ])
        self.projects_table.horizontalHeader().setStretchLastSection(True)
        self.projects_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "6px";
                gridline-color: {RIGELColors.BORDER_LIGHT};
                selection-background-color: {RIGELColors.PRIMARY_GREEN};
                font-family: "Segoe UI";
                font-size: "11px";
            }}
            QTableWidget::item {{
                padding: "12px" "8px";
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background-color: {RIGELColors.BACKGROUND_SELECTED};
                color: {RIGELColors.TEXT_PRIMARY};
                font-weight: 600;
            }}
            QHeaderView::section {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "8px";
                font-weight: 600;
                font-family: "Segoe UI";
                font-size: "12px";
                border-bottom: "2px" solid {RIGELColors.PRIMARY_GREEN};
            }}
        """)
        
        # Add sample data
        self.projects_table.insertRow(0)
        self.projects_table.setItem(0, 0, QTableWidgetItem("P001"))
        self.projects_table.setItem(0, 1, QTableWidgetItem("Website Development"))
        self.projects_table.setItem(0, 2, QTableWidgetItem("ABC Company"))
        self.projects_table.setItem(0, 3, QTableWidgetItem("2024/01/15"))
        self.projects_table.setItem(0, 4, QTableWidgetItem("2024/03/15"))
        self.projects_table.setItem(0, 5, QTableWidgetItem("R 150,000.00"))
        self.projects_table.setItem(0, 6, QTableWidgetItem("In Progress"))
        self.projects_table.setItem(0, 7, QTableWidgetItem("65%"))
        self.projects_table.setItem(0, 8, QTableWidgetItem(""))
        
        self.projects_table.insertRow(1)
        self.projects_table.setItem(1, 0, QTableWidgetItem("P002"))
        self.projects_table.setItem(1, 1, QTableWidgetItem("Mobile App"))
        self.projects_table.setItem(1, 2, QTableWidgetItem("XYZ Corp"))
        self.projects_table.setItem(1, 3, QTableWidgetItem("2024/02/01"))
        self.projects_table.setItem(1, 4, QTableWidgetItem("2024/04/30"))
        self.projects_table.setItem(1, 5, QTableWidgetItem("R 200,000.00"))
        self.projects_table.setItem(1, 6, QTableWidgetItem("In Progress"))
        self.projects_table.setItem(1, 7, QTableWidgetItem("40%"))
        self.projects_table.setItem(1, 8, QTableWidgetItem(""))
        
        self.projects_table.insertRow(2)
        self.projects_table.setItem(2, 0, QTableWidgetItem("P003"))
        self.projects_table.setItem(2, 1, QTableWidgetItem("System Integration"))
        self.projects_table.setItem(2, 2, QTableWidgetItem("Tech Solutions"))
        self.projects_table.setItem(2, 3, QTableWidgetItem("2024/01/10"))
        self.projects_table.setItem(2, 4, QTableWidgetItem("2024/02/28"))
        self.projects_table.setItem(2, 5, QTableWidgetItem("R 75,000.00"))
        self.projects_table.setItem(2, 6, QTableWidgetItem("Completed"))
        self.projects_table.setItem(2, 7, QTableWidgetItem("100%"))
        self.projects_table.setItem(2, 8, QTableWidgetItem(""))
        
        # Set column widths
        self.projects_table.setColumnWidth(0, 80)
        self.projects_table.setColumnWidth(1, 150)
        self.projects_table.setColumnWidth(2, 120)
        self.projects_table.setColumnWidth(3, 100)
        self.projects_table.setColumnWidth(4, 100)
        self.projects_table.setColumnWidth(5, 100)
        self.projects_table.setColumnWidth(6, 100)
        self.projects_table.setColumnWidth(7, 80)
        self.projects_table.setColumnWidth(8, 80)
        
        projects_card.addWidget(self.projects_table)
        projects_layout.addWidget(projects_card)
        projects_layout.addStretch()
        
        tab_widget.addTab(projects_tab, "Active Projects")
        
        # Project Archive Tab
        archive_tab = QWidget()
        archive_layout = QVBoxLayout(archive_tab)
        archive_layout.setContentsMargins(30, 30, 30, 30)
        archive_layout.setSpacing(16)
        
        archive_card = ModernCard("Project Archive")
        archive_content = QLabel("View and manage completed and archived projects with historical data and performance metrics")
        archive_content.setFont(RIGELFonts.body(12))
        archive_content.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY}; padding: 20px;")
        archive_card.addWidget(archive_content)
        archive_layout.addWidget(archive_card)
        archive_layout.addStretch()
        
        tab_widget.addTab(archive_tab, "Archive")
        
        layout.addWidget(tab_widget)
        
        return widget
    
    def create_settings_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        title = QLabel("System Settings")
        title.setFont(RIGELFonts.heading(18, True))
        title.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        layout.addWidget(title)
        
        # Settings with tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                background-color: {RIGELColors.BACKGROUND_CARD};
                padding: "0px";
            }}
            QTabWidget::tab-bar {{
                background-color: {RIGELColors.BACKGROUND_DARK};
                border-bottom: "1px" solid {RIGELColors.BORDER_LIGHT};
            }}
            QTabBar::tab {{
                background-color: {RIGELColors.BACKGROUND_SIDEBAR};
                color: {RIGELColors.TEXT_PRIMARY};
                padding: "12px" "24px";
                margin-right: "2px";
                border-top-left-radius: "4px";
                border-top-right-radius: "4px";
                font-family: "Segoe UI";
                font-size: "12px";
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background-color: {RIGELColors.PRIMARY_GREEN};
                color: {RIGELColors.TEXT_WHITE};
            }}
        """)
        
        # General Settings Tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setContentsMargins(30, 30, 30, 30)
        general_layout.setSpacing(16)
        
        general_card = ModernCard("General Settings")
        general_form = QFormLayout()
        general_form.setSpacing(12)
        
        company_name = QLineEdit()
        company_name.setText("ABC (PTY) Ltd")
        general_form.addRow("Company Name *:", company_name)
        
        company_email = QLineEdit()
        company_email.setText("info@abccompany.co.za")
        general_form.addRow("Company Email *:", company_email)
        
        company_phone = QLineEdit()
        company_phone.setText("011 555 1234")
        general_form.addRow("Company Phone *:", company_phone)
        
        currency = QComboBox()
        currency.addItems(["ZAR - South African Rand", "USD - US Dollar", "EUR - Euro", "GBP - British Pound"])
        currency.setCurrentText("ZAR - South African Rand")
        general_form.addRow("Default Currency *:", currency)
        
        date_format = QComboBox()
        date_format.addItems(["YYYY/MM/DD", "DD/MM/YYYY", "MM/DD/YYYY"])
        date_format.setCurrentText("YYYY/MM/DD")
        general_form.addRow("Date Format *:", date_format)
        
        general_card.addLayout(general_form)
        general_layout.addWidget(general_card)
        general_layout.addStretch()
        
        tab_widget.addTab(general_tab, "General")
        
        # Security Settings Tab
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        security_layout.setContentsMargins(30, 30, 30, 30)
        security_layout.setSpacing(16)
        
        security_card = ModernCard("Security Settings")
        security_content = QLabel("Configure user authentication, password policies, data encryption, and access control settings")
        security_content.setFont(RIGELFonts.body(12))
        security_content.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY}; padding: 20px;")
        security_card.addWidget(security_content)
        security_layout.addWidget(security_card)
        security_layout.addStretch()
        
        tab_widget.addTab(security_tab, "Security")
        
        # Backup Settings Tab
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        backup_layout.setContentsMargins(30, 30, 30, 30)
        backup_layout.setSpacing(16)
        
        backup_card = ModernCard("Backup Settings")
        backup_content = QLabel("Configure automatic backup schedules, backup locations, and data retention policies")
        backup_content.setFont(RIGELFonts.body(12))
        backup_content.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY}; padding: 20px;")
        backup_card.addWidget(backup_content)
        backup_layout.addWidget(backup_card)
        backup_layout.addStretch()
        
        tab_widget.addTab(backup_tab, "Backup")
        
        layout.addWidget(tab_widget)
        
        return widget
    
    def create_report_card(self, icon: str, title: str, description: str, category: str):
        """Create a report card with icon, title, and description"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {RIGELColors.BACKGROUND_CARD};
                border: "1px" solid {RIGELColors.BORDER_LIGHT};
                border-radius: "8px";
                padding: "0px";
            }}
            QFrame:hover {{
                border-color: {RIGELColors.PRIMARY_GREEN};
                box-shadow: 0 "2px" "8px" rgba(0, 166, 81, 0.1);
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)
        
        # Icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        icon_label = QLabel(icon)
        icon_label.setFont(RIGELFonts.heading(24))
        icon_label.setStyleSheet(f"color: {RIGELColors.PRIMARY_GREEN};")
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(RIGELFonts.heading(12, True))
        title_label.setStyleSheet(f"color: {RIGELColors.TEXT_PRIMARY};")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setFont(RIGELFonts.body(10))
        desc_label.setStyleSheet(f"color: {RIGELColors.TEXT_SECONDARY};")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        # Generate button
        generate_btn = QPushButton("Generate Report")
        generate_btn.setFont(RIGELFonts.body(10, True))
        
        # Set button color based on category
        if category == "financial":
            btn_color = RIGELColors.PRIMARY_GREEN
        elif category == "management":
            btn_color = RIGELColors.INFO
        elif category == "tax":
            btn_color = RIGELColors.WARNING
        else:
            btn_color = RIGELColors.SECONDARY_BLUE
            
        generate_btn.setStyleSheet(f"QPushButton {{ background-color: {btn_color}; color: {RIGELColors.TEXT_WHITE}; border: none; border-radius: \"6px\"; padding: \"10px\" \"16px\"; font-family: \"Segoe UI\"; font-weight: 600; }} QPushButton:hover {{ background-color: {btn_color}dd; }} QPushButton:pressed {{ background-color: {btn_color}aa; }}")
        card_layout.addWidget(generate_btn)
        
        # Set fixed size for card
        card.setFixedSize(280, 180)
        
        return card
    
    # Customer CRUD Methods
    def load_customers_data(self):
        """Load customers from database into table"""
        self.customers_table.setRowCount(0)
        customers = db.get_customers()
        
        for customer in customers:
            row = self.customers_table.rowCount()
            self.customers_table.insertRow(row)
            self.customers_table.setItem(row, 0, QTableWidgetItem(customer.get('customer_code', '')))
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer.get('name', '')))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer.get('phone', '')))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer.get('email', '')))
            self.customers_table.setItem(row, 4, QTableWidgetItem(customer.get('contact_person', '')))
            self.customers_table.setItem(row, 5, QTableWidgetItem(""))
            # Store customer ID in the row
            self.customers_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, customer.get('id'))
    
    def add_customer(self):
        """Open dialog to add new customer"""
        dialog = CustomerFormDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            customer_data = dialog.data
            if db.add_customer(customer_data):
                QMessageBox.information(self, "Success", "Customer added successfully!")
                self.load_customers_data()
            else:
                QMessageBox.warning(self, "Error", "Failed to add customer.")
    
    def edit_customer(self):
        """Open dialog to edit selected customer"""
        selected_row = self.customers_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a customer to edit.")
            return
        
        # Get customer ID from stored data
        customer_id = self.customers_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        customers = db.get_customers()
        customer_data = next((c for c in customers if c['id'] == customer_id), None)
        
        if customer_data:
            dialog = CustomerFormDialog(self, customer_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.data
                if db.update_customer(customer_id, updated_data):
                    QMessageBox.information(self, "Success", "Customer updated successfully!")
                    self.load_customers_data()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update customer.")
    
    def delete_customer(self):
        """Delete selected customer"""
        selected_row = self.customers_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a customer to delete.")
            return
        
        # Get customer ID from stored data
        customer_id = self.customers_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        customer_name = self.customers_table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete customer '{customer_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if db.delete_customer(customer_id):
                QMessageBox.information(self, "Success", "Customer deleted successfully!")
                self.load_customers_data()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete customer.")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    app.setStyleSheet(f"QMainWindow {{ background-color: {RIGELColors.BACKGROUND_MAIN}; }}")
    
    window = RIGELMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
