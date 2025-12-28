"""
Celebration Overlay - Star Animation for Correct Answers
The "dopamine hit" that makes the app feel finished.

PEDAGOGICAL PURPOSE:
A visual reward activates the brain's reward system, making
the child want to continue. This is the difference between
"5 minutes of engagement" and "30 minutes of flow state."
"""

from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, 
    QTimer, QPoint, QSize, pyqtProperty
)
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
import os


class CelebrationOverlay(QWidget):
    """
    A transparent overlay that shows a star animation and plays a sound.
    
    DESIGN:
    - Large emoji star that scales up and bounces
    - Optional "ding" sound effect
    - Auto-hides after animation completes
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Make overlay transparent and cover parent
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Star emoji label
        self.star_label = QLabel("⭐", self)
        self.star_label.setFont(QFont("Segoe UI Emoji", 80))
        self.star_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.star_label.setStyleSheet("background: transparent;")
        
        # Animation for scaling effect
        self._scale = 1.0
        self.scale_anim = QPropertyAnimation(self, b"scale")
        self.scale_anim.setDuration(600)
        self.scale_anim.setStartValue(0.3)
        self.scale_anim.setEndValue(1.0)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        # Setup sound effect
        self.sound = QSoundEffect()
        sound_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'ding.wav')
        if os.path.exists(sound_path):
            self.sound.setSource(QUrl.fromLocalFile(sound_path))
            self.sound.setVolume(0.5)
        
        # Hide initially
        self.hide()
    
    def get_scale(self):
        return self._scale
    
    def set_scale(self, value):
        self._scale = value
        # Update star size based on scale
        base_size = 120
        new_size = int(base_size * value)
        self.star_label.setFont(QFont("Segoe UI Emoji", int(80 * value)))
        self._center_star()
    
    scale = pyqtProperty(float, get_scale, set_scale)
    
    def _center_star(self):
        """Center the star in the overlay."""
        if self.parent():
            parent_rect = self.parent().rect()
            self.setGeometry(parent_rect)
            star_size = self.star_label.sizeHint()
            x = (parent_rect.width() - star_size.width()) // 2
            y = (parent_rect.height() - star_size.height()) // 2
            self.star_label.move(x, y)
    
    def celebrate(self):
        """
        Show the celebration animation.
        
        Called when child gets a correct answer.
        """
        self._center_star()
        self.show()
        self.raise_()
        
        # Play sound (if available)
        if self.sound.source().isValid():
            self.sound.play()
        
        # Start scale animation
        self.scale_anim.start()
        
        # Auto-hide after animation
        QTimer.singleShot(1500, self.hide)
    
    def resizeEvent(self, event):
        """Reposition star when overlay resizes."""
        super().resizeEvent(event)
        self._center_star()
