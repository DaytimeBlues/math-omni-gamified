"""
Visual Board Component - Premium Emoji Rendering

Handles the grid layout of emojis, animations, and multiple visualization modes.

Gemini Pedagogical Modes:
- NORMAL: Standard display for counting/addition
- GHOST: Items fade out (Take-Away model, intermediate)
- CROSSOUT: Items marked with X but remain visible (Novice-friendly per Concreteness Fading)
"""

from enum import Enum, auto
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtGui import QFont, QPainter, QPen, QColor

from config import FONT_FAMILY


class VisualMode(Enum):
    """
    Visual rendering modes per Gemini pedagogical audit.
    
    NORMAL: For counting/addition - show items without modification
    GHOST: For subtraction (intermediate) - items fade out (Take-Away)
    CROSSOUT: For subtraction (novice) - items marked with X but visible
    """
    NORMAL = auto()
    GHOST = auto()      # Current implementation - items fade
    CROSSOUT = auto()   # Items visible but marked (recommended for novices)


class EmojiItem(QLabel):
    """
    Individual emoji item with Ghost Mode capability.
    Ghost Mode: Fades out and draws a red cross over the item.
    """
    def __init__(self, char: str, parent=None):
        super().__init__(char, parent)
        self.char = char
        self.is_ghost = False
        self.setFont(QFont("Segoe UI Emoji", 48))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: transparent;")
        
        # Opacity effect for fade out
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
    def set_ghost_mode(self, enabled: bool, animate: bool = True):
        """Enable ghost mode (faded + crossed out)."""
        self.is_ghost = enabled
        
        target_opacity = 0.3 if enabled else 1.0
        
        if animate:
            self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.anim.setDuration(400)
            self.anim.setEndValue(target_opacity)
            self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.anim.start()
        else:
            self.opacity_effect.setOpacity(target_opacity)
            
        self.update() # Trigger paintEvent for cross

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.is_ghost:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw Red Cross
            pen = QPen(QColor("#FF6B6B"))  # Soft Coral
            pen.setWidth(4)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            # Calculate cross coordinates (centered, 60% size)
            rect = self.rect()
            s = int(min(rect.width(), rect.height()) * 0.6)
            cx, cy = rect.center().x(), rect.center().y()
            
            painter.drawLine(cx - s//2, cy - s//2, cx + s//2, cy + s//2)
            painter.drawLine(cx + s//2, cy - s//2, cx - s//2, cy + s//2)
            painter.end()


class VisualBoard(QWidget):
    """
    Grid container for problem visuals.
    Auto-arranges items in rows of 5.
    
    DeepSeek Performance Fix: Object pooling to eliminate GC jitter.
    Pre-allocates 20 EmojiItem widgets and reuses them.
    """
    POOL_SIZE = 20  # Max items we'll ever display
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Pre-allocate widget pool (DeepSeek recommendation)
        self._pool: list[EmojiItem] = []
        for _ in range(self.POOL_SIZE):
            item = EmojiItem("?")  # Placeholder char
            item.setVisible(False)
            self._pool.append(item)
        
    def render(self, emoji: str, count: int, mode: str = "normal", subtract_count: int = 0):
        """
        Render emojis using pooled widgets.
        Zero allocations during gameplay = no GC jitter.
        """
        cols = 5
        
        # 1. Reset all pooled widgets
        for widget in self._pool:
            widget.setVisible(False)
            widget.is_ghost = False
            widget.opacity_effect.setOpacity(1.0)
        
        # 2. Activate required count from pool
        for i in range(min(count, self.POOL_SIZE)):
            item = self._pool[i]
            
            # Update content (no allocation, just setText)
            item.setText(emoji)
            item.char = emoji
            
            # Grid positioning
            row = i // cols
            col = i % cols
            
            # Remove from current position and re-add at correct spot
            self.grid.removeWidget(item)
            self.grid.addWidget(item, row, col)
            
            # Ghost mode for subtraction
            is_ghost = (mode == "subtract") and (i >= (count - subtract_count))
            
            item.setVisible(True)
            
            if is_ghost:
                # Staggered animation for visual effect
                QTimer.singleShot(500 + (i * 50), lambda w=item: w.set_ghost_mode(True))

    def _clear(self):
        """Hide all pooled items (no destruction)."""
        for item in self._pool:
            item.setVisible(False)
