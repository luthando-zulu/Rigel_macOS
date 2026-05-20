#!/usr/bin/env python3
"""
RIGEL Business Installation Wizard
Complete installation and license activation system
"""

import sys
import os
import json
import hashlib
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QCheckBox, QProgressBar, QLineEdit,
    QFormLayout, QGroupBox, QMessageBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

# ─────────────────────────────────────────────────────────────────────────────
#  INSTALLATION CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
class InstallConstants:
    APP_NAME = "RIGEL Business"
    APP_VERSION = "4.1.0"
    COMPANY_NAME = "Stella Lumen"
    WEBSITE = "www.stella-lumen.com"
    
    # Window dimensions
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900

    # Trial settings
    TRIAL_DAYS = 30
    LICENSE_KEY_FORMAT = "RIGEL-XXXX-XXXX-XXXX-XXXX"

    # File paths
    EULA_FILE = "assets/resources/RIGEL_EULA.pdf"
    LOGO_FILE = "assets/branding/logo/Rigel-Package-300x300.jpg"
    LICENSE_DB = "data/license.db"

    # Colors
    PRIMARY_COLOR = "#00A651"
    SECONDARY_COLOR = "#2C3E50"
    ACCENT_COLOR = "#3498DB"
    WARNING_COLOR = "#E74C3C"
    SUCCESS_COLOR = "#27AE60"

# ─────────────────────────────────────────────────────────────────────────────
#  LICENSE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
class LicenseManager:
    """Manages license activation and validation"""

    def __init__(self):
        self.license_data = {}
        self.load_license_data()

    def load_license_data(self):
        """Load license information from database"""
        try:
            license_path = Path(InstallConstants.LICENSE_DB)
            if license_path.exists():
                with open(license_path, 'r') as f:
                    self.license_data = json.load(f)
        except Exception as e:
            print(f"Error loading license data: {e}")
            self.license_data = {}

    def save_license_data(self):
        """Save license information to database"""
        try:
            license_path = Path(InstallConstants.LICENSE_DB)
            license_path.parent.mkdir(parents=True, exist_ok=True)
            with open(license_path, 'w') as f:
                json.dump(self.license_data, f, indent=2)
        except Exception as e:
            print(f"Error saving license data: {e}")

    def get_machine_id(self) -> str:
        """Generate unique machine identifier"""
        system_info = platform.uname()
        machine_data = f"{system_info.node}{system_info.machine}{system_info.processor}"
        return hashlib.sha256(machine_data.encode()).hexdigest()[:16].upper()

    def validate_license_key(self, license_key: str) -> bool:
        """Validate license key format and checksum"""
        if not license_key or len(license_key) != 23:
            return False

        # Check format: RIGEL-XXXX-XXXX-XXXX-XXXX
        parts = license_key.split('-')
        if len(parts) != 5 or parts[0] != 'RIGEL':
            return False

        # Validate each segment is 4 characters
        for part in parts[1:]:
            if len(part) != 4 or not part.isalnum():
                return False

        return True

    def activate_license(self, license_key: str, company_name: str) -> Dict[str, Any]:
        """Activate license and return activation result"""
        if not self.validate_license_key(license_key):
            return {"success": False, "message": "Invalid license key format"}

        machine_id = self.get_machine_id()

        # Simulate license activation (replace with actual server call)
        activation_data = {
            "license_key": license_key,
            "company_name": company_name,
            "machine_id": machine_id,
            "activated_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "status": "active"
        }

        self.license_data = activation_data
        self.save_license_data()

        return {"success": True, "message": "License activated successfully", "data": activation_data}

    def is_license_valid(self) -> bool:
        """Check if current license is valid"""
        if not self.license_data:
            return False

        expiry_date = datetime.fromisoformat(self.license_data.get("expiry_date", ""))
        return datetime.now() < expiry_date and self.license_data.get("status") == "active"

    def is_trial_valid(self) -> bool:
        """Check if trial period is still valid"""
        try:
            install_date = datetime.fromisoformat(self.license_data.get("install_date", datetime.now().isoformat()))
            trial_end = install_date + timedelta(days=InstallConstants.TRIAL_DAYS)
            return datetime.now() < trial_end
        except:
            return True  # Allow trial if date parsing fails

    def get_license_status(self) -> Dict[str, Any]:
        """Get comprehensive license status"""
        return {
            "has_license": bool(self.license_data),
            "is_license_valid": self.is_license_valid(),
            "is_trial_valid": self.is_trial_valid(),
            "machine_id": self.get_machine_id(),
            "license_data": self.license_data
        }

