#!/usr/bin/env python3
"""
RIGEL Business Main Application Window
QMainWindow with QStackedWidget for module navigation
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QLabel, QPushButton, QFrame, QScrollArea,
    QMessageBox, QSplitter, QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QAction

from installation.installation_wizard import license_manager, InstallConstants
from ui.landing_page import create_landing_page
from modules.reports_center import create_reports_center
from modules.company_setup import create_company_setup
from core.chart_of_accounts import coa_manager

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
class SidebarNavigation(QWidget):
    """Sidebar navigation with menu items"""

    navigation_requested = pyqtSignal(str)  # Signal for navigation

    def __init__(self):
        super().__init__()
        self.current_page = "landing"
        self.setup_ui()

    def setup_ui(self):
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QWidget {
                background-color: #1E2A2A;
                border-right: 1px solid #34495E;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo section
        logo_section = self.create_logo_section()
        layout.addWidget(logo_section)

        # Navigation menu
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        nav_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2C3E50;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #00A651;
                border-radius: 4px;
                min-height: 30px;
            }
        """)

        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(5)

        # Navigation items
        self.nav_items = self.create_navigation_items()
        for item in self.nav_items:
            nav_layout.addWidget(item)

        nav_layout.addStretch()
        nav_scroll.setWidget(nav_widget)
        layout.addWidget(nav_scroll)

        # Footer
        footer = self.create_footer()
        layout.addWidget(footer)

    def create_logo_section(self) -> QWidget:
        """Create logo section at top of sidebar"""
        logo_widget = QWidget()
        logo_widget.setFixedHeight(120)
        logo_widget.setStyleSheet("""
            QWidget {
                background-color: #2A3638;
                border-bottom: 1px solid #34495E;
            }
        """)

        layout = QVBoxLayout(logo_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Logo
        logo_label = QLabel()
        try:
            pixmap = QPixmap("assets/branding/logo/Rigel-Package-300x300.jpg")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                logo_label.setText("RIGEL")
                logo_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00A651;")
        except:
            logo_label.setText("RIGEL")
            logo_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00A651;")

        # App name
        app_name = QLabel("RIGEL Business")
        app_name.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
        """)

        # Version
        version = QLabel(f"v{InstallConstants.APP_VERSION}")
        version.setStyleSheet("""
            font-size: 12px;
            color: #BDC3C7;
        """)

        # Powered by
        powered_by = QLabel("Powered by Stella Lumen")
        powered_by.setStyleSheet("""
            font-size: 10px;
            color: #00A651;
            font-weight: bold;
        """)

        layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(app_name, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(powered_by, alignment=Qt.AlignmentFlag.AlignCenter)

        return logo_widget

    def create_navigation_items(self) -> list:
        """Create navigation menu items"""
        items = []

        # Define menu items with their properties
        menu_items = [
            {
                "id": "landing",
                "text": "Dashboard",
                "icon": "🏠",
                "description": "Main dashboard and overview"
            },
            {
                "id": "registration",
                "text": "Registration",
                "icon": "📝",
                "description": "Company registration and setup"
            },
            {
                "id": "transact",
                "text": "Transact",
                "icon": "💼",
                "description": "Record business transactions"
            },
            {
                "id": "cashbook",
                "text": "Cash Book",
                "icon": "💰",
                "description": "Cash book management"
            },
            {
                "id": "customers",
                "text": "Customers",
                "icon": "👥",
                "description": "Customer management"
            },
            {
                "id": "directors",
                "text": "Directors",
                "icon": "👔",
                "description": "Director transactions"
            },
            {
                "id": "employees",
                "text": "Employees",
                "icon": "👷",
                "description": "Employee management"
            },
            {
                "id": "inventories",
                "text": "Inventories",
                "icon": "📦",
                "description": "Inventory management"
            },
            {
                "id": "assets",
                "text": "Fixed Assets",
                "icon": "🏢",
                "description": "Fixed assets management"
            },
            {
                "id": "projects",
                "text": "Projects",
                "icon": "📋",
                "description": "Project management"
            },
            {
                "id": "adjustments",
                "text": "Adjustments",
                "icon": "⚙️",
                "description": "Accounting adjustments"
            },
            {
                "id": "reports",
                "text": "Reports",
                "icon": "📊",
                "description": "Financial reports and statements"
            }
        ]

        for item_data in menu_items:
            item = self.create_nav_item(item_data)
            items.append(item)

        return items

    def create_nav_item(self, item_data: Dict[str, str]) -> QPushButton:
        """Create a navigation item button"""
        button = QPushButton()
        button.setProperty("nav_id", item_data["id"])
        button.setFixedHeight(50)
        button.setCheckable(True)

        # Layout
        layout = QHBoxLayout(button)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(item_data["icon"])
        icon_label.setFixedSize(24, 24)
        icon_label.setStyleSheet("font-size: 16px;")

        # Text layout
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title = QLabel(item_data["text"])
        title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: white;
        """)

        desc = QLabel(item_data["description"])
        desc.setStyleSheet("""
            font-size: 10px;
            color: #BDC3C7;
        """)

        text_layout.addWidget(title)
        text_layout.addWidget(desc)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()

        # Styling
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 6px;
                text-align: left;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
            QPushButton:checked {
                background-color: #00A651;
                border-left: 4px solid #27AE60;
            }
            QPushButton:checked QLabel {
                color: white;
            }
        """)

        button.clicked.connect(lambda: self.on_nav_clicked(item_data["id"]))
        return button

    def create_footer(self) -> QWidget:
        """Create footer with license info"""
        footer = QWidget()
        footer.setFixedHeight(80)
        footer.setStyleSheet("""
            QWidget {
                background-color: #2A3638;
                border-top: 1px solid #34495E;
            }
        """)

        layout = QVBoxLayout(footer)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)

        # License status
        license_status = license_manager.get_license_status()
        if license_status["is_license_valid"]:
            status_text = "✓ Licensed"
            status_color = "#27AE60"
        elif license_status["is_trial_valid"]:
            days_left = 30  # Calculate actual days
            status_text = f"Trial ({days_left} days)"
            status_color = "#E74C3C"
        else:
            status_text = "License Expired"
            status_color = "#E74C3C"

        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: bold;
            color: {status_color};
            text-align: center;
        """)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Activate license button
        activate_button = QPushButton("Activate License")
        activate_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 5px 10px;
                font-size: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        activate_button.clicked.connect(self.show_license_activation)

        layout.addWidget(status_label)
        layout.addWidget(activate_button)

        return footer

    def on_nav_clicked(self, nav_id: str):
        """Handle navigation item click"""
        # Update current page
        self.current_page = nav_id

        # Update button states
        for item in self.nav_items:
            nav_id_prop = item.property("nav_id")
            item.setChecked(nav_id_prop == nav_id)

        # Emit navigation signal
        self.navigation_requested.emit(nav_id)

    def set_active_page(self, page_id: str):
        """Set the active navigation page"""
        self.current_page = page_id

        # Update button states
        for item in self.nav_items:
            nav_id_prop = item.property("nav_id")
            item.setChecked(nav_id_prop == page_id)

    def show_license_activation(self):
        """Show license activation dialog"""
        from installation.installation_wizard import LicenseActivationDialog
        dialog = LicenseActivationDialog(self)
        dialog.exec()

# ─────────────────────────────────────────────────────────────────────────────
#  HEADER BAR
# ─────────────────────────────────────────────────────────────────────────────
class HeaderBar(QWidget):
    """Top header bar with version info and user actions"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QWidget {
                background-color: #2A3638;
                border-bottom: 1px solid #34495E;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)

        # Version info
        version_layout = QVBoxLayout()
        version_layout.setSpacing(2)

        version_label = QLabel(f"RIGEL Business v{InstallConstants.APP_VERSION}")
        version_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: white;
        """)

        build_type = "Complete" if "FULL" in os.environ.get("BUILD_MODE", "") else "Trial"
        build_label = QLabel(f"{build_type} Version")
        build_label.setStyleSheet("""
            font-size: 10px;
            color: #BDC3C7;
        """)

        version_layout.addWidget(version_label)
        version_layout.addWidget(build_label)
        layout.addLayout(version_layout)

        layout.addStretch()

        # User actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)

        # Settings button
        settings_button = QPushButton("⚙️ Settings")
        settings_button.setStyleSheet(self.get_button_style())
        settings_button.clicked.connect(self.show_settings)
        actions_layout.addWidget(settings_button)

        # Help button
        help_button = QPushButton("❓ Help")
        help_button.setStyleSheet(self.get_button_style())
        help_button.clicked.connect(self.show_help)
        actions_layout.addWidget(help_button)

        # Logout button
        logout_button = QPushButton("🚪 Logout")
        logout_button.setStyleSheet(self.get_button_style("#E74C3C"))
        logout_button.clicked.connect(self.logout)
        actions_layout.addWidget(logout_button)

        layout.addLayout(actions_layout)

    def get_button_style(self, bg_color: str = "#3498DB") -> str:
        """Get button styling"""
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                padding: 8px 12px;
                font-size: 12px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {bg_color}CC;
            }}
        """

    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", "Settings dialog coming soon!")

    def show_help(self):
        """Show help dialog"""
        QMessageBox.information(self, "Help", "Help system coming soon!")

    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(self, "Logout",
                                   "Are you sure you want to log out?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Return to landing page
            self.main_window.show_landing_page()

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APPLICATION WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class RigelMainWindow(QMainWindow):
    """Main application window with sidebar navigation"""

    def __init__(self):
        super().__init__()
        self.modules = {}  # Cache for loaded modules
        self.current_module = None
        self.setup_window()
        self.setup_ui()
        self.setup_menu()
        self.show_landing_page()

    def setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle(f"RIGEL Business v{InstallConstants.APP_VERSION}")
        self.setMinimumSize(1200, 800)
        self.resize(InstallConstants.WINDOW_WIDTH, InstallConstants.WINDOW_HEIGHT)

        # Set window icon
        try:
            self.setWindowIcon(QIcon("assets/branding/logo/Rigel-Package-300x300.jpg"))
        except:
            pass

        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
        """)

    def setup_ui(self):
        """Setup main UI components"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = SidebarNavigation()
        self.sidebar.navigation_requested.connect(self.on_navigation_requested)
        main_layout.addWidget(self.sidebar)

        # Right panel (header + content)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header
        self.header = HeaderBar(self)
        right_layout.addWidget(self.header)

        # Content area with stacked widget
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #F8F9FA;
            }
        """)
        right_layout.addWidget(self.content_stack)

        main_layout.addWidget(right_panel)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2A3638;
                color: white;
                border-top: 1px solid #34495E;
            }
        """)
        self.status_bar.showMessage("Ready")

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2A3638;
                color: white;
                border-bottom: 1px solid #34495E;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 12px;
            }
            QMenuBar::item:selected {
                background-color: #34495E;
            }
        """)

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Company", self)
        new_action.triggered.connect(self.new_company)
        file_menu.addAction(new_action)

        open_action = QAction("Open Company", self)
        open_action.triggered.connect(self.open_company)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        backup_action = QAction("Backup Data", self)
        backup_action.triggered.connect(self.backup_data)
        tools_menu.addAction(backup_action)

        restore_action = QAction("Restore Data", self)
        restore_action.triggered.connect(self.restore_data)
        tools_menu.addAction(restore_action)

        tools_menu.addSeparator()

        license_action = QAction("License Manager", self)
        license_action.triggered.connect(self.show_license_manager)
        tools_menu.addAction(license_action)

        # Reports menu
        reports_menu = menubar.addMenu("Reports")

        financial_action = QAction("Financial Reports", self)
        financial_action.triggered.connect(lambda: self.show_module("reports"))
        reports_menu.addAction(financial_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About RIGEL", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        help_action = QAction("User Guide", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def on_navigation_requested(self, module_id: str):
        """Handle navigation request from sidebar"""
        self.show_module(module_id)

    def show_module(self, module_id: str):
        """Show a specific module"""
        try:
            # Update sidebar
            self.sidebar.set_active_page(module_id)

            # Get or create module
            if module_id not in self.modules:
                self.modules[module_id] = self.create_module(module_id)

            if self.modules[module_id]:
                # Switch to module
                self.content_stack.setCurrentWidget(self.modules[module_id])
                self.current_module = module_id
                self.status_bar.showMessage(f"Loaded {module_id} module")

        except Exception as e:
            QMessageBox.critical(self, "Module Error",
                               f"Failed to load {module_id} module: {str(e)}")

    def create_module(self, module_id: str) -> Optional[QWidget]:
        """Create a module instance"""
        try:
            if module_id == "landing":
                return create_landing_page(self)
            elif module_id == "registration":
                return create_company_setup(self)
            elif module_id == "reports":
                return create_reports_center(self)
            elif module_id == "transact":
                # Placeholder for transact module
                return self.create_placeholder_module("Transact", "Transaction recording module")
            elif module_id == "cashbook":
                return self.create_placeholder_module("Cash Book", "Cash book management module")
            elif module_id == "customers":
                return self.create_placeholder_module("Customers", "Customer management module")
            elif module_id == "directors":
                return self.create_placeholder_module("Directors", "Director transactions module")
            elif module_id == "employees":
                return self.create_placeholder_module("Employees", "Employee management module")
            elif module_id == "inventories":
                return self.create_placeholder_module("Inventories", "Inventory management module")
            elif module_id == "assets":
                return self.create_placeholder_module("Fixed Assets", "Fixed assets management module")
            elif module_id == "projects":
                return self.create_placeholder_module("Projects", "Project management module")
            elif module_id == "adjustments":
                return self.create_placeholder_module("Adjustments", "Accounting adjustments module")
            else:
                return self.create_placeholder_module("Unknown Module", "Module not implemented yet")

        except Exception as e:
            print(f"Error creating module {module_id}: {e}")
            return self.create_placeholder_module("Error", f"Failed to load module: {str(e)}")

    def create_placeholder_module(self, title: str, description: str) -> QWidget:
        """Create a placeholder module"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2C3E50;
            text-align: center;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 18px;
            color: #6A7575;
            text-align: center;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Coming soon message
        coming_soon = QLabel("🚧 This module is under development and will be available in the next update.")
        coming_soon.setStyleSheet("""
            font-size: 16px;
            color: #E74C3C;
            text-align: center;
            font-style: italic;
        """)
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(coming_soon)
        layout.addStretch()

        return widget

    def show_landing_page(self):
        """Show the landing page"""
        self.show_module("landing")

    # ─────────────────────────────────────────────────────────────────────────
    #  MENU ACTION HANDLERS
    # ─────────────────────────────────────────────────────────────────────────
    def new_company(self):
        """Create new company"""
        self.show_module("registration")

    def open_company(self):
        """Open existing company"""
        QMessageBox.information(self, "Open Company", "Company selection dialog coming soon!")

    def backup_data(self):
        """Backup application data"""
        QMessageBox.information(self, "Backup", "Data backup functionality coming soon!")

    def restore_data(self):
        """Restore application data"""
        QMessageBox.information(self, "Restore", "Data restore functionality coming soon!")

    def show_license_manager(self):
        """Show license manager"""
        from installation.installation_wizard import LicenseActivationDialog
        dialog = LicenseActivationDialog(self)
        dialog.exec()

    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        <h2>RIGEL Business</h2>
        <p><b>Version:</b> {InstallConstants.APP_VERSION}</p>
        <p><b>Company:</b> {InstallConstants.COMPANY_NAME}</p>
        <p><b>Website:</b> {InstallConstants.WEBSITE}</p>
        <p><br>Professional accounting software for modern businesses.</p>
        <p>© 2024 {InstallConstants.COMPANY_NAME}. All rights reserved.</p>
        """

        QMessageBox.about(self, "About RIGEL Business", about_text)

    def show_help(self):
        """Show help dialog"""
        QMessageBox.information(self, "Help", "User guide and help system coming soon!")

    def closeEvent(self, event):
        """Handle application close"""
        reply = QMessageBox.question(self, "Exit Application",
                                   "Are you sure you want to exit RIGEL Business?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

# ─────────────────────────────────────────────────────────────────────────────
#  APPLICATION LAUNCH
# ─────────────────────────────────────────────────────────────────────────────
def launch_main_application():
    """Launch the main RIGEL Business application"""
    app = QApplication(sys.argv)

    # Check license status
    license_status = license_manager.get_license_status()

    if not license_status["is_license_valid"] and not license_status["is_trial_valid"]:
        # Show license activation
        from installation.installation_wizard import LicenseActivationDialog
        dialog = LicenseActivationDialog()
        if dialog.exec() != 1:  # Dialog was cancelled
            return 1

    # Create and show main window
    window = RigelMainWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(launch_main_application())