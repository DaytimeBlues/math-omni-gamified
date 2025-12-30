"""
Celebration Overlay
"""
import random
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPointF, QPropertyAnimation
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush

from config import COLORS, FONT_FAMILY

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Random velocity (explosion)
        self.vx = random.uniform(-10, 10)
        self.vy = random.uniform(-15, -5) # Upward burst
        self.gravity = 0.5
        self.color = QColor(
            random.choice([
                COLORS['primary'], COLORS['accent'], 
                COLORS['success'], COLORS['danger'],
                "#FFD700", "#FF69B4", "#00FFFF" # Gold, HotPink, Cyan
            ])
        )
        self.size = random.randint(8, 16)
        self.life = 1.0 # 100% opacity
        self.decay = random.uniform(0.01, 0.03)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity # Gravity
        self.life -= self.decay

class CelebrationOverlay(QWidget):
    """
    Full-screen overlay with confetti particles and congratulatory text.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False) # Catch clicks to skip?
        # Actually want to block clicks to underlying, BUT click to dismiss.
        
        self.particles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_physics)
        
        # Setup UI
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.msg_label = QLabel("LEVEL COMPLETE!")
        self.msg_label.setFont(QFont(FONT_FAMILY, 48, QFont.Weight.Bold))
        self.msg_label.setStyleSheet("color: white; padding: 20px; background-color: rgba(0,0,0,100); border-radius: 20px;")
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.msg_label)
        
        self.hide()

    def start(self, text="LEVEL COMPLETE!"):
        self.msg_label.setText(text)
        self.resize(self.parent().size())
        self.show()
        self.raise_()
        
        # Spawn particles (center bottom)
        cx = self.width() / 2
        cy = self.height() # Bottom
        self.particles = []
        for _ in range(100):
            self.particles.append(Particle(cx, cy))
            
        self.timer.start(16) # ~60 FPS
        
        # Auto-dismiss
        QTimer.singleShot(2500, self.stop)

    def stop(self):
        self.timer.stop()
        self.hide()

    def mousePressEvent(self, event):
        # Click to skip
        self.stop()

    def _update_physics(self):
        alive_particles = []
        for p in self.particles:
            p.update()
            if p.life > 0 and p.y < self.height() + 50:
                alive_particles.append(p)
        
        self.particles = alive_particles
        
        if not self.particles:
            self.stop()
        
        self.update() # Trigger paint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Semi-transparent dark background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # Draw particles
        for p in self.particles:
            painter.setBrush(QBrush(p.color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setOpacity(max(0, p.life))
            
            # Simple circle
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)
            
            # Or Rect for confetti style?
            # painter.drawRect(int(p.x), int(p.y), p.size, p.size)
