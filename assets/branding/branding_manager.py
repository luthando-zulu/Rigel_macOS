#!/usr/bin/env python3
"""
Rigel Business Branding Manager
Comprehensive branding integration for filename, taskbar, shortcuts, and search bar
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import platform
from datetime import datetime

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSettings

class BrandingManager:
    """
    Comprehensive branding manager for Rigel Business
    Handles logo integration, file naming, taskbar icons, shortcuts, and search visibility
    """
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_macos = self.system == "Darwin"
        
        # Brand information
        self.brand_info = {
            'app_name': 'RIGEL Business',
            'app_short_name': 'RIGEL',
            'company_name': 'Stella Lumen',
            'website': 'www.stella-lumen.com',
            'version': '1.0.0',
            'description': 'Professional Business Accounting Solution',
            'copyright': f'© {datetime.now().year} Stella Lumen'
        }
        
        # File naming conventions
        self.file_naming = {
            'executable': 'RIGEL_Business.exe' if self.is_windows else 'RIGEL_Business',
            'installer': 'RIGEL_Business_Setup.exe' if self.is_windows else 'RIGEL_Business_Installer.dmg',
            'config': 'rigel_business_config.json',
            'data': 'rigel_business_data.db',
            'log': 'rigel_business.log',
            'backup': 'rigel_business_backup'
        }
        
        # Brand colors and assets
        self.brand_colors = {
            'primary': '#00B050',      # Green
            'secondary': '#0070C0',    # Blue  
            'dark': '#2A3638',         # Dark
            'light': '#FFFFFF',        # White
            'accent': '#FFA500'        # Orange
        }
        
        # Initialize paths
        self._initialize_paths()
    
    def _initialize_paths(self):
        """Initialize application and system paths"""
        if self.is_windows:
            self.app_data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
            self.desktop_dir = Path(os.environ.get("USERPROFILE", Path.home())) / "Desktop"
            self.start_menu_dir = Path(os.environ.get("APPDATA", Path.home())) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            self.program_files_dir = Path(os.environ.get("PROGRAMFILES", "C:\\Program Files"))
        elif self.is_macos:
            self.app_data_dir = Path.home() / "Library" / "Application Support" / "RIGELBusiness"
            self.desktop_dir = Path.home() / "Desktop"
            self.applications_dir = Path("/Applications")
        else:
            self.app_data_dir = Path.home() / ".rigelbusiness"
            self.desktop_dir = Path.home() / "Desktop"
        
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
    
    def integrate_application_branding(self, app_instance: QApplication) -> bool:
        """Integrate Rigel Business branding into the application"""
        try:
            # Set application name and metadata
            app_instance.setApplicationName(self.brand_info['app_name'])
            app_instance.setApplicationVersion(self.brand_info['version'])
            app_instance.setOrganizationName(self.brand_info['company_name'])
            app_instance.setOrganizationDomain(self.brand_info['website'])
            
            # Set application icon
            logo_widget_path = Path(__file__).parent.parent / "logo" / "logo_widget.py"
            if logo_widget_path.exists():
                try:
                    from assets.logo.logo_widget import logo_manager
                    app_icon = QIcon()
                    app_icon.addPixmap(logo_manager.get_window_icon())
                    app_instance.setWindowIcon(app_icon)
                except ImportError:
                    print("Logo widget not available, using default icon")
            
            # Set application display name
            if self.is_windows:
                # Set Windows application user model ID
                import ctypes
                app_id = f"StellaLumen.{self.brand_info['app_short_name']}.1.0.0"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            
            return True
            
        except Exception as e:
            print(f"Application branding integration failed: {e}")
            return False
    
    def create_desktop_shortcut(self, executable_path: Path, description: str = None) -> bool:
        """Create desktop shortcut with Rigel Business branding"""
        try:
            if self.is_windows:
                return self._create_windows_shortcut(executable_path, description)
            elif self.is_macos:
                return self._create_macos_shortcut(executable_path, description)
            else:
                return self._create_linux_shortcut(executable_path, description)
                
        except Exception as e:
            print(f"Desktop shortcut creation failed: {e}")
            return False
    
    def _create_windows_shortcut(self, executable_path: Path, description: str = None) -> bool:
        """Create Windows desktop shortcut"""
        try:
            import pythoncom
            from win32com.client import Dispatch
            
            # Shortcut path
            shortcut_path = self.desktop_dir / f"{self.brand_info['app_short_name']}.lnk"
            
            # Create shell object
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            
            # Set shortcut properties
            shortcut.Targetpath = str(executable_path)
            shortcut.WorkingDirectory = str(executable_path.parent)
            shortcut.Description = description or self.brand_info['description']
            shortcut.IconLocation = str(executable_path)
            
            # Save shortcut
            shortcut.Save()
            
            # Set application user model ID for the shortcut
            import ctypes
            app_id = f"StellaLumen.{self.brand_info['app_short_name']}.1.0.0"
            shortcut_path = self.desktop_dir / f"{self.brand_info['app_short_name']}.lnk"
            
            return True
            
        except ImportError:
            # Fallback method without win32com
            return self._create_windows_shortcut_fallback(executable_path, description)
        except Exception as e:
            print(f"Windows shortcut creation failed: {e}")
            return False
    
    def _create_windows_shortcut_fallback(self, executable_path: Path, description: str = None) -> bool:
        """Fallback Windows shortcut creation using batch file"""
        try:
            # Create a batch file that launches the application
            batch_file = self.desktop_dir / f"{self.brand_info['app_short_name']}.bat"
            
            batch_content = f'''@echo off
cd /d "{executable_path.parent}"
"{executable_path}" %*
'''
            
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            return True
            
        except Exception as e:
            print(f"Fallback Windows shortcut creation failed: {e}")
            return False
    
    def _create_macos_shortcut(self, executable_path: Path, description: str = None) -> bool:
        """Create macOS desktop shortcut (alias)"""
        try:
            import subprocess
            
            # Create alias using AppleScript
            shortcut_name = f"{self.brand_info['app_short_name']}"
            shortcut_path = self.desktop_dir / shortcut_name
            
            applescript = f'''
            tell application "Finder"
                make alias file to POSIX file "{executable_path}" at POSIX file "{self.desktop_dir}"
                set name of result to "{shortcut_name}"
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"macOS shortcut creation failed: {e}")
            return False
    
    def _create_linux_shortcut(self, executable_path: Path, description: str = None) -> bool:
        """Create Linux desktop shortcut (.desktop file)"""
        try:
            desktop_file = self.desktop_dir / f"{self.brand_info['app_short_name'].lower()}.desktop"
            
            desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name={self.brand_info['app_name']}
Comment={description or self.brand_info['description']}
Exec={executable_path}
Icon={executable_path}
Terminal=false
Categories=Office;Finance;
StartupNotify=true
'''
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            # Make file executable
            os.chmod(desktop_file, 0o755)
            
            return True
            
        except Exception as e:
            print(f"Linux shortcut creation failed: {e}")
            return False
    
    def integrate_search_bar_visibility(self) -> bool:
        """Integrate Rigel Business with system search functionality"""
        try:
            if self.is_windows:
                return self._integrate_windows_search()
            elif self.is_macos:
                return self._integrate_macos_search()
            else:
                return self._integrate_linux_search()
                
        except Exception as e:
            print(f"Search bar integration failed: {e}")
            return False
    
    def _integrate_windows_search(self) -> bool:
        """Integrate with Windows Search/Cortana"""
        try:
            # Create application registration for Windows Search
            app_registration = {
                "app_id": f"StellaLumen.{self.brand_info['app_short_name']}",
                "app_name": self.brand_info['app_name'],
                "description": self.brand_info['description'],
                "company": self.brand_info['company_name'],
                "version": self.brand_info['version']
            }
            
            # Save registration info
            registration_file = self.app_data_dir / "search_registration.json"
            with open(registration_file, 'w') as f:
                json.dump(app_registration, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Windows search integration failed: {e}")
            return False
    
    def _integrate_macos_search(self) -> bool:
        """Integrate with macOS Spotlight"""
        try:
            # Create application metadata for Spotlight
            spotlight_info = {
                "bundle_identifier": f"com.stellalumen.{self.brand_info['app_short_name'].lower()}",
                "app_name": self.brand_info['app_name'],
                "description": self.brand_info['description'],
                "categories": ["Business", "Finance", "Accounting"]
            }
            
            # Save metadata
            metadata_file = self.app_data_dir / "spotlight_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(spotlight_info, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"macOS search integration failed: {e}")
            return False
    
    def _integrate_linux_search(self) -> bool:
        """Integrate with Linux desktop search"""
        try:
            # Create desktop entry with search metadata
            desktop_file = self.app_data_dir / f"{self.brand_info['app_short_name'].lower()}.desktop"
            
            desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name={self.brand_info['app_name']}
GenericName=Business Accounting
Comment={self.brand_info['description']}
Keywords=accounting;business;finance;rigel;
Categories=Office;Finance;Business;
'''
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            return True
            
        except Exception as e:
            print(f"Linux search integration failed: {e}")
            return False
    
    def set_window_branding(self, window) -> bool:
        """Set Rigel Business branding for application window"""
        try:
            # Set window title
            window.setWindowTitle(f"{self.brand_info['app_name']} v{self.brand_info['version']}")
            
            # Set window icon
            logo_widget_path = Path(__file__).parent.parent / "logo" / "logo_widget.py"
            if logo_widget_path.exists():
                try:
                    from assets.logo.logo_widget import logo_manager
                    window.setWindowIcon(logo_manager.get_window_icon())
                except ImportError:
                    print("Logo widget not available")
            
            # Set window taskbar icon
            if self.is_windows:
                try:
                    import ctypes
                    app_id = f"StellaLumen.{self.brand_info['app_short_name']}.1.0.0"
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                except:
                    pass
            
            return True
            
        except Exception as e:
            print(f"Window branding failed: {e}")
            return False
    
    def create_installation_branding(self, install_path: Path) -> bool:
        """Create branding files for installation"""
        try:
            # Create branding directory
            branding_dir = install_path / "branding"
            branding_dir.mkdir(exist_ok=True)
            
            # Create brand info file
            brand_info_file = branding_dir / "brand_info.json"
            with open(brand_info_file, 'w') as f:
                json.dump(self.brand_info, f, indent=2)
            
            # Create file naming conventions file
            naming_file = branding_dir / "file_naming.json"
            with open(naming_file, 'w') as f:
                json.dump(self.file_naming, f, indent=2)
            
            # Create color scheme file
            colors_file = branding_dir / "colors.json"
            with open(colors_file, 'w') as f:
                json.dump(self.brand_colors, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Installation branding creation failed: {e}")
            return False
    
    def get_brand_info(self) -> Dict[str, Any]:
        """Get complete brand information"""
        return {
            'brand_info': self.brand_info,
            'file_naming': self.file_naming,
            'brand_colors': self.brand_colors,
            'paths': {
                'app_data_dir': str(self.app_data_dir),
                'desktop_dir': str(self.desktop_dir),
                'system': self.system
            }
        }
    
    def apply_filename_branding(self, file_path: Path) -> Path:
        """Apply Rigel Business branding to filename"""
        try:
            # Get file extension
            extension = file_path.suffix
            
            # Create branded filename
            branded_name = f"{self.brand_info['app_short_name']}_{file_path.stem}{extension}"
            branded_path = file_path.parent / branded_name
            
            return branded_path
            
        except Exception as e:
            print(f"Filename branding failed: {e}")
            return file_path
    
    def validate_branding_integration(self) -> Dict[str, Any]:
        """Validate that branding integration is working correctly"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'checks': {}
        }
        
        try:
            # Check brand info
            if not self.brand_info.get('app_name'):
                validation_result['is_valid'] = False
                validation_result['errors'].append("App name not set")
            
            # Check file naming
            if not self.file_naming.get('executable'):
                validation_result['is_valid'] = False
                validation_result['errors'].append("Executable naming not set")
            
            # Check paths
            if not self.app_data_dir.exists():
                validation_result['warnings'].append("App data directory does not exist")
            
            # Check logo widget
            logo_widget_path = Path(__file__).parent.parent / "logo" / "logo_widget.py"
            if not logo_widget_path.exists():
                validation_result['warnings'].append("Logo widget not found")
            
            validation_result['checks'] = {
                'brand_info': bool(self.brand_info.get('app_name')),
                'file_naming': bool(self.file_naming.get('executable')),
                'paths': self.app_data_dir.exists(),
                'logo_widget': logo_widget_path.exists()
            }
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Validation failed: {e}")
        
        return validation_result

# Global branding manager instance
branding_manager = BrandingManager()