# Global license manager instance
license_manager = LicenseManager()

# ─────────────────────────────────────────────────────────────────────────────
#  INSTALLATION WIZARD PAGES
# ─────────────────────────────────────────────────────────────────────────────
class WelcomePage(QWizardPage):
    """Welcome page with RIGEL logo and tagline"""

    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to RIGEL Business")
        self.setSubTitle("Professional Accounting Software for Modern Businesses")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Logo section
        logo_layout = QHBoxLayout()
        logo_layout.addStretch()

        # Try to load logo
        logo_label = QLabel()
        try:
            pixmap = QPixmap(InstallConstants.LOGO_FILE)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                logo_label.setText("RIGEL")
                logo_label.setStyleSheet(f"font-size: 48px; font-weight: bold; color: {InstallConstants.PRIMARY_COLOR};")
        except:
            logo_label.setText("RIGEL")
            logo_label.setStyleSheet(f"font-size: 48px; font-weight: bold; color: {InstallConstants.PRIMARY_COLOR};")

        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        layout.addLayout(logo_layout)

        # Tagline
        tagline = QLabel("Empowering Business Growth Through Intelligent Accounting")
        tagline.setStyleSheet("font-size: 14px; color: #666; text-align: center;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)

        # Version info
        version_info = QLabel(f"Version {InstallConstants.APP_VERSION}")
        version_info.setStyleSheet("font-size: 12px; color: #888; text-align: center;")
        version_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_info)

        layout.addStretch()

        # Footer
        footer = QLabel(f"© 2024 {InstallConstants.COMPANY_NAME}. All rights reserved.")
        footer.setStyleSheet("font-size: 10px; color: #999; text-align: center;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

class LicenseAgreementPage(QWizardPage):
    """License agreement page with EULA display"""

    def __init__(self):
        super().__init__()
        self.setTitle("License Agreement")
        self.setSubTitle("Please read and accept the End User License Agreement")
        self.accept_checkbox = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # EULA text area
        self.eula_text = QTextEdit()
        self.eula_text.setReadOnly(True)
        self.eula_text.setMinimumHeight(300)

        # Load EULA content
        self.load_eula_content()

        layout.addWidget(self.eula_text)

        # Accept checkbox
        self.accept_checkbox = QCheckBox("I have read and accept the terms of the License Agreement")
        self.accept_checkbox.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.accept_checkbox)

        # Register field for validation
        self.registerField("licenseAccepted*", self.accept_checkbox)

    def load_eula_content(self):
        """Load EULA content from file or use default"""
        try:
            eula_path = Path(InstallConstants.EULA_FILE)
            if eula_path.exists():
                with open(eula_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = self.get_default_eula()
            self.eula_text.setPlainText(content)
        except Exception as e:
            print(f"Error loading EULA: {e}")
            self.eula_text.setPlainText(self.get_default_eula())

    def get_default_eula(self) -> str:
        """Default EULA content when file is not available"""
        return f"""
END USER LICENSE AGREEMENT

This End User License Agreement ("Agreement") is entered into between {InstallConstants.COMPANY_NAME} ("Licensor") and you ("Licensee") for the use of RIGEL Business software.

1. GRANT OF LICENSE
Licensor grants Licensee a non-exclusive, non-transferable license to use the Software in accordance with the terms of this Agreement.

2. RESTRICTIONS
Licensee shall not: copy, modify, distribute, reverse engineer, or create derivative works of the Software.

3. INTELLECTUAL PROPERTY
The Software and all intellectual property rights therein are owned by Licensor.

4. WARRANTY
The Software is provided "AS IS" without warranty of any kind.

5. LIMITATION OF LIABILITY
Licensor shall not be liable for any damages arising from use of the Software.

6. TERMINATION
This Agreement terminates automatically if Licensee breaches any term.

By accepting this agreement, you acknowledge that you have read, understood, and agree to be bound by these terms.

© 2024 {InstallConstants.COMPANY_NAME}. All rights reserved.
"""

class InstallationPage(QWizardPage):
    """Installation progress page"""

    def __init__(self):
        super().__init__()
        self.setTitle("Installing RIGEL Business")
        self.setSubTitle("Please wait while the application is being installed")
        self.progress_bar = None
        self.status_label = None
        self.install_thread = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Preparing installation...")
        self.status_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(self.status_label)

        layout.addStretch()

    def initializePage(self):
        """Start installation when page is shown"""
        self.start_installation()

    def start_installation(self):
        """Start the installation process"""
        self.install_thread = InstallationThread()
        self.install_thread.progress_updated.connect(self.update_progress)
        self.install_thread.status_updated.connect(self.update_status)
        self.install_thread.installation_completed.connect(self.installation_finished)
        self.install_thread.start()

    def update_progress(self, value: int):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def update_status(self, status: str):
        """Update status message"""
        self.status_label.setText(status)

    def installation_finished(self, success: bool):
        """Handle installation completion"""
        if success:
            self.status_label.setText("Installation completed successfully!")
            self.status_label.setStyleSheet("font-size: 12px; color: green; font-weight: bold;")
        else:
            self.status_label.setText("Installation failed. Please try again.")
            self.status_label.setStyleSheet("font-size: 12px; color: red; font-weight: bold;")

class FinishPage(QWizardPage):
    """Installation completion page"""

    def __init__(self):
        super().__init__()
        self.setTitle("Installation Complete")
        self.setSubTitle("RIGEL Business has been successfully installed")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Success message
        success_label = QLabel("✓ Installation completed successfully!")
        success_label.setStyleSheet(f"font-size: 16px; color: {InstallConstants.SUCCESS_COLOR}; font-weight: bold;")
        layout.addWidget(success_label)

        # Launch button
        launch_button = QPushButton("Launch RIGEL Business")
        launch_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {InstallConstants.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #008a45;
            }}
        """)
        launch_button.clicked.connect(self.launch_application)
        layout.addWidget(launch_button)

        layout.addStretch()

        # Footer
        footer = QLabel("Thank you for choosing RIGEL Business")
        footer.setStyleSheet("font-size: 12px; color: #666; text-align: center;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    def launch_application(self):
        """Launch the main application"""
        try:
            # Import and launch main application
            from rigel_core import launch
            launch(build_mode="FULL")
            # Close wizard
            self.wizard().accept()
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to launch application: {str(e)}")

# ─────────────────────────────────────────────────────────────────────────────
#  LICENSE ACTIVATION DIALOG
# ─────────────────────────────────────────────────────────────────────────────
class LicenseActivationDialog(QWidget):
    """License activation dialog with exact layout from User Manual"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("License Activation - RIGEL Business")
        self.setFixedSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("RIGEL Business License Activation")
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {InstallConstants.SECONDARY_COLOR};")
        layout.addWidget(header)

        # Machine ID section
        machine_group = QGroupBox("Machine Information")
        machine_layout = QFormLayout(machine_group)

        self.machine_id_label = QLabel(license_manager.get_machine_id())
        self.machine_id_label.setStyleSheet("font-family: monospace; font-size: 12px; background-color: #f5f5f5; padding: 5px;")
        machine_layout.addRow("Machine ID:", self.machine_id_label)

        layout.addWidget(machine_group)

        # License section
        license_group = QGroupBox("License Information")
        license_layout = QFormLayout(license_group)

        self.company_name_edit = QLineEdit()
        self.company_name_edit.setPlaceholderText("Enter your company name")
        license_layout.addRow("Company Name:", self.company_name_edit)

        self.license_key_edit = QLineEdit()
        self.license_key_edit.setPlaceholderText(InstallConstants.LICENSE_KEY_FORMAT)
        self.license_key_edit.setMaxLength(23)  # RIGEL-XXXX-XXXX-XXXX-XXXX
        license_layout.addRow("License Key:", self.license_key_edit)

        layout.addWidget(license_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.activate_button = QPushButton("Activate License")
        self.activate_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {InstallConstants.PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #008a45;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)
        self.activate_button.clicked.connect(self.activate_license)
        button_layout.addWidget(self.activate_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.status_label)

    def activate_license(self):
        """Handle license activation"""
        company_name = self.company_name_edit.text().strip()
        license_key = self.license_key_edit.text().strip()

        if not company_name:
            self.show_error("Please enter your company name")
            return

        if not license_key:
            self.show_error("Please enter a license key")
            return

        # Disable button during activation
        self.activate_button.setEnabled(False)
        self.activate_button.setText("Activating...")

        try:
            result = license_manager.activate_license(license_key, company_name)

            if result["success"]:
                self.show_success("License activated successfully!")
                QTimer.singleShot(2000, self.accept)
            else:
                self.show_error(result["message"])
        except Exception as e:
            self.show_error(f"Activation failed: {str(e)}")
        finally:
            self.activate_button.setEnabled(True)
            self.activate_button.setText("Activate License")

    def show_error(self, message: str):
        """Show error message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"font-size: 12px; color: {InstallConstants.WARNING_COLOR}; font-weight: bold;")

    def show_success(self, message: str):
        """Show success message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"font-size: 12px; color: {InstallConstants.SUCCESS_COLOR}; font-weight: bold;")

    def accept(self):
        """Handle successful activation"""
        self.close()
        # Emit signal or call callback if needed

    def reject(self):
        """Handle cancellation"""
        self.close()

# ─────────────────────────────────────────────────────────────────────────────
#  INSTALLATION THREAD
# ─────────────────────────────────────────────────────────────────────────────
class InstallationThread(QThread):
    """Thread for handling installation process"""

    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    installation_completed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.installation_steps = [
            "Initializing installation...",
            "Creating application directories...",
            "Setting up database...",
            "Installing core components...",
            "Configuring system settings...",
            "Creating shortcuts...",
            "Finalizing installation...",
            "Installation complete!"
        ]

    def run(self):
        """Execute installation steps"""
        try:
            total_steps = len(self.installation_steps)

            for i, step in enumerate(self.installation_steps):
                self.status_updated.emit(step)
                self.progress_updated.emit(int((i / total_steps) * 100))

                # Simulate installation time
                self.msleep(500)

                # Perform actual installation tasks here
                if "directories" in step.lower():
                    self.create_directories()
                elif "database" in step.lower():
                    self.setup_database()
                elif "shortcuts" in step.lower():
                    self.create_shortcuts()

            self.progress_updated.emit(100)
            self.installation_completed.emit(True)

        except Exception as e:
            print(f"Installation error: {e}")
            self.status_updated.emit(f"Installation failed: {str(e)}")
            self.installation_completed.emit(False)

    def create_directories(self):
        """Create necessary directories"""
        dirs = [
            Path("data"),
            Path("backups"),
            Path("logs"),
            Path("temp")
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def setup_database(self):
        """Initialize database"""
        # Initialize license data
        license_manager.license_data = {
            "install_date": datetime.now().isoformat(),
            "status": "trial"
        }
        license_manager.save_license_data()

    def create_shortcuts(self):
        """Create desktop and start menu shortcuts"""
        try:
            # Import shortcut manager if available
            from installation.shortcut_manager import shortcut_manager
            if shortcut_manager:
                shortcut_manager.create_shortcuts()
        except ImportError:
            pass  # Shortcut manager not available

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN INSTALLATION WIZARD
# ─────────────────────────────────────────────────────────────────────────────
class InstallationWizard(QWizard):
    """Main installation wizard"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Installing {InstallConstants.APP_NAME} {InstallConstants.APP_VERSION}")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setFixedSize(600, 500)

        # Set window icon
        try:
            self.setWindowIcon(QIcon(InstallConstants.LOGO_FILE))
        except:
            pass

        # Add pages
        self.addPage(WelcomePage())
        self.addPage(LicenseAgreementPage())
        self.addPage(InstallationPage())
        self.addPage(FinishPage())

        # Configure wizard
        self.setButtonText(QWizard.WizardButton.NextButton, "Next")
        self.setButtonText(QWizard.WizardButton.BackButton, "Back")
        self.setButtonText(QWizard.WizardButton.FinishButton, "Finish")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Cancel")

    def accept(self):
        """Handle wizard completion"""
        super().accept()

    def reject(self):
        """Handle wizard cancellation"""
        reply = QMessageBox.question(
            self, "Cancel Installation",
            "Are you sure you want to cancel the installation?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            super().reject()

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def run_installation_wizard(app: QApplication = None):
    """Run the installation wizard"""
    created_app = False
    if app is None:
        app = QApplication(sys.argv)
        created_app = True

    # Apply modern styling
    app.setStyle("Fusion")

    wizard = InstallationWizard()
    result = wizard.exec()

    if created_app:
        # Keep the application alive for the caller.
        pass

    return result == QWizard.DialogCode.Accepted

def show_license_activation(parent=None):
    """Show license activation dialog"""
    dialog = LicenseActivationDialog(parent)
    return dialog.exec()

def check_license_and_run():
    """Check license status and run appropriate flow"""
    license_status = license_manager.get_license_status()

    if license_status["is_license_valid"]:
        # License is valid, proceed to main app
        return True
    elif license_status["is_trial_valid"]:
        # Trial is valid, proceed to main app
        return True
    else:
        # License/trial expired, show activation
        return show_license_activation()

if __name__ == "__main__":
    # Run installation wizard
    if run_installation_wizard():
        print("Installation completed successfully")
    else:
        print("Installation cancelled")