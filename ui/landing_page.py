#!/usr/bin/env python3
"""
RIGEL Business Landing Page
Main index page with Register Company and Transact buttons
"""

import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGridLayout, QSpacerItem,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QLinearGradient

from installation.installation_wizard import license_manager, InstallConstants
from core.chart_of_accounts import coa_manager

# ─────────────────────────────────────────────────────────────────────────────
#  LANDING PAGE WIDGET
# ─────────────────────────────────────────────────────────────────────────────
class LandingPage(QWidget):
    """Main landing page with hero section and action buttons"""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                background-color: #e9ecef;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #00A651;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #008a45;
            }
        """)

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(30)

        # Hero section
        hero_section = self.create_hero_section()
        content_layout.addWidget(hero_section)

        # Action buttons section
        action_section = self.create_action_section()
        content_layout.addWidget(action_section)

        # Dashboard preview section
        dashboard_section = self.create_dashboard_preview()
        content_layout.addWidget(dashboard_section)

        # Features section
        features_section = self.create_features_section()
        content_layout.addWidget(features_section)

        # Footer
        footer_section = self.create_footer_section()
        content_layout.addWidget(footer_section)

        # Add stretch to push content to top
        content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

    def create_hero_section(self) -> QWidget:
        """Create hero section with logo and tagline"""
        hero_widget = QWidget()
        hero_layout = QVBoxLayout(hero_widget)
        hero_layout.setContentsMargins(40, 40, 40, 40)
        hero_layout.setSpacing(20)

        # Logo and title section
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(20)

        # Logo
        logo_label = QLabel()
        try:
            # Try to load logo
            pixmap = QPixmap("assets/branding/logo/Rigel-Package-300x300.jpg")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                logo_label.setText("RIGEL")
                logo_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #00A651;")
        except:
            logo_label.setText("RIGEL")
            logo_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #00A651;")

        logo_layout.addWidget(logo_label)

        # Title and tagline
        title_layout = QVBoxLayout()
        title_layout.setSpacing(10)

        title = QLabel("RIGEL Business")
        title.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #2C3E50;
        """)

        tagline = QLabel("Professional Accounting Software for Modern Businesses")
        tagline.setStyleSheet("""
            font-size: 18px;
            color: #6A7575;
        """)

        powered_by = QLabel("Powered by Stella Lumen")
        powered_by.setStyleSheet("""
            font-size: 12px;
            color: #00A651;
            font-weight: bold;
        """)

        title_layout.addWidget(title)
        title_layout.addWidget(tagline)
        title_layout.addWidget(powered_by)
        title_layout.addStretch()

        logo_layout.addLayout(title_layout)
        logo_layout.addStretch()

        hero_layout.addLayout(logo_layout)

        # Version and license info
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)

        version_info = QLabel(f"Version {InstallConstants.APP_VERSION}")
        version_info.setStyleSheet("font-size: 14px; color: #888;")

        license_status = license_manager.get_license_status()
        if license_status["is_license_valid"]:
            license_info = QLabel("✓ Licensed Version")
            license_info.setStyleSheet("font-size: 14px; color: #27AE60; font-weight: bold;")
        elif license_status["is_trial_valid"]:
            days_left = 30  # Calculate actual days left
            license_info = QLabel(f"Trial Version ({days_left} days left)")
            license_info.setStyleSheet("font-size: 14px; color: #E74C3C; font-weight: bold;")
        else:
            license_info = QLabel("License Expired")
            license_info.setStyleSheet("font-size: 14px; color: #E74C3C; font-weight: bold;")

        info_layout.addWidget(version_info)
        info_layout.addWidget(license_info)
        info_layout.addStretch()

        hero_layout.addLayout(info_layout)

        return hero_widget

    def create_action_section(self) -> QWidget:
        """Create action buttons section"""
        action_widget = QWidget()
        action_layout = QVBoxLayout(action_widget)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(20)

        # Section title
        section_title = QLabel("Get Started")
        section_title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            text-align: center;
        """)
        section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        action_layout.addWidget(section_title)

        # Buttons grid
        buttons_widget = QWidget()
        buttons_layout = QGridLayout(buttons_widget)
        buttons_layout.setSpacing(20)

        # Register Company button
        register_button = self.create_action_button(
            "Register Company",
            "Set up your company profile and chart of accounts",
            "🏢",
            self.on_register_company
        )

        # Transact button
        transact_button = self.create_action_button(
            "Transact",
            "Start recording business transactions",
            "💼",
            self.on_transact
        )

        # Reports button
        reports_button = self.create_action_button(
            "Reports",
            "Generate financial statements and reports",
            "📊",
            self.on_reports
        )

        # Settings button
        settings_button = self.create_action_button(
            "Settings",
            "Configure application preferences",
            "⚙️",
            self.on_settings
        )

        buttons_layout.addWidget(register_button, 0, 0)
        buttons_layout.addWidget(transact_button, 0, 1)
        buttons_layout.addWidget(reports_button, 1, 0)
        buttons_layout.addWidget(settings_button, 1, 1)

        action_layout.addWidget(buttons_widget)

        return action_widget

    def create_action_button(self, title: str, description: str, icon: str,
                           callback) -> QPushButton:
        """Create an action button with icon and description"""
        button = QPushButton()
        button.setFixedSize(250, 120)

        # Create button layout
        button_layout = QVBoxLayout(button)
        button_layout.setContentsMargins(15, 15, 15, 15)
        button_layout.setSpacing(8)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2C3E50;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #6A7575;
            text-align: center;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)

        button_layout.addWidget(icon_label)
        button_layout.addWidget(title_label)
        button_layout.addWidget(desc_label)

        # Button styling
        button.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #F8F9FA;
                border-color: #00A651;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background-color: #E9ECEF;
                transform: translateY(0px);
            }
        """)

        button.clicked.connect(callback)
        return button

    def create_features_section(self) -> QWidget:
        """Create features overview section"""
        features_widget = QWidget()
        features_layout = QVBoxLayout(features_widget)
        features_layout.setContentsMargins(0, 0, 0, 0)
        features_layout.setSpacing(20)

        # Section title
        title = QLabel("Why Choose RIGEL Business?")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            text-align: center;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        features_layout.addWidget(title)

        # Features grid
        features_grid = QGridLayout()
        features_grid.setSpacing(20)

        features = [
            ("📈", "Real-time Financial Reporting", "Generate balance sheets, income statements, and cash flow reports instantly"),
            ("🔒", "Secure & Compliant", "Built with security in mind, compliant with accounting standards"),
            ("⚡", "Fast & Efficient", "Streamlined workflows for quick transaction processing"),
            ("📱", "User-Friendly Interface", "Intuitive design that accounting professionals love"),
            ("🔄", "Multi-Company Support", "Manage multiple companies from a single interface"),
            ("☁️", "Cloud-Ready", "Prepare your business for cloud migration when ready")
        ]

        for i, (icon, title_text, desc) in enumerate(features):
            row = i // 2
            col = i % 2

            feature_card = self.create_feature_card(icon, title_text, desc)
            features_grid.addWidget(feature_card, row, col)

        features_layout.addLayout(features_grid)

        return features_widget

    def create_feature_card(self, icon: str, title: str, description: str) -> QWidget:
        """Create a feature card"""
        card = QWidget()
        card.setFixedHeight(120)
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
            }
            QWidget:hover {
                border-color: #00A651;
                background-color: #F8F9FA;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2C3E50;
            text-align: center;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 11px;
            color: #6A7575;
            text-align: center;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)

        return card

    def create_footer_section(self) -> QWidget:
        """Create footer section"""
        footer_widget = QWidget()
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 40, 0, 20)
        footer_layout.setSpacing(10)

        # Footer text
        footer_text = QLabel("© 2024 Stella Lumen. All rights reserved.")
        footer_text.setStyleSheet("""
            font-size: 12px;
            color: #888;
            text-align: center;
        """)
        footer_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        footer_layout.addWidget(footer_text)

        return footer_widget

    # ─────────────────────────────────────────────────────────────────────────
    #  ACTION HANDLERS
    # ─────────────────────────────────────────────────────────────────────────
    def on_register_company(self):
        """Handle Register Company button click"""
        try:
            from modules.registration import registration_module
            self.main_window.show_module(registration_module.RegistrationModule(self.main_window))
        except ImportError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Coming Soon",
                                  "Company Registration module is under development.")

    def on_transact(self):
        """Handle Transact button click"""
        try:
            from modules.transact import transact_module
            self.main_window.show_module(transact_module.TransactModule(self.main_window))
        except ImportError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Coming Soon",
                                  "Transaction module is under development.")

    def on_reports(self):
        """Handle Reports button click"""
        try:
            from modules.reports import reports_module
            self.main_window.show_module(reports_module.ReportsModule(self.main_window))
        except ImportError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Coming Soon",
                                  "Reports module is under development.")

    def on_settings(self):
        """Handle Settings button click"""
        try:
            from modules.settings import settings_module
            self.main_window.show_module(settings_module.SettingsModule(self.main_window))
        except ImportError:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Coming Soon",
                                  "Settings module is under development.")

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN APPLICATION INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────
def create_landing_page(main_window) -> LandingPage:
    """Factory function to create landing page"""
    return LandingPage(main_window)

if __name__ == "__main__":
    # Test the landing page
    app = QApplication(sys.argv)

    # Mock main window
    class MockMainWindow:
        def show_module(self, module):
            print(f"Showing module: {module}")

    window = MockMainWindow()
    landing = create_landing_page(window)
    landing.show()

    sys.exit(app.exec())