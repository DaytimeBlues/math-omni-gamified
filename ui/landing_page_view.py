"""
Year 1 Curriculum Landing Page - ACARA v9.0 Aligned
Merged Edition: High-Fidelity UI (StudioAI) + Performance Optimizations (Z.ai)
"""
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QSize
)
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient, QPixmap
from config import (
    FONT_FAMILY, COLORS, BUTTON_GAP
)
# Import the new utility
from ui.premium_utils import add_soft_shadow

# =============================================================================
# DOMAIN CONFIGURATION (ACARA Year 1)
# =============================================================================
DOMAIN_CONFIG = {
    "number": {
        "title": "Number Explorer",
        "icon": "🔢",
        "subtitle": "Numbers to 120 • Addition & Subtraction",
        "color_primary": "#FF9F43",    # Mango Pop
        "color_secondary": "#E67E22",  # Deep Mango
        "color_accent": "#FFF4E6",     # Light Mango
    },
    "patterns": {
        "title": "Pattern Wizard",
        "icon": "🔮",
        "subtitle": "Skip Counting • Repeating Patterns",
        "color_primary": "#A29BFE",    # Soft Purple
        "color_secondary": "#6C5CE7",  # Deep Purple
        "color_accent": "#F3F1FF",     # Light Purple
    },
    "measurement": {
        "title": "Measurement Giant",
        "icon": "📏",
        "subtitle": "Length • Mass • Capacity • Time",
        "color_primary": "#00B894",    # Mint Leaf
        "color_secondary": "#009E77",  # Deep Mint
        "color_accent": "#E8FBF5",     # Light Mint
    },
    "data": {
        "title": "Space & Data Detective",
        "icon": "🔍",
        "subtitle": "Shapes • Directions • Data Tables",
        "color_primary": "#48DBFB",    # Soft Sky
        "color_secondary": "#0ABDE3",  # Ocean Depth
        "color_accent": "#E8F8FD",     # Light Sky
    },
}

# =============================================================================
# STYLES
# =============================================================================
HEADER_CARD_STYLE = """
    QFrame#HeaderCard {
        background-color: #FFFEF8;
        border-radius: 20px;
    }
"""
EGG_COUNTER_STYLE = """
    QFrame#EggCounter {
        background-color: #FFF8E0;
        border: 3px solid #FFB347;
        border-radius: 25px;
    }
"""

class DomainCard(QFrame):
    """
    Interactive domain card with progress indicator and elastic hover animation.
    """
    
    clicked = pyqtSignal(str)  # Emits domain key
    _icon_cache: Dict[str, QPixmap] = {}

    @staticmethod
    def _render_icon(icon: str, size: int = 64) -> QPixmap:
        """Pre-render an emoji icon into a cached QPixmap."""
        cache_key = f"{icon}_{size}"
        if cache_key in DomainCard._icon_cache:
            return DomainCard._icon_cache[cache_key]
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = QFont("Segoe UI Emoji", int(size * 0.7))
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, icon)
        painter.end()
        
        DomainCard._icon_cache[cache_key] = pixmap
        return pixmap
    
    def __init__(self, domain_key: str, parent=None):
        super().__init__(parent)
        self.domain_key = domain_key
        self.config = DOMAIN_CONFIG[domain_key]
        self._progress = 0  # 0-100
        self._hovered = False
        self._original_geometry = None
        
        self.setObjectName(f"DomainCard_{domain_key}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(220, 260)
        self.setMaximumSize(280, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self._build_ui()
        self._apply_style()
        self._setup_animations()
        
        # Add premium shadow
        add_soft_shadow(self, blur=25, offset_y=10, opacity=35)
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # Icon
        self.icon_label = QLabel()
        self.icon_label.setPixmap(self._render_icon(self.config["icon"], 80))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.icon_label)
        
        # Title
        self.title_label = QLabel(self.config["title"])
        self.title_label.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel(self.config["subtitle"])
        self.subtitle_label.setFont(QFont(FONT_FAMILY, 11))
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet(f"color: {COLORS.get('text_light', '#666')}; background: transparent;")
        layout.addWidget(self.subtitle_label)
        
        layout.addStretch()
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)
        self._style_progress_bar()
        layout.addWidget(self.progress_bar)
        
        # Progress Label
        self.progress_label = QLabel("0% Complete")
        self.progress_label.setFont(QFont(FONT_FAMILY, 10))
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet(f"color: {COLORS.get('text_light', '#666')}; background: transparent;")
        layout.addWidget(self.progress_label)
    
    def _style_progress_bar(self):
        primary = self.config["color_primary"]
        secondary = self.config["color_secondary"]
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #E8E8E8;
                border: none;
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {secondary},
                    stop:1 {primary}
                );
                border-radius: 6px;
            }}
        """)
    
    def _apply_style(self):
        accent = self.config["color_accent"]
        primary = self.config["color_primary"]
        
        self.setStyleSheet(f"""
            QFrame#DomainCard_{self.domain_key} {{
                background-color: {accent};
                border: 3px solid {primary};
                border-radius: 25px;
            }}
        """)
        self.title_label.setStyleSheet(f"color: {self.config['color_secondary']}; background: transparent;")
    
    def _setup_animations(self):
        self._hover_animation = QPropertyAnimation(self, b"geometry")
        self._hover_animation.setDuration(200)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutElastic)
    
    def set_progress(self, value: int):
        self._progress = max(0, min(100, value))
        self.progress_bar.setValue(self._progress)
        self.progress_label.setText(f"{self._progress}% Complete")
    
    def enterEvent(self, event):
        super().enterEvent(event)
        self._hovered = True
        if self._original_geometry is None:
            self._original_geometry = self.geometry()
        
        current = self.geometry()
        expanded = current.adjusted(-6, -6, 6, 6)
        
        self._hover_animation.stop()
        self._hover_animation.setStartValue(current)
        self._hover_animation.setEndValue(expanded)
        self._hover_animation.start()
        
        # Intensify shadow
        add_soft_shadow(self, blur=35, offset_y=15, opacity=45)
    
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hovered = False
        if self._original_geometry:
            current = self.geometry()
            self._hover_animation.stop()
            self._hover_animation.setStartValue(current)
            self._hover_animation.setEndValue(self._original_geometry)
            self._hover_animation.start()
        
        # Reset shadow
        add_soft_shadow(self, blur=25, offset_y=10, opacity=35)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.domain_key)
        super().mousePressEvent(event)
        
    def cleanup(self):
        try:
            self.clicked.disconnect()
        except:
            pass
        self.deleteLater()

class LandingPageView(QWidget):
    """
    Year 1 Curriculum Landing Page - Main Navigation Hub.
    """
    domain_selected = pyqtSignal(str)
    
    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self._domain_cards = {}
        self._eggs = 0
        self._build_ui()
    
    def _build_ui(self):
        self.setAutoFillBackground(False)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # --- HEADER ---
        header = self._build_header()
        layout.addLayout(header)
        
        # --- INSTRUCTIONS ---
        instructions = QLabel("Choose your learning adventure!")
        instructions.setFont(QFont(FONT_FAMILY, 22))
        instructions.setStyleSheet(f"color: {COLORS.get('text_light', '#555')}; background: transparent;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        layout.addSpacing(10)
        
        # --- DOMAIN GRID ---
        grid_container = self._build_domain_grid()
        layout.addWidget(grid_container, stretch=1, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
    
    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(20)
        
        # Title Card
        title_card = QFrame()
        title_card.setObjectName("HeaderCard")
        title_card.setStyleSheet(HEADER_CARD_STYLE)
        add_soft_shadow(title_card, blur=20, offset_y=6, opacity=20)
        
        title_layout = QHBoxLayout(title_card)
        title_layout.setContentsMargins(20, 10, 20, 10)
        
        title_icon = QLabel("🎓")
        title_icon.setFont(QFont("Segoe UI Emoji", 28))
        title_icon.setStyleSheet("background: transparent;")
        
        title_text = QLabel("Year 1 Math Adventure")
        title_text.setFont(QFont(FONT_FAMILY, 26, QFont.Weight.Bold))
        title_text.setStyleSheet(f"color: {COLORS.get('text', '#333')}; background: transparent;")
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        
        header.addWidget(title_card)
        header.addStretch()
        
        # Egg Counter
        egg_frame = QFrame()
        egg_frame.setObjectName("EggCounter")
        egg_frame.setStyleSheet(EGG_COUNTER_STYLE)
        egg_frame.setFixedHeight(50)
        add_soft_shadow(egg_frame, blur=12, offset_y=3, opacity=20)
        
        egg_layout = QHBoxLayout(egg_frame)
        egg_layout.setContentsMargins(15, 5, 20, 5)
        egg_layout.setSpacing(10)
        
        egg_icon = QLabel("🥚")
        egg_icon.setFont(QFont("Segoe UI Emoji", 24))
        egg_icon.setStyleSheet("background: transparent; border: none;")
        
        self.egg_label = QLabel("0 eggs")
        self.egg_label.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        self.egg_label.setStyleSheet(f"color: {COLORS.get('text', '#333')}; background: transparent; border: none;")
        
        egg_layout.addWidget(egg_icon)
        egg_layout.addWidget(self.egg_label)
        
        header.addWidget(egg_frame)
        return header
    
    def _build_domain_grid(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container.setMinimumSize(500, 500)
        
        grid = QGridLayout(container)
        grid.setSpacing(BUTTON_GAP)
        grid.setContentsMargins(20, 20, 20, 20)
        
        domains = ["number", "patterns", "measurement", "data"]
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for domain, pos in zip(domains, positions):
            card = DomainCard(domain)
            card.clicked.connect(self._on_domain_clicked)
            self._domain_cards[domain] = card
            grid.addWidget(card, pos[0], pos[1])
        
        return container
    
    def _on_domain_clicked(self, domain_key: str):
        self.domain_selected.emit(domain_key)
    
    def refresh(self, egg_count: int):
        """Refresh the landing page with current progress data (Synchronous)."""
        self._eggs = egg_count
        self.egg_label.setText(f"{egg_count} eggs")
        self._load_domain_progress()
    
    def _load_domain_progress(self):
        """Load and display progress for each domain from profile."""
        try:
            from core.user_profile import StudentProfile
            profile = StudentProfile.load()
            
            domain_progress_map = {
                "number": (profile.progress.get("counting", 0) + 
                           profile.progress.get("addition", 0) +
                           profile.progress.get("subtraction", 0)) * 2.0,
                "patterns": profile.progress.get("patterns", 0) * 10,
                "measurement": profile.progress.get("measurement", 0) * 10,
                "data": profile.progress.get("data", 0) * 10,
            }
            
            for domain, progress in domain_progress_map.items():
                if domain in self._domain_cards:
                    self._domain_cards[domain].set_progress(int(min(100, max(0, progress))))
        except Exception as e:
            print(f"[LandingPageView] Warning loading progress: {e}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#FEF9E7"))
        gradient.setColorAt(0.5, QColor("#FAF0DC"))
        gradient.setColorAt(1.0, QColor("#F5E6C8"))
        
        painter.fillRect(self.rect(), gradient)
