"""
Premium Map View - Level Selection UI

Claude's Implementation matching reference design:
- Cream gradient background
- Premium level buttons with shadows
- Pill-shaped egg counter
- Generous whitespace
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QIcon
from ui.practice_dialog import PracticeDialog

from config import (
    MIN_TOUCH_TARGET, BUTTON_GAP, MAP_LEVELS_COUNT,
    FONT_FAMILY, FONT_SIZE_BODY, FONT_SIZE_HEADING, COLORS
)


# =============================================================================
# PREMIUM STYLES
# =============================================================================

PREMIUM_BG = """
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #FEF9E7,
        stop:0.5 #FAF0DC,
        stop:1 #F5E6C8
    );
"""

HEADER_CARD_STYLE = """
    QFrame#HeaderCard {
        background-color: #FFFEF8;
        border-radius: 20px;
        padding: 15px 25px;
    }
"""

EGG_COUNTER_STYLE = """
    QFrame#EggCounter {
        background-color: #FFF8E0;
        border: 3px solid #FFB347;
        border-radius: 25px;
    }
"""


def add_soft_shadow(widget, blur=25, offset_y=8, opacity=30):
    """Add a soft, premium drop shadow."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(0, 0, 0, opacity))
    shadow.setOffset(0, offset_y)
    widget.setGraphicsEffect(shadow)


class PremiumLevelButton(QPushButton):
    """
    A premium level button with 3D effect and shadow.
    """
    
    def __init__(self, level: int, parent=None):
        super().__init__(str(level), parent)
        self.level = level
        self._unlocked = False
        
        self.setFixedSize(100, 100)
        self.setFont(QFont(FONT_FAMILY, 28, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._apply_locked_style()
    
    def _apply_unlocked_style(self):
        """Bright, inviting style for unlocked levels."""
        self.setStyleSheet("""
            QPushButton {
                background-color: #00C897;
                color: white;
                border: none;
                border-bottom: 6px solid #009E77;
                border-radius: 50px;
            }
            QPushButton:hover {
                background-color: #1AD8A7;
            }
            QPushButton:pressed {
                background-color: #009E77;
                border-bottom: 2px solid #009E77;
            }
        """)
        add_soft_shadow(self, blur=20, offset_y=6, opacity=35)
    
    def _apply_locked_style(self):
        """Muted style for locked levels."""
        self.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #9E9E9E;
                border: none;
                border-bottom: 6px solid #BDBDBD;
                border-radius: 50px;
            }
        """)
        # Lighter shadow for locked
        add_soft_shadow(self, blur=10, offset_y=4, opacity=15)
    
    def set_unlocked(self, unlocked: bool):
        """Set the unlock state."""
        self._unlocked = unlocked
        if unlocked:
            self._apply_unlocked_style()
            self.setEnabled(True)
        else:
            self._apply_locked_style()
            self.setEnabled(False)


class PremiumMapView(QWidget):
    """
    Premium Map View with gradient background and chunky level buttons.
    
    Layout:
    ┌────────────────────────────────────────┐
    │  ┌─────────────────────┐    🥚 90     │  Header
    │  │ 🗺️ Counting Adventure│              │
    │  └─────────────────────┘              │
    ├────────────────────────────────────────┤
    │         Tap a level to play!           │
    │                                        │
    │    [1]  [2]  [3]  [4]  [5]             │
    │                                        │
    │    [6]  [7]  [8]  [9]  [10]            │
    │                                        │
    └────────────────────────────────────────┘
    """
    
    level_selected = pyqtSignal(int)
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self._level_buttons = []
        self._build_ui()
    
    def _build_ui(self):
        """Build the premium map UI."""
        self.setStyleSheet(PREMIUM_BG)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(35)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # --- HEADER ---
        header = self._build_header()
        layout.addLayout(header)
        
        # --- INSTRUCTIONS ---
        instructions = QLabel("Tap a level to start counting!")
        instructions.setFont(QFont(FONT_FAMILY, 20))
        instructions.setStyleSheet(f"color: {COLORS['text_light']}; background: transparent;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
        
        layout.addSpacing(20)
        
        # --- LEVEL GRID ---
        levels_widget = self._build_level_grid()
        layout.addWidget(levels_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
    
    def _build_header(self) -> QHBoxLayout:
        """Build header with title card and egg counter."""
        header = QHBoxLayout()
        header.setSpacing(20)
        
        # Title Card
        title_card = QFrame()
        title_card.setObjectName("HeaderCard")
        title_card.setStyleSheet(HEADER_CARD_STYLE)
        add_soft_shadow(title_card, blur=20, offset_y=6, opacity=20)
        
        title_layout = QHBoxLayout(title_card)
        title_layout.setContentsMargins(20, 10, 20, 10)
        
        map_icon = QLabel("🗺️")
        map_icon.setFont(QFont("Segoe UI Emoji", 28))
        map_icon.setStyleSheet("background: transparent;")
        
        title_text = QLabel("Counting Adventure")
        title_text.setFont(QFont(FONT_FAMILY, 26, QFont.Weight.Bold))
        title_text.setStyleSheet(f"color: {COLORS['text']}; background: transparent;")
        
        title_layout.addWidget(map_icon)
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
        self.egg_label.setStyleSheet(f"color: {COLORS['accent_dark']}; background: transparent; border: none;")
        
        egg_layout.addWidget(egg_icon)
        egg_layout.addWidget(self.egg_label)
        
        header.addWidget(egg_frame)
        
        # Training Camp Button
        self.practice_btn = QPushButton("🏕️ Training Camp")
        self.practice_btn.setFixedHeight(50)
        self.practice_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFB347;
                color: white;
                border: none;
                border-bottom: 4px solid #E59400;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #FFC347;
            }
            QPushButton:pressed {
                background-color: #E59400;
                border-bottom: 2px solid #E59400;
            }
        """)
        self.practice_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.practice_btn.clicked.connect(self._on_practice_clicked)
        header.addWidget(self.practice_btn)
        
        return header
    
    def _build_level_grid(self) -> QWidget:
        """Build the level selection grid."""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        
        grid = QGridLayout(container)
        grid.setSpacing(BUTTON_GAP)
        
        # Create 2 rows of 5 buttons
        for i in range(1, MAP_LEVELS_COUNT + 1):
            btn = PremiumLevelButton(i)
            btn.clicked.connect(lambda checked, level=i: self.level_selected.emit(level))
            self._level_buttons.append(btn)
            
            row = (i - 1) // 5
            col = (i - 1) % 5
            grid.addWidget(btn, row, col)
        
        return container
    
    def _on_practice_clicked(self):
        """Open the practice configuration dialog."""
        print(f"[PremiumMapView] ACTION: Opening PracticeDialog")
        dialog = PracticeDialog(self)
        if dialog.exec():
            print(f"[PremiumMapView] ACTION: Starting practice mode: {dialog.selected_mode}")
            # We emit the mode string instead of a level int
            self.level_selected.emit(dialog.selected_mode)
            
    async def refresh(self, egg_count: int):
        """Update the map with current progress."""
        self.egg_label.setText(f"{egg_count} eggs")
        
        # Get unlocked level from DB
        unlocked = await self.db.get_unlocked_level()
        
        for idx, btn in enumerate(self._level_buttons, start=1):
            btn.set_unlocked(idx <= unlocked)
