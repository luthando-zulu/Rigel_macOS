#!/usr/bin/env python3
"""
RIGEL Business Dashboard with Professional Charts
Dashboard with revenue trends, expense breakdown, cash flow, etc.
"""

import sys
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QProgressBar, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush

# ─────────────────────────────────────────────────────────────────────────────
#  SIMPLE CHART WIDGETS (WITHOUT EXTERNAL DEPENDENCIES)
# ─────────────────────────────────────────────────────────────────────────────
class SimpleLineChart(QFrame):
    """Simple line chart widget"""

    def __init__(self, title: str, data: List[float], labels: List[str] = None):
        super().__init__()
        self.title = title
        self.data = data
        self.labels = labels or [f"Point {i+1}" for i in range(len(data))]
        self.setMinimumSize(300, 200)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)

    def paintEvent(self, event):
        """Draw the line chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Colors
        bg_color = QColor("#F8F9FA")
        line_color = QColor("#00A651")
        grid_color = QColor("#E0E0E0")
        text_color = QColor("#2C3E50")

        # Fill background
        painter.fillRect(self.rect(), bg_color)

        # Draw title
        painter.setPen(text_color)
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_rect = painter.boundingRect(self.rect(), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)
        painter.drawText(self.rect().adjusted(0, 10, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)

        if not self.data:
            return

        # Chart area
        margin = 60
        chart_rect = self.rect().adjusted(margin, 60, -margin, -margin)

        # Calculate scales
        max_value = max(self.data) if self.data else 1
        min_value = min(self.data) if self.data else 0
        value_range = max_value - min_value or 1

        # Draw grid and labels
        painter.setPen(grid_color)
        painter.setFont(QFont("Segoe UI", 8))

        # Y-axis labels and grid
        for i in range(5):
            y_value = min_value + (value_range * i / 4)
            y_pos = chart_rect.bottom() - (chart_rect.height() * i / 4)

            # Grid line
            painter.drawLine(chart_rect.left(), int(y_pos), chart_rect.right(), int(y_pos))

            # Label
            label = f"R{y_value:,.0f}"
            painter.drawText(chart_rect.left() - 50, int(y_pos + 5), label)

        # X-axis labels
        for i, label in enumerate(self.labels):
            if i < len(self.labels):
                x_pos = chart_rect.left() + (chart_rect.width() * i / max(1, len(self.labels) - 1))
                painter.drawText(int(x_pos - 20), chart_rect.bottom() + 20, label[:8])  # Truncate long labels

        # Draw line
        painter.setPen(QPen(line_color, 3, Qt.PenStyle.SolidLine))
        points = []

        for i, value in enumerate(self.data):
            x = chart_rect.left() + (chart_rect.width() * i / max(1, len(self.data) - 1))
            y = chart_rect.bottom() - (chart_rect.height() * (value - min_value) / value_range)
            points.append((x, y))

        # Draw lines between points
        for i in range(1, len(points)):
            painter.drawLine(int(points[i-1][0]), int(points[i-1][1]),
                          int(points[i][0]), int(points[i][1]))

        # Draw points
        painter.setBrush(QBrush(line_color))
        for x, y in points:
            painter.drawEllipse(int(x - 4), int(y - 4), 8, 8)

class SimpleBarChart(QFrame):
    """Simple bar chart widget"""

    def __init__(self, title: str, data: Dict[str, float]):
        super().__init__()
        self.title = title
        self.data = data
        self.setMinimumSize(300, 200)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)

    def paintEvent(self, event):
        """Draw the bar chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Colors
        bg_color = QColor("#F8F9FA")
        bar_color = QColor("#3498DB")
        grid_color = QColor("#E0E0E0")
        text_color = QColor("#2C3E50")

        # Fill background
        painter.fillRect(self.rect(), bg_color)

        # Draw title
        painter.setPen(text_color)
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_rect = painter.boundingRect(self.rect(), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)
        painter.drawText(self.rect().adjusted(0, 10, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)

        if not self.data:
            return

        # Chart area
        margin = 60
        chart_rect = self.rect().adjusted(margin, 60, -margin, -margin)

        # Calculate scale
        max_value = max(self.data.values()) if self.data else 1

        # Draw bars
        bar_width = chart_rect.width() / len(self.data) * 0.8
        spacing = chart_rect.width() / len(self.data) * 0.2

        painter.setFont(QFont("Segoe UI", 8))

        for i, (label, value) in enumerate(self.data.items()):
            # Bar position
            x = chart_rect.left() + i * (bar_width + spacing)
            bar_height = (value / max_value) * chart_rect.height()
            y = chart_rect.bottom() - bar_height

            # Draw bar
            painter.setBrush(QBrush(bar_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))

            # Draw value on top of bar
            painter.setPen(text_color)
            value_text = f"R{value:,.0f}"
            value_rect = painter.boundingRect(0, 0, int(bar_width), 20, Qt.AlignmentFlag.AlignCenter, value_text)
            painter.drawText(int(x + bar_width/2 - value_rect.width()/2), int(y - 5), value_text)

            # Draw label
            label_rect = painter.boundingRect(0, 0, int(bar_width), 20, Qt.AlignmentFlag.AlignCenter, label[:10])
            painter.drawText(int(x + bar_width/2 - label_rect.width()/2), chart_rect.bottom() + 15, label[:10])

class SimplePieChart(QFrame):
    """Simple pie chart widget"""

    def __init__(self, title: str, data: Dict[str, float]):
        super().__init__()
        self.title = title
        self.data = data
        self.colors = [
            QColor("#00A651"), QColor("#3498DB"), QColor("#E74C3C"),
            QColor("#9B59B6"), QColor("#E67E22"), QColor("#1ABC9C")
        ]
        self.setMinimumSize(300, 200)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)

    def paintEvent(self, event):
        """Draw the pie chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Colors
        bg_color = QColor("#F8F9FA")
        text_color = QColor("#2C3E50")

        # Fill background
        painter.fillRect(self.rect(), bg_color)

        # Draw title
        painter.setPen(text_color)
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_rect = painter.boundingRect(self.rect(), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)
        painter.drawText(self.rect().adjusted(0, 10, 0, 0), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)

        if not self.data:
            return

        # Chart area
        margin = 40
        chart_rect = self.rect().adjusted(margin, 60, -margin, -margin)
        center = chart_rect.center()
        radius = min(chart_rect.width(), chart_rect.height()) / 2

        # Calculate total
        total = sum(self.data.values())
        if total == 0:
            return

        # Draw pie slices
        start_angle = 0
        legend_y = chart_rect.top()

        for i, (label, value) in enumerate(self.data.items()):
            # Calculate angle
            angle = (value / total) * 360
            color = self.colors[i % len(self.colors)]

            # Draw slice
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPie(center.x() - radius, center.y() - radius,
                          radius * 2, radius * 2, int(start_angle * 16), int(angle * 16))

            # Draw legend
            painter.setBrush(QBrush(color))
            painter.drawRect(chart_rect.right() - 150, legend_y, 15, 15)

            painter.setPen(text_color)
            painter.setFont(QFont("Segoe UI", 9))
            legend_text = f"{label}: R{value:,.0f} ({value/total*100:.1f}%)"
            painter.drawText(chart_rect.right() - 130, legend_y + 12, legend_text)

            legend_y += 20
            start_angle += angle

# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD WIDGETS
# ─────────────────────────────────────────────────────────────────────────────
class DashboardCard(QGroupBox):
    """Dashboard metric card"""

    def __init__(self, title: str, value: str, subtitle: str = "", icon: str = ""):
        super().__init__(title)
        self.setup_ui(value, subtitle, icon)

    def setup_ui(self, value: str, subtitle: str, icon: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Icon and value row
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)

        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px;")
            top_layout.addWidget(icon_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #00A651;
        """)
        top_layout.addWidget(value_label)
        top_layout.addStretch()

        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("""
                font-size: 12px;
                color: #6A7575;
            """)
            layout.addWidget(subtitle_label)

        layout.addLayout(top_layout)

        # Styling
        self.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: #2C3E50;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px 0 5px;
            }
        """)

class RecentTransactionsTable(QGroupBox):
    """Recent transactions table"""

    def __init__(self):
        super().__init__("Recent Transactions")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Description", "Amount", "Type"])
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
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

        # Sample data
        sample_data = [
            ["2024-01-15", "Office Supplies", "R 2,500.00", "Expense"],
            ["2024-01-14", "Client Payment", "R 15,000.00", "Income"],
            ["2024-01-13", "Bank Charges", "R 150.00", "Expense"],
            ["2024-01-12", "Equipment Purchase", "R 25,000.00", "Asset"],
            ["2024-01-11", "Consulting Services", "R 8,000.00", "Income"]
        ]

        self.table.setRowCount(len(sample_data))
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                self.table.setItem(row, col, QTableWidgetItem(value))

        self.table.resizeColumnsToContents()
        layout.addWidget(self.table)

        self.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: #2C3E50;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px 0 5px;
            }
        """)

# ─────────────────────────────────────────────────────────────────────────────
#  DASHBOARD MAIN WIDGET
# ─────────────────────────────────────────────────────────────────────────────
class DashboardWidget(QWidget):
    """Main dashboard with charts and metrics"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_dashboard_data()

    def setup_ui(self):
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2C3E50;
        """)

        subtitle = QLabel("Business overview and key metrics")
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #6A7575;
        """)

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)

        # Metrics cards row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)

        self.revenue_card = DashboardCard("Total Revenue", "R 450,000", "This month", "💰")
        self.expenses_card = DashboardCard("Total Expenses", "R 320,000", "This month", "💸")
        self.profit_card = DashboardCard("Net Profit", "R 130,000", "This month", "📈")
        self.cash_card = DashboardCard("Cash Balance", "R 85,000", "Current", "🏦")

        metrics_layout.addWidget(self.revenue_card)
        metrics_layout.addWidget(self.expenses_card)
        metrics_layout.addWidget(self.profit_card)
        metrics_layout.addWidget(self.cash_card)

        content_layout.addLayout(metrics_layout)

        # Charts row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        # Revenue trend chart
        self.revenue_chart = SimpleLineChart(
            "Revenue Trend (Last 6 Months)",
            [350000, 380000, 420000, 390000, 450000, 450000],
            ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        )

        # Expense breakdown chart
        self.expenses_chart = SimplePieChart(
            "Expense Breakdown",
            {
                "Salaries": 150000,
                "Rent": 25000,
                "Supplies": 35000,
                "Marketing": 20000,
                "Utilities": 15000,
                "Other": 75000
            }
        )

        charts_layout.addWidget(self.revenue_chart)
        charts_layout.addWidget(self.expenses_chart)

        content_layout.addLayout(charts_layout)

        # Bottom row - Cash flow and recent transactions
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)

        # Cash flow chart
        self.cash_flow_chart = SimpleBarChart(
            "Cash Flow Analysis",
            {
                "Operating": 120000,
                "Investing": -50000,
                "Financing": 100000
            }
        )

        # Recent transactions
        self.recent_transactions = RecentTransactionsTable()

        bottom_layout.addWidget(self.cash_flow_chart)
        bottom_layout.addWidget(self.recent_transactions)

        content_layout.addLayout(bottom_layout)

        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def load_dashboard_data(self):
        """Load dashboard data (placeholder for real data)"""
        # In a real implementation, this would load data from the database
        # For now, we'll use the sample data already set up

        # Update metrics with "real-time" data
        self.update_metrics()

        # Set up auto-refresh timer (optional)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_metrics)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def update_metrics(self):
        """Update dashboard metrics"""
        # Simulate some variation in metrics
        base_revenue = 450000
        base_expenses = 320000

        # Add some random variation
        revenue_variation = random.randint(-5000, 5000)
        expense_variation = random.randint(-3000, 3000)

        revenue = base_revenue + revenue_variation
        expenses = base_expenses + expense_variation
        profit = revenue - expenses

        self.revenue_card.layout().itemAt(0).layout().itemAt(1).widget().setText(f"R {revenue:,}")
        self.expenses_card.layout().itemAt(0).layout().itemAt(1).widget().setText(f"R {expenses:,}")
        self.profit_card.layout().itemAt(0).layout().itemAt(1).widget().setText(f"R {profit:,}")

        # Update profit/loss color
        profit_color = "#27AE60" if profit >= 0 else "#E74C3C"
        self.profit_card.layout().itemAt(0).layout().itemAt(1).widget().setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {profit_color};
        """)

# ─────────────────────────────────────────────────────────────────────────────
#  INTEGRATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────
def create_dashboard() -> DashboardWidget:
    """Factory function to create dashboard"""
    return DashboardWidget()

if __name__ == "__main__":
    # Test the dashboard
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dashboard = create_dashboard()
    dashboard.show()

    sys.exit(app.exec())