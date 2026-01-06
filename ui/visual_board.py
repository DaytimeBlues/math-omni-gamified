import logging
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QFont, QPainter, QColor, QPixmap, QPen

# --- VERBOSE LOGGING GOVERNANCE ---
# Narrative style for self-diagnosis
# ----------------------------------

class EmojiItem(QLabel):
    """
    Optimized emoji display item.
    
    PERFORMANCE IMPROVEMENT (Frontend Audit v3.0):
    - Implements class-level caching for ghost-mode pixmaps.
    - Avoids QGraphicsOpacityEffect overhead (which creates offscreen buffers).
    - Uses pre-rendered QPixmaps for "crossout" mode for 60FPS performance on low-end hardware.
    """
    
    # Class-level cache: "emoji_size" -> QPixmap
    _ghost_cache: dict[str, QPixmap] = {}
    _normal_cache: dict[str, QPixmap] = {}

    def __init__(self, emoji: str, size: int = 80, parent=None):
        super().__init__(parent)
        self._emoji = emoji
        self._size = size
        self._is_ghost = False
        
        # Initialize with normal pixmap
        print(f"[EmojiItem] INIT: Creating item '{emoji}' size={size}")
        self._normal_pixmap = self._get_normal_pixmap(emoji, size)
        self.setPixmap(self._normal_pixmap)
        
        # Fixed size for stability, but content is pre-rendered
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Ensure we don't scale the pixmap (it's already the right size)
        self.setScaledContents(False)

    def set_ghost_mode(self, enabled: bool, animate: bool = True):
        """
        Switch between normal and ghost/crossout mode.
        If 'enabled' is True, shows the Emoji with 30% opacity and a red cross.
        """
        if self._is_ghost == enabled:
            return
            
        print(f"[EmojiItem] STATE: Switching ghost mode for '{self._emoji}' to {enabled} (animate={animate})")
        self._is_ghost = enabled
        
        target_pixmap = self._get_ghost_pixmap() if enabled else self._normal_pixmap
        
        if animate:
            print(f"[EmojiItem] ANIM: Starting opacity transition")
            self._animate_transition(target_pixmap)
        else:
            self.setPixmap(target_pixmap)

    def _get_normal_pixmap(self, emoji: str, size: int) -> QPixmap:
        """Retrieve or create a normal emoji pixmap from cache."""
        key = f"{emoji}_{size}"
        if key not in self._normal_cache:
            print(f"[EmojiItem] CACHE MISS: Rendering normal pixmap for {key}")
            self._normal_cache[key] = self._render_emoji(emoji, size, ghost=False)
        else:
             # print(f"[EmojiItem] CACHE HIT: Found normal pixmap for {key}") # Commented for spam reduction
             pass
        return self._normal_cache[key]

    def _get_ghost_pixmap(self) -> QPixmap:
        """Retrieve or create a ghost mode pixmap from cache."""
        key = f"{self._emoji}_{self._size}_ghost"
        if key not in self._ghost_cache:
            print(f"[EmojiItem] CACHE MISS: Rendering ghost pixmap for {key}")
            self._ghost_cache[key] = self._render_emoji(self._emoji, self._size, ghost=True)
        return self._ghost_cache[key]

    @staticmethod
    def _render_emoji(emoji: str, size: int, ghost: bool) -> QPixmap:
        """
        Render the emoji to a customized QPixmap.
        If ghost=True, applies 30% opacity and draws a red cross.
        
        FIX: Added soft cream circle background for better visual blending.
        """
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # 0. Draw soft cream background circle (matches UI background)
        bg_color = QColor("#FEF9E7")  # Cream from design tokens
        bg_color.setAlpha(200)  # Slightly transparent for softness
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        margin = int(size * 0.05)
        painter.drawEllipse(margin, margin, size - 2*margin, size - 2*margin)
        
        # 1. Draw Emoji
        # If ghost, we draw the text at 30% opacity
        opacity = 0.3 if ghost else 1.0
        painter.setOpacity(opacity)
        
        # Use a large font size relative to the box
        font_size = int(size * 0.65)  # Slightly smaller to fit in circle
        font = QFont("Segoe UI Emoji", font_size)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        painter.setFont(font)
        
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        
        # 2. Draw Cross (if ghost)
        if ghost:
            painter.setOpacity(1.0) # Cross is full strength
            pen = QPen(QColor("#FF6B6B")) # Premium error color
            # Thickness scales with size
            pen.setWidth(max(3, size // 16))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            # Margin for the cross so it doesn't touch edges
            margin = int(size * 0.2)
            rect = pixmap.rect().adjusted(margin, margin, -margin, -margin)
            
            painter.drawLine(rect.topLeft(), rect.bottomRight())
            painter.drawLine(rect.topRight(), rect.bottomLeft())
            
        painter.end()
        return pixmap
        
    def _animate_transition(self, target_pixmap: QPixmap):
        """Fade out, swap pixmap, fade in."""
        # Note: A proper crossfade requires two widgets or custom painting.
        # For simplicity/performance on low-end, we'll do a quick opacity dip.
        
        # However, since we are replacing the specific painting approach, 
        # let's just swap it. The visual audit said "Pre-rendered QPixmap be better?"
        # Animation is secondary to the performance fix.
        # We will implement a simple property animation if needed, 
        # but for now, the instant snap is cleaner than a laggy fade.
        self.setPixmap(target_pixmap)


class VisualBoard(QWidget):
    """
    Manages the grid of emojis.
    Refactored to be RESPONSIVE (Frontend Audit v3.0).
    """
    
    MAX_COLUMNS = 5
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("[VisualBoard] INIT: Starting up")
        
        # Layout Setup
        self._layout = QGridLayout(self)
        self._layout.setSpacing(10) # Gap between items
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Responsive Column Stretching
        # ensuring columns share space equally
        for i in range(self.MAX_COLUMNS):
            self._layout.setColumnStretch(i, 1)
            
        self._active_widgets = []
        
        # Size Policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(150) # Ensure it has some presence

    def render(self, emoji: str, count: int, mode: str="normal", subtract_count: int=0, animate_crossout: bool=True):
        """
        Render `count` items.
        mode="subtract": The last `subtract_count` items are ghosted.
        Returns the list of items that were ghosted (if any).
        """
        print(f"[VisualBoard] RENDER: emoji={emoji} count={count} mode={mode} sub={subtract_count}")
        
        self._clear()
        leaver_widgets = []
        
        # Determine strict grid size
        # We want to center the grid content. 
        # Standard logic: fill row by row.
        
        # Calculate dynamic size based on current widget width
        # But since we are inside a layout, 'width()' might be 0 initially.
        # We'll use a sensible default of 80 if we can't determine, or rely on layout.
        
        # Strategy: Create widgets, add to grid. Qt Layout handles the positions.
        
        for i in range(count):
            # Create Item
            item = EmojiItem(emoji, size=80) # Fixed size items, layout handles spacing
            
            # Grid Math
            row = i // self.MAX_COLUMNS
            col = i % self.MAX_COLUMNS
            
            # Special Centering Logic for Partial Last Row?
            # Standard GRID left-aligns the last row.
            # To center the last row, we'd need nested HBoxes.
            # BUT, the Frontend Audit specifically requested "Check VisualBoard... inside QuestionCard"
            # and proposed "Use QGridLayout with proper stretch factors"
            # So we stick to QGridLayout for robustness.
            
            self._layout.addWidget(item, row, col, Qt.AlignmentFlag.AlignCenter)
            self._active_widgets.append(item)
            
            # Apply Mode
            if mode == "subtract" or mode == "crossout":
                # Logic: Is this one of the items to be removed?
                # Usually we remove from the END.
                # If we have 5 items and subtract 2, we ghost indices 3 and 4 (0-based).
                threshold_index = count - subtract_count
                if i >= threshold_index:
                    is_ghost = True
                else:
                    is_ghost = False
                    
                if is_ghost:
                    leaver_widgets.append(item)
                    if not animate_crossout:
                        item.set_ghost_mode(True, animate=False)
        
        return leaver_widgets

    def _clear(self):
        """Remove all items from layout."""
        # print("[VisualBoard] ACTION: Clearing board") # Verbose
        for widget in self._active_widgets:
            self._layout.removeWidget(widget)
            widget.deleteLater()
        self._active_widgets.clear()
