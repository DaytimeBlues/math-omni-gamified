"""
Progress Report UI Component
Display student progress reports in a child-friendly, visual format
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QScrollArea, QFrame,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QTextEdit, QGridLayout, QGroupBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient
import json
from datetime import datetime
from typing import Dict, List
import math

# Integration with app design tokens
from ui.design_tokens import COLORS, FONT_FAMILY

print(f"[progress_report_view.py] ENTRY: Initializing Progress Report View")

class ProgressReportView(QWidget):
    """Main widget for displaying progress reports"""
    
    report_generated = pyqtSignal(dict)  # Signal when report is generated
    
    def __init__(self, profile, parent=None):
        print(f"[ProgressReportView.__init__] ENTRY: profile={profile.name if profile else 'None'}")
        super().__init__(parent)
        
        self.profile = profile
        self.report_generator = None  # Will be set from outside
        self.current_report = None
        
        print(f"[ProgressReportView.__init__] CALC: Setting up UI components")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface"""
        print(f"[ProgressReportView.setup_ui] ENTRY")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        name = self.profile.name if self.profile else "Student"
        self.title_label = QLabel(f"Progress Report: {name}")
        title_font = QFont(FONT_FAMILY, 18, QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {COLORS['primary']};")
        
        self.date_label = QLabel(datetime.now().strftime("%B %d, %Y"))
        self.date_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 14px;")
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.date_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.daily_btn = self._create_report_button("📊 Daily View", "daily")
        self.weekly_btn = self._create_report_button("📈 Weekly View", "weekly")
        self.skills_btn = self._create_report_button("🎯 Skills", "skills")
        self.save_btn = self._create_report_button("💾 Save", "save")
        self.print_btn = self._create_report_button("🖨️ Print", "print")
        
        button_layout.addWidget(self.daily_btn)
        button_layout.addWidget(self.weekly_btn)
        button_layout.addWidget(self.skills_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.print_btn)
        
        # Tab widget for different report views
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setStyleSheet(f"QTabWidget::pane {{ border: 1px solid {COLORS['locked']}; border-radius: 5px; }}")
        
        # Create tabs
        self.summary_tab = SummaryTab()
        self.details_tab = DetailsTab()
        self.skills_tab = SkillsTab()
        self.history_tab = HistoryTab()
        
        self.tab_widget.addTab(self.summary_tab, "📋 Summary")
        self.tab_widget.addTab(self.details_tab, "🔍 Details")
        self.tab_widget.addTab(self.skills_tab, "🎯 Skills")
        self.tab_widget.addTab(self.history_tab, "📊 History")
        
        # Add to main layout
        main_layout.addLayout(header_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tab_widget, 1)
        
        print(f"[ProgressReportView.setup_ui] COMPLETE: UI with {self.tab_widget.count()} tabs created")
        
    def _create_report_button(self, text: str, report_type: str) -> QPushButton:
        """Create a styled report button"""
        from ui.design_tokens import STYLES
        
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setMinimumWidth(120)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Styling based on button type
        if report_type in ["daily", "weekly", "skills"]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border-radius: 8px;
                    border-bottom: 4px solid {COLORS['primary_shadow']};
                    font-weight: bold;
                    padding: 8px;
                }}
                QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}
                QPushButton:pressed {{ border-bottom: 0px; margin-top: 4px; }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['success']};
                    color: white;
                    border-radius: 8px;
                    border-bottom: 4px solid {COLORS['success_dark']};
                    font-weight: bold;
                    padding: 8px;
                }}
                QPushButton:hover {{ background-color: #55E6C1; }}
                QPushButton:pressed {{ border-bottom: 0px; margin-top: 4px; }}
            """)
        
        # Connect signals
        if report_type == "daily":
            btn.clicked.connect(self.generate_daily_report)
        elif report_type == "weekly":
            btn.clicked.connect(self.generate_weekly_report)
        elif report_type == "skills":
            btn.clicked.connect(self.generate_skills_report)
        elif report_type == "save":
            btn.clicked.connect(self.save_current_report)
        elif report_type == "print":
            btn.clicked.connect(self.print_report)
        
        return btn
    
    def generate_daily_report(self):
        """Generate and display daily report"""
        if not self.report_generator: return
        try:
            self.current_report = self.report_generator.generate_daily_report()
            self.update_display(self.current_report)
        except Exception as e: print(f"[ProgressReportView] ERROR: {e}")
    
    def generate_weekly_report(self):
        """Generate and display weekly report"""
        if not self.report_generator: return
        try:
            self.current_report = self.report_generator.generate_weekly_report()
            self.update_display(self.current_report)
        except Exception as e: print(f"[ProgressReportView] ERROR: {e}")
    
    def generate_skills_report(self):
        """Generate and display skills breakdown report"""
        if not self.report_generator: return
        try:
            self.current_report = self.report_generator.generate_skill_breakdown_report()
            self.update_display(self.current_report)
        except Exception as e: print(f"[ProgressReportView] ERROR: {e}")
    
    def update_display(self, report: Dict):
        """Update all tabs with report data"""
        report_type = report.get('report_type', '').replace('_', ' ').title()
        name = self.profile.name if self.profile else "Student"
        self.title_label.setText(f"Progress Report: {name} - {report_type}")
        
        self.summary_tab.update_data(report)
        self.details_tab.update_data(report)
        self.skills_tab.update_data(report)
        self.history_tab.update_data(report)
        
        self.report_generated.emit(report)
    
    def save_current_report(self):
        """Save the current report to file"""
        if not self.current_report or not self.report_generator: return
        try:
            report_type = self.current_report.get('report_type', 'unknown')
            filepath = self.report_generator.save_report(self.current_report, report_type)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Report Saved", f"Report saved to:\n{filepath}")
        except Exception as e: print(f"[ProgressReportView] ERROR: {e}")
    
    def print_report(self):
        """Print the current report (simulated)"""
        if not self.current_report: return
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Print", "Print functionality ready. Please connect a printer.")

class SummaryTab(QWidget):
    """Tab showing summary overview"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Summary cards container
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(20)
        
        self.card_accuracy = self._create_summary_card("🎯 Accuracy", "0%", COLORS['primary'])
        self.card_time = self._create_summary_card("⏱️ Time", "0 min", COLORS['secondary'])
        self.card_eggs = self._create_summary_card("🥚 Eggs", "0", COLORS['accent'])
        self.card_level = self._create_summary_card("📈 Level", "Level 1", COLORS['error'])
        
        self.cards_layout.addWidget(self.card_accuracy)
        self.cards_layout.addWidget(self.card_time)
        self.cards_layout.addWidget(self.card_eggs)
        self.cards_layout.addWidget(self.card_level)
        self.cards_layout.addStretch()
        
        # Recommendations section
        recommendations_group = QGroupBox("🌟 Recommendations")
        recommendations_group.setStyleSheet(f"QGroupBox {{ font-weight: bold; border: 2px solid {COLORS['secondary']}; border-radius: 8px; margin-top: 10px; padding-top: 10px; }}")
        
        rec_layout = QVBoxLayout()
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        self.recommendations_text.setMaximumHeight(150)
        self.recommendations_text.setStyleSheet(f"background-color: {COLORS['canvas']}; border: none;")
        
        rec_layout.addWidget(self.recommendations_text)
        recommendations_group.setLayout(rec_layout)
        
        layout.addLayout(self.cards_layout)
        layout.addWidget(recommendations_group, 1)
    
    def _create_summary_card(self, title: str, value: str, color: str) -> QFrame:
        card = QFrame()
        card.setFixedSize(180, 120)
        card.setStyleSheet(f"QFrame {{ background-color: white; border: 2px solid {color}; border-radius: 10px; padding: 15px; }}")
        
        card_layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {color};")
        
        value_label = QLabel(value)
        value_label.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {COLORS['text']};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if "Accuracy" in title: self.accuracy_value = value_label
        elif "Time" in title: self.time_value = value_label
        elif "Eggs" in title: self.eggs_value = value_label
        elif "Level" in title: self.level_value = value_label
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label, 1, Qt.AlignmentFlag.AlignCenter)
        return card
    
    def update_data(self, report: Dict):
        try:
            metrics = report.get('metrics', {})
            accuracy = metrics.get('accuracy_rate', 0)
            self.accuracy_value.setText(f"{accuracy:.1%}")
            self.time_value.setText(f"{int(metrics.get('time_spent_minutes', 0))} min")
            self.eggs_value.setText(f"{report.get('total_eggs', 0)}")
            self.level_value.setText(f"Level {report.get('current_level', 1)}")
            
            recs = report.get('recommendations', [])
            self.recommendations_text.setText("\n".join([f"• {r}" for r in recs]) if recs else "Keep practicing!")
        except Exception as e: print(f"[SummaryTab] ERROR: {e}")

class DetailsTab(QWidget):
    """Tab showing detailed metrics and error analysis"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        self.metrics_table = QTableWidget(0, 2)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        content_layout.addWidget(QLabel("📊 Detailed Metrics"))
        content_layout.addWidget(self.metrics_table)
        
        self.error_text = QTextEdit()
        self.error_text.setReadOnly(True)
        content_layout.addWidget(QLabel("🔍 Common Errors"))
        content_layout.addWidget(self.error_text)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def update_data(self, report: Dict):
        metrics = report.get('metrics', {})
        self.metrics_table.setRowCount(len(metrics))
        for i, (k, v) in enumerate(metrics.items()):
            self.metrics_table.setItem(i, 0, QTableWidgetItem(k.replace('_', ' ').title()))
            self.metrics_table.setItem(i, 1, QTableWidgetItem(f"{v:.1%}" if 'rate' in k else str(v)))
        
        errors = report.get('top_3_errors', [])
        self.error_text.setText("\n".join([f"• {e['pattern']} ({e['count']}x)" for e in errors]))

class SkillsTab(QWidget):
    """Tab showing skill breakdown and mastery"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.skills_vbox = QVBoxLayout()
        layout.addLayout(self.skills_vbox)
        layout.addStretch()
        
    def update_data(self, report: Dict):
        # Clear old widgets
        while self.skills_vbox.count():
            child = self.skills_vbox.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        skills = report.get('skill_analysis', {})
        for skill, perf in [("Counting", skills.get('counting_performance', 0)),
                            ("Addition", skills.get('addition_performance', 0)),
                            ("Subtraction", skills.get('subtraction_performance', 0))]:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.addWidget(QLabel(f"<b>{skill}</b>"))
            bar = SkillProgressBar(COLORS['primary'] if skill=="Counting" else COLORS['secondary'])
            bar.setProgress(perf)
            row_layout.addWidget(bar, 1)
            row_layout.addWidget(QLabel(f"{perf:.0%}"))
            self.skills_vbox.addWidget(row)

class SkillProgressBar(QWidget):
    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self.progress = 0.0
        self.color = color
        self.setFixedHeight(24)
        
    def setProgress(self, p): self.progress = p; self.update()
    
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor("#F0F0F0")))
        painter.drawRoundedRect(self.rect(), 12, 12)
        if self.progress > 0:
            painter.setBrush(QBrush(QColor(self.color)))
            r = self.rect()
            r.setWidth(int(r.width() * self.progress))
            painter.drawRoundedRect(r, 12, 12)

class HistoryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.list = QTextEdit(); self.list.setReadOnly(True)
        layout.addWidget(QLabel("📁 Recent Reports"))
        layout.addWidget(self.list)
    def update_data(self, r): pass
