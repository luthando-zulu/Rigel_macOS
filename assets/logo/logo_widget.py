#!/usr/bin/env python3
"""
Rigel Business Logo Widget
Professional logo display with multiple size options and animations
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QFont, QColor, QLinearGradient, QPen, QBrush, QPixmap
from pathlib import Path
import platform

class LogoWidget(QWidget):
    """
    Rigel Business logo widget with customizable sizes and animations
    """
    
    def __init__(self, parent=None, px=64, show_text=True, animated=True):
        super().__init__(parent)
        self.px = px
        self.show_text = show_text
        self.animated = animated
        self._opacity = 1.0
        
        # Set fixed size
        self.setFixedSize(self.px, self.px if not show_text else self.px + 20)
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        self.animation_phase = 0
        
        if self.animated:
            self.animation_timer.start(50)  # 20 FPS
    
    def paintEvent(self, event):
        """Paint the Rigel Business logo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Center point
        center_x = self.width() // 2
        center_y = (self.height() // 2) - (10 if self.show_text else 0)
        
        # Draw logo circle
        self._draw_logo_circle(painter, center_x, center_y)
        
        # Draw Rigel text
        if self.show_text:
            self._draw_rigel_text(painter, center_x, center_y + self.px // 2 + 5)
    
    def _draw_logo_circle(self, painter, center_x, center_y):
        """Draw the main logo circle with gradient"""
        radius = self.px // 2 - 4
        
        # Create gradient
        gradient = QLinearGradient(center_x - radius, center_y - radius, 
                                  center_x + radius, center_y + radius)
        
        # Rigel Business brand colors
        gradient.setColorAt(0.0, QColor(0, 176, 80))    # Green (#00B050)
        gradient.setColorAt(0.5, QColor(0, 112, 192))    # Blue (#0070C0)
        gradient.setColorAt(1.0, QColor(42, 54, 56))      # Dark (#2A3638)
        
        # Draw outer circle
        painter.setPen(QPen(QColor(42, 54, 56), 2))
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Draw inner circle (white background for text)
        inner_radius = radius - 8
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(center_x - inner_radius, center_y - inner_radius, 
                          inner_radius * 2, inner_radius * 2)
        
        # Draw "R" letter
        self._draw_r_letter(painter, center_x, center_y, inner_radius)
    
    def _draw_r_letter(self, painter, center_x, center_y, radius):
        """Draw the stylized 'R' letter"""
        font_size = int(radius * 0.8)
        font = QFont("Arial", font_size, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(QColor(42, 54, 56), 2))
        
        # Calculate text position
        text_rect = painter.fontMetrics().boundingRect("R")
        text_x = center_x - text_rect.width() // 2
        text_y = center_y + text_rect.height() // 3
        
        painter.drawText(text_x, text_y, "R")
    
    def _draw_rigel_text(self, painter, center_x, y):
        """Draw the 'RIGEL' text below the logo"""
        font_size = max(8, self.px // 6)
        font = QFont("Arial", font_size, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Gradient text effect
        gradient = QLinearGradient(0, y - 10, 0, y + 10)
        gradient.setColorAt(0.0, QColor(0, 176, 80))
        gradient.setColorAt(1.0, QColor(0, 112, 192))
        
        painter.setPen(QPen(QBrush(gradient), 1))
        
        # Draw text
        text = "RIGEL"
        text_rect = painter.fontMetrics().boundingRect(text)
        text_x = center_x - text_rect.width() // 2
        
        painter.drawText(text_x, y, text)
    
    def _animate(self):
        """Animation loop for subtle effects"""
        if not self.animated:
            return
        
        self.animation_phase += 1
        
        # Subtle pulsing effect
        if self.animation_phase % 40 == 0:
            self._opacity = 0.9 if self._opacity == 1.0 else 1.0
            self.update()
    
    @pyqtProperty(float)
    def opacity(self):
        """Property for opacity animation"""
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()

class LogoManager:
    """
    Manager for Rigel Business logo assets and branding
    """
    
    def __init__(self):
        self.logo_dir = Path(__file__).parent
        self.assets_dir = self.logo_dir.parent
        
        # Brand colors
        self.colors = {
            'primary': QColor(0, 176, 80),      # Green (#00B050)
            'secondary': QColor(0, 112, 192),    # Blue (#0070C0)
            'dark': QColor(42, 54, 56),          # Dark (#2A3638)
            'light': QColor(255, 255, 255),      # White
            'accent': QColor(255, 165, 0)         # Orange (#FFA500)
        }
        
        # Application info
        self.app_info = {
            'name': 'RIGEL Business',
            'version': '1.0.0',
            'company': 'Stella Lumen',
            'website': 'www.stella-lumen.com',
            'description': 'Professional Business Accounting Solution'
        }
    
    def get_logo_widget(self, parent=None, size=64, show_text=True, animated=False):
        """Get a logo widget instance"""
        return LogoWidget(parent, size, show_text, animated)
    
    def get_app_icon(self, size=32):
        """Get application icon as QPixmap"""
        # Create a simple icon representation
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw simplified logo for icon
        center = size // 2
        radius = size // 2 - 2
        
        # Background circle
        painter.setPen(QPen(self.colors['dark'], 1))
        painter.setBrush(QBrush(self.colors['primary']))
        painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)
        
        # Draw "R"
        font = QFont("Arial", int(size * 0.4), QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QPen(self.colors['light'], 1))
        
        text_rect = painter.fontMetrics().boundingRect("R")
        text_x = center - text_rect.width() // 2
        text_y = center + text_rect.height() // 3
        
        painter.drawText(text_x, text_y, "R")
        painter.end()
        
        return pixmap
    
    def get_window_icon(self):
        """Get window icon for the application"""
        return self.get_app_icon(32)
    
    def get_taskbar_icon(self):
        """Get taskbar icon"""
        return self.get_app_icon(16)
    
    def get_brand_colors(self):
        """Get brand color palette"""
        return self.colors
    
    def get_app_info(self):
        """Get application information"""
        return self.app_info
    
    def create_logo_variants(self):
        """Create different logo variants for various uses"""
        variants = {}
        
        # Different sizes
        sizes = [16, 24, 32, 48, 64, 128, 256]
        for size in sizes:
            variants[f'icon_{size}'] = self.get_app_icon(size)
        
        # Window icon
        variants['window_icon'] = self.get_window_icon()
        
        # Taskbar icon
        variants['taskbar_icon'] = self.get_taskbar_icon()
        
        return variants
    
    def apply_branding_to_widget(self, widget):
        """Apply Rigel Business branding to a widget"""
        # Apply brand colors to widget stylesheet
        brand_style = f"""
        QWidget {{
            background-color: {self.colors['light'].name()};
            color: {self.colors['dark'].name()};
        }}
        QPushButton {{
            background-color: {self.colors['primary'].name()};
            color: {self.colors['light'].name()};
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {self.colors['secondary'].name()};
        }}
        QLabel {{
            color: {self.colors['dark'].name()};
        }}
        """
        
        widget.setStyleSheet(brand_style)
    
    def get_splash_screen_data(self):
        """Get splash screen data"""
        return {
            'logo': self.get_app_icon(128),
            'title': self.app_info['name'],
            'subtitle': self.app_info['description'],
            'version': f"Version {self.app_info['version']}",
            'company': self.app_info['company'],
            'website': self.app_info['website'],
            'colors': self.colors
        }

# Global logo manager instance
logo_manager = LogoManager()
