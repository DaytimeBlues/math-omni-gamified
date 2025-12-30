"""
Celebration Overlay - Visual Reward System (Gemini Design)

QPainter-based particle effects with tap-to-skip.
Uses CelebrationFactory for variety (no immediate repeats).
"""
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor

from ui.effects.factory import CelebrationFactory, VisualEffect


class CelebrationOverlay(QWidget):
    """
    Fullscreen overlay for celebration effects.
    
    Features:
    - 4 visual effects (confetti, stars, bubbles, hearts)
    - No immediate repeats
    - Tap-to-skip
    - Callback on complete
    """
    
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        self.factory = CelebrationFactory()
        self.active_effect: VisualEffect | None = None
        self._callback = None
        
        # UI Elements
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 64px; 
                font-weight: bold;
                color: white;
                background-color: rgba(0,0,0,100);
                border-radius: 20px;
                padding: 20px;
            }
        """)
        
        # Animation Loop (~60 FPS)
        self._timer = QTimer()
        self._timer.timeout.connect(self._game_loop)
        self._frame_time = 16
        
        self.hide()

    def start(self, text: str = "Good Job!", on_complete=None):
        """
        Starts the visual celebration.
        
        Args:
            text: Message to display
            on_complete: Optional callback when effect finishes
        """
        self._callback = on_complete
        self.active_effect = self.factory.create_effect()
        self.label.setText(text)
        self.label.adjustSize()
        
        # Center label and resize to parent
        if self.parent():
            self.resize(self.parent().size())
            center = self.rect().center()
            self.label.move(
                center.x() - self.label.width() // 2, 
                center.y() - self.label.height() // 2
            )
        
        self.show()
        self.raise_()
        self._timer.start(self._frame_time)

    def _game_loop(self):
        """Animation update loop."""
        if not self.active_effect:
            self.stop()
            return

        # Update physics
        is_running = self.active_effect.update(self._frame_time, self.rect())
        
        # Trigger repaint
        self.update()

        if not is_running:
            self.stop()

    def paintEvent(self, event):
        """Delegate drawing to active effect."""
        if not self.active_effect:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.active_effect.draw(painter, self.rect())

    def mousePressEvent(self, event):
        """Tap-to-skip: allow user to skip animation."""
        self.stop()

    def stop(self):
        """Clean up and notify."""
        self._timer.stop()
        self.active_effect = None
        self.hide()
        
        if self._callback:
            # Defer callback to ensure UI stack unwinds cleanly
            QTimer.singleShot(0, self._callback)
            self._callback = None
            
        self.finished.emit()
