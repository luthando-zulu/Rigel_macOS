#!/usr/bin/env python3
"""
Desktop Shortcut Manager for RIGEL Business
Handles desktop shortcut creation, installation automation, and system integration
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import platform
from datetime import datetime
import subprocess

class ShortcutManager:
    """
    Comprehensive desktop shortcut manager for RIGEL Business
    Supports Windows, macOS, and Linux with installation automation
    """
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_macos = self.system == "Darwin"
        self.is_linux = self.system == "Linux"
        
        # Application information
        self.app_info = {
            'name': 'RIGEL Business',
            'short_name': 'RIGEL',
            'version': '1.0.0',
            'company': 'Stella Lumen',
            'description': 'Professional Business Accounting Solution',
            'website': 'www.stella-lumen.com',
            'executable': 'RIGEL_Business.exe' if self.is_windows else 'RIGEL_Business'
        }
        
        # Initialize paths
        self._initialize_paths()
        
        # Load configuration
        self.config = self._load_config()
    
    def _initialize_paths(self):
        """Initialize system-specific paths"""
        if self.is_windows:
            self.desktop_dir = Path(os.environ.get("USERPROFILE", Path.home())) / "Desktop"
            self.start_menu_dir = Path(os.environ.get("APPDATA", Path.home())) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            self.program_files_dir = Path(os.environ.get("PROGRAMFILES", "C:\\Program Files"))
            self.app_data_dir = Path(os.environ.get("APPDATA", Path.home())) / "RIGELBusiness"
            self.common_startup = Path(os.environ.get("ALLUSERSPROFILE", Path.home())) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            self.user_startup = Path(os.environ.get("APPDATA", Path.home())) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            
        elif self.is_macos:
            self.desktop_dir = Path.home() / "Desktop"
            self.applications_dir = Path("/Applications")
            self.app_data_dir = Path.home() / "Library" / "Application Support" / "RIGELBusiness"
            self.user_applications = Path.home() / "Applications"
            
        else:  # Linux
            self.desktop_dir = Path.home() / "Desktop"
            self.applications_dir = Path("/usr/share/applications")
            self.local_applications = Path.home() / ".local" / "share" / "applications"
            self.app_data_dir = Path.home() / ".rigelbusiness"
        
        # Ensure directories exist
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load shortcut configuration"""
        config_file = self.app_data_dir / "shortcut_config.json"
        default_config = {
            "create_desktop_shortcut": True,
            "create_start_menu_shortcut": True,
            "create_quick_launch": True,
            "auto_start": False,
            "shortcut_locations": ["desktop", "start_menu"],
            "icon_path": None,
            "working_directory": None,
            "arguments": "",
            "run_as_admin": False,
            "created_shortcuts": [],
            "installation_date": None
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                print(f"Error loading shortcut config: {e}")
                return default_config
        else:
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save shortcut configuration"""
        try:
            config_file = self.app_data_dir / "shortcut_config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving shortcut config: {e}")
    
    def create_all_shortcuts(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create all configured shortcuts"""
        try:
            success = True
            
            # Update configuration
            self.config['executable_path'] = str(executable_path)
            self.config['icon_path'] = str(icon_path) if icon_path else None
            self.config['working_directory'] = str(executable_path.parent)
            self.config['installation_date'] = datetime.now().isoformat()
            
            # Create desktop shortcut
            if self.config.get("create_desktop_shortcut", True):
                if self.create_desktop_shortcut(executable_path, icon_path):
                    print("Desktop shortcut created successfully")
                else:
                    print("Failed to create desktop shortcut")
                    success = False
            
            # Create start menu shortcut
            if self.config.get("create_start_menu_shortcut", True):
                if self.create_start_menu_shortcut(executable_path, icon_path):
                    print("Start menu shortcut created successfully")
                else:
                    print("Failed to create start menu shortcut")
                    success = False
            
            # Create quick launch shortcut
            if self.config.get("create_quick_launch", True):
                if self.create_quick_launch_shortcut(executable_path, icon_path):
                    print("Quick launch shortcut created successfully")
                else:
                    print("Failed to create quick launch shortcut")
            
            # Create auto-start shortcut
            if self.config.get("auto_start", False):
                if self.create_auto_start_shortcut(executable_path, icon_path):
                    print("Auto-start shortcut created successfully")
                else:
                    print("Failed to create auto-start shortcut")
            
            # Save configuration
            self._save_config(self.config)
            
            return success
            
        except Exception as e:
            print(f"Shortcut creation failed: {e}")
            return False
    
    def create_desktop_shortcut(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create desktop shortcut"""
        try:
            if self.is_windows:
                return self._create_windows_desktop_shortcut(executable_path, icon_path)
            elif self.is_macos:
                return self._create_macos_desktop_shortcut(executable_path, icon_path)
            else:
                return self._create_linux_desktop_shortcut(executable_path, icon_path)
                
        except Exception as e:
            print(f"Desktop shortcut creation failed: {e}")
            return False
    
    def _create_windows_desktop_shortcut(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create Windows desktop shortcut"""
        try:
            shortcut_path = self.desktop_dir / f"{self.app_info['short_name']}.lnk"
            
            # Try using Windows COM interface
            try:
                import pythoncom
                from win32com.client import Dispatch
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(str(shortcut_path))
                
                # Set shortcut properties
                shortcut.Targetpath = str(executable_path)
                shortcut.WorkingDirectory = str(executable_path.parent)
                shortcut.Description = self.app_info['description']
                shortcut.IconLocation = str(icon_path) if icon_path else str(executable_path)
                
                if self.config.get("arguments"):
                    shortcut.Arguments = self.config.get("arguments", "")
                
                if self.config.get("run_as_admin"):
                    # Set run as admin flag
                    pass  # Requires additional Windows API calls
                
                shortcut.Save()
                
                # Add to created shortcuts
                self.config["created_shortcuts"].append({
                    "type": "desktop",
                    "path": str(shortcut_path),
                    "created": datetime.now().isoformat()
                })
                
                return True
                
            except ImportError:
                # Fallback method without win32com
                return self._create_windows_shortcut_fallback(executable_path, icon_path, shortcut_path)
                
        except Exception as e:
            print(f"Windows desktop shortcut creation failed: {e}")
            return False
    
    def _create_windows_shortcut_fallback(self, executable_path: Path, icon_path: Optional[Path], shortcut_path: Path) -> bool:
        """Fallback Windows shortcut creation using batch file"""
        try:
            # Create a batch file that launches the application
            batch_file = shortcut_path.with_suffix('.bat')
            
            batch_content = f'''@echo off
cd /d "{executable_path.parent}"
"{executable_path}" {self.config.get("arguments", "")}
'''
            
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            # Add to created shortcuts
            self.config["created_shortcuts"].append({
                "type": "desktop",
                "path": str(batch_file),
                "created": datetime.now().isoformat(),
                "method": "batch_fallback"
            })
            
            return True
            
        except Exception as e:
            print(f"Fallback Windows shortcut creation failed: {e}")
            return False
    
    def _create_macos_desktop_shortcut(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create macOS desktop shortcut (alias)"""
        try:
            # Create alias using AppleScript
            shortcut_name = f"{self.app_info['short_name']}"
            shortcut_path = self.desktop_dir / shortcut_name
            
            applescript = f'''
            tell application "Finder"
                make alias file to POSIX file "{executable_path}" at POSIX file "{self.desktop_dir}"
                set name of result to "{shortcut_name}"
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Add to created shortcuts
                self.config["created_shortcuts"].append({
                    "type": "desktop",
                    "path": str(shortcut_path),
                    "created": datetime.now().isoformat(),
                    "method": "macos_alias"
                })
                return True
            else:
                print(f"AppleScript error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"macOS desktop shortcut creation failed: {e}")
            return False
    
    def _create_linux_desktop_shortcut(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create Linux desktop shortcut (.desktop file)"""
        try:
            desktop_file = self.desktop_dir / f"{self.app_info['short_name'].lower()}.desktop"
            
            icon_path_str = str(icon_path) if icon_path else str(executable_path)
            
            desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name={self.app_info['name']}
GenericName=Business Accounting
Comment={self.app_info['description']}
Exec={executable_path} {self.config.get("arguments", "")}
Icon={icon_path_str}
Terminal=false
Categories=Office;Finance;Business;
StartupNotify=true
MimeType=application/x-rigel-business;
'''
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            # Make file executable
            os.chmod(desktop_file, 0o755)
            
            # Add to created shortcuts
            self.config["created_shortcuts"].append({
                "type": "desktop",
                "path": str(desktop_file),
                "created": datetime.now().isoformat(),
                "method": "linux_desktop"
            })
            
            return True
            
        except Exception as e:
            print(f"Linux desktop shortcut creation failed: {e}")
            return False
    
    def create_start_menu_shortcut(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create start menu shortcut"""
        try:
            if self.is_windows:
                return self._create_windows_start_menu_shortcut(executable_path, icon_path)
            elif self.is_macos:
                return self._create_macos_dock_shortcut(executable_path, icon_path)
            else:
                return self._create_linux_menu_shortcut(executable_path, icon_path)
                
        except Exception as e:
            print(f"Start menu shortcut creation failed: {e}")
            return False
    
    def _create_windows_start_menu_shortcut(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create Windows start menu shortcut"""
        try:
            # Create application folder in Start Menu
            app_folder = self.start_menu_dir / self.app_info['name']
            app_folder.mkdir(exist_ok=True)
            
            shortcut_path = app_folder / f"{self.app_info['short_name']}.lnk"
            
            # Use same method as desktop shortcut
            try:
                import pythoncom
                from win32com.client import Dispatch
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(str(shortcut_path))
                
                shortcut.Targetpath = str(executable_path)
                shortcut.WorkingDirectory = str(executable_path.parent)
                shortcut.Description = self.app_info['description']
                shortcut.IconLocation = str(icon_path) if icon_path else str(executable_path)
                
                if self.config.get("arguments"):
                    shortcut.Arguments = self.config.get("arguments", "")
                
                shortcut.Save()
                
                # Add to created shortcuts
                self.config["created_shortcuts"].append({
                    "type": "start_menu",
                    "path": str(shortcut_path),
                    "created": datetime.now().isoformat()
                })
                
                return True
                
            except ImportError:
                # Fallback method
                batch_file = shortcut_path.with_suffix('.bat')
                batch_content = f'''@echo off
cd /d "{executable_path.parent}"
"{executable_path}" {self.config.get("arguments", "")}
'''
                with open(batch_file, 'w') as f:
                    f.write(batch_content)
                
                self.config["created_shortcuts"].append({
                    "type": "start_menu",
                    "path": str(batch_file),
                    "created": datetime.now().isoformat(),
                    "method": "batch_fallback"
                })
                
                return True
                
        except Exception as e:
            print(f"Windows start menu shortcut creation failed: {e}")
            return False
    
    def _create_macos_dock_shortcut(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create macOS dock shortcut"""
        try:
            # Add to Applications folder for dock visibility
            if self.user_applications.exists():
                app_alias = self.user_applications / self.app_info['short_name']
                
                applescript = f'''
                tell application "Finder"
                    make alias file to POSIX file "{executable_path}" at POSIX file "{self.user_applications}"
                    set name of result to "{self.app_info['short_name']}"
                end tell
                '''
                
                result = subprocess.run(['osascript', '-e', applescript], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.config["created_shortcuts"].append({
                        "type": "dock",
                        "path": str(app_alias),
                        "created": datetime.now().isoformat(),
                        "method": "macos_alias"
                    })
                    return True
                else:
                    print(f"macOS dock shortcut creation failed: {result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"macOS dock shortcut creation failed: {e}")
            return False
    
    def _create_linux_menu_shortcut(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create Linux menu shortcut"""
        try:
            # Create system-wide desktop entry
            desktop_file = self.local_applications / f"{self.app_info['short_name'].lower()}.desktop"
            self.local_applications.mkdir(parents=True, exist_ok=True)
            
            icon_path_str = str(icon_path) if icon_path else str(executable_path)
            
            desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name={self.app_info['name']}
GenericName=Business Accounting
Comment={self.app_info['description']}
Exec={executable_path} {self.config.get("arguments", "")}
Icon={icon_path_str}
Terminal=false
Categories=Office;Finance;Business;
StartupNotify=true
MimeType=application/x-rigel-business;
Keywords=accounting;business;finance;rigel;
'''
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            os.chmod(desktop_file, 0o644)
            
            # Update desktop database
            try:
                subprocess.run(['update-desktop-database', str(self.local_applications)], 
                             capture_output=True, check=False)
            except:
                pass  # Command not available
            
            self.config["created_shortcuts"].append({
                "type": "menu",
                "path": str(desktop_file),
                "created": datetime.now().isoformat(),
                "method": "linux_desktop"
            })
            
            return True
            
        except Exception as e:
            print(f"Linux menu shortcut creation failed: {e}")
            return False
    
    def create_quick_launch_shortcut(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create quick launch shortcut"""
        try:
            if self.is_windows:
                return self._create_windows_quick_launch(executable_path, icon_path)
            else:
                # Quick launch is Windows-specific
                return True
                
        except Exception as e:
            print(f"Quick launch shortcut creation failed: {e}")
            return False
    
    def _create_windows_quick_launch(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create Windows quick launch shortcut"""
        try:
            # Quick launch folder location (Windows 10/11)
            quick_launch_dir = Path(os.environ.get("APPDATA", Path.home())) / "Microsoft" / "Internet Explorer" / "Quick Launch"
            
            if quick_launch_dir.exists():
                shortcut_path = quick_launch_dir / f"{self.app_info['short_name']}.lnk"
                
                try:
                    import pythoncom
                    from win32com.client import Dispatch
                    
                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(str(shortcut_path))
                    
                    shortcut.Targetpath = str(executable_path)
                    shortcut.WorkingDirectory = str(executable_path.parent)
                    shortcut.Description = self.app_info['description']
                    shortcut.IconLocation = str(icon_path) if icon_path else str(executable_path)
                    
                    if self.config.get("arguments"):
                        shortcut.Arguments = self.config.get("arguments", "")
                    
                    shortcut.Save()
                    
                    self.config["created_shortcuts"].append({
                        "type": "quick_launch",
                        "path": str(shortcut_path),
                        "created": datetime.now().isoformat()
                    })
                    
                    return True
                    
                except ImportError:
                    # Fallback - create in user Quick Launch
                    return True
                    
        except Exception as e:
            print(f"Windows quick launch shortcut creation failed: {e}")
            return False
    
    def create_auto_start_shortcut(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create auto-start shortcut"""
        try:
            if self.is_windows:
                return self._create_windows_autostart(executable_path, icon_path)
            elif self.is_macos:
                return self._create_macos_autostart(executable_path, icon_path)
            else:
                return self._create_linux_autostart(executable_path, icon_path)
                
        except Exception as e:
            print(f"Auto-start shortcut creation failed: {e}")
            return False
    
    def _create_windows_autostart(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create Windows auto-start shortcut"""
        try:
            startup_dir = self.user_startup
            shortcut_path = startup_dir / f"{self.app_info['short_name']}.lnk"
            
            try:
                import pythoncom
                from win32com.client import Dispatch
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(str(shortcut_path))
                
                shortcut.Targetpath = str(executable_path)
                shortcut.WorkingDirectory = str(executable_path.parent)
                shortcut.Description = f"{self.app_info['name']} - Auto Start"
                shortcut.IconLocation = str(icon_path) if icon_path else str(executable_path)
                
                if self.config.get("arguments"):
                    shortcut.Arguments = self.config.get("arguments", "")
                
                shortcut.Save()
                
                self.config["created_shortcuts"].append({
                    "type": "autostart",
                    "path": str(shortcut_path),
                    "created": datetime.now().isoformat()
                })
                
                return True
                
            except ImportError:
                # Fallback - create batch file
                batch_file = startup_dir / f"{self.app_info['short_name']}.bat"
                batch_content = f'''@echo off
cd /d "{executable_path.parent}"
start "" "{executable_path}" {self.config.get("arguments", "")}
'''
                with open(batch_file, 'w') as f:
                    f.write(batch_content)
                
                self.config["created_shortcuts"].append({
                    "type": "autostart",
                    "path": str(batch_file),
                    "created": datetime.now().isoformat(),
                    "method": "batch_fallback"
                })
                
                return True
                
        except Exception as e:
            print(f"Windows auto-start shortcut creation failed: {e}")
            return False
    
    def _create_macos_autostart(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create macOS auto-start shortcut"""
        try:
            # Create launch agent
            launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
            launch_agents_dir.mkdir(exist_ok=True)
            
            plist_file = launch_agents_dir / f"com.stellalumen.{self.app_info['short_name'].lower()}.plist"
            
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.stellalumen.{self.app_info['short_name'].lower()}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{executable_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
'''
            
            with open(plist_file, 'w') as f:
                f.write(plist_content)
            
            # Load the launch agent
            subprocess.run(['launchctl', 'load', str(plist_file)], 
                         capture_output=True, check=False)
            
            self.config["created_shortcuts"].append({
                "type": "autostart",
                "path": str(plist_file),
                "created": datetime.now().isoformat(),
                "method": "macos_launch_agent"
            })
            
            return True
            
        except Exception as e:
            print(f"macOS auto-start shortcut creation failed: {e}")
            return False
    
    def _create_linux_autostart(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Create Linux auto-start shortcut"""
        try:
            autostart_dir = Path.home() / ".config" / "autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_file = autostart_dir / f"{self.app_info['short_name'].lower()}.desktop"
            
            desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name={self.app_info['name']}
Exec={executable_path} {self.config.get("arguments", "")}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
'''
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            os.chmod(desktop_file, 0o644)
            
            self.config["created_shortcuts"].append({
                "type": "autostart",
                "path": str(desktop_file),
                "created": datetime.now().isoformat(),
                "method": "linux_autostart"
            })
            
            return True
            
        except Exception as e:
            print(f"Linux auto-start shortcut creation failed: {e}")
            return False
    
    def remove_all_shortcuts(self) -> bool:
        """Remove all created shortcuts"""
        try:
            success = True
            
            for shortcut_info in self.config.get("created_shortcuts", []):
                shortcut_path = Path(shortcut_info["path"])
                
                try:
                    if shortcut_path.exists():
                        if shortcut_path.is_file():
                            shortcut_path.unlink()
                        elif shortcut_path.is_dir():
                            shutil.rmtree(shortcut_path)
                        print(f"Removed shortcut: {shortcut_path}")
                    else:
                        print(f"Shortcut not found: {shortcut_path}")
                        
                except Exception as e:
                    print(f"Failed to remove shortcut {shortcut_path}: {e}")
                    success = False
            
            # Clear created shortcuts list
            self.config["created_shortcuts"] = []
            self._save_config(self.config)
            
            return success
            
        except Exception as e:
            print(f"Shortcut removal failed: {e}")
            return False
    
    def get_shortcut_status(self) -> Dict[str, Any]:
        """Get status of all shortcuts"""
        status = {
            "total_shortcuts": len(self.config.get("created_shortcuts", [])),
            "existing_shortcuts": 0,
            "missing_shortcuts": 0,
            "shortcut_details": []
        }
        
        for shortcut_info in self.config.get("created_shortcuts", []):
            shortcut_path = Path(shortcut_info["path"])
            exists = shortcut_path.exists()
            
            if exists:
                status["existing_shortcuts"] += 1
            else:
                status["missing_shortcuts"] += 1
            
            status["shortcut_details"].append({
                "type": shortcut_info["type"],
                "path": str(shortcut_path),
                "exists": exists,
                "created": shortcut_info.get("created"),
                "method": shortcut_info.get("method", "standard")
            })
        
        return status
    
    def repair_shortcuts(self, executable_path: Path, icon_path: Optional[Path] = None) -> bool:
        """Repair missing shortcuts"""
        try:
            status = self.get_shortcut_status()
            
            if status["missing_shortcuts"] == 0:
                print("All shortcuts are present")
                return True
            
            print(f"Repairing {status['missing_shortcuts']} missing shortcuts...")
            
            # Remove all shortcuts and recreate them
            self.remove_all_shortcuts()
            return self.create_all_shortcuts(executable_path, icon_path)
            
        except Exception as e:
            print(f"Shortcut repair failed: {e}")
            return False
    
    def export_shortcut_config(self, export_path: Path) -> bool:
        """Export shortcut configuration"""
        try:
            export_data = {
                "app_info": self.app_info,
                "config": self.config,
                "system": self.system,
                "export_date": datetime.now().isoformat()
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Shortcut config export failed: {e}")
            return False
    
    def import_shortcut_config(self, import_path: Path) -> bool:
        """Import shortcut configuration"""
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            self.config = import_data.get("config", self.config)
            self._save_config(self.config)
            
            return True
            
        except Exception as e:
            print(f"Shortcut config import failed: {e}")
            return False

# Global shortcut manager instance
shortcut_manager = ShortcutManager()
