#!/usr/bin/env python3
"""
RIGEL Business Styles
"""

def get_stylesheet():
    """Get main application stylesheet"""
    return "QMainWindow { background-color: #F5F5F5; } QPushButton { background-color: #00B050; color: white; }"

def get_dialog_style():
    """Get dialog stylesheet"""
    return "QDialog { background-color: #F5F5F5; }"

def apply_modern_style(app):
    """Apply modern styling to the application"""
    app.setStyleSheet(get_stylesheet())
