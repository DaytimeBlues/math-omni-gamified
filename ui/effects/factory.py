"""
Visual Effects for Celebrations (Gemini Design)

Strategy Pattern: CelebrationOverlay owns a VisualEffect instance.
QPainter rendering for efficiency (<60 particles).
"""
import random
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QPolygonF
from PyQt6.QtCore import QPointF, QRect, Qt


# --- Data Structures ---

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    size: float
    color: QColor
    rotation: float = 0.0
    rot_speed: float = 0.0
    life: float = 1.0  # 0.0 to 1.0
    shape_type: str = "circle"


# --- Abstract Base Class ---

class VisualEffect(ABC):
    def __init__(self, duration_ms: int = 3000):
        self.duration_ms = duration_ms
        self.elapsed_ms = 0
        self.particles: list[Particle] = []
        self.finished = False

    @abstractmethod
    def _init_particles(self, rect: QRect):
        """Initialize particle positions based on screen size."""
        pass

    def update(self, dt_ms: int, rect: QRect) -> bool:
        """
        Updates physics. Returns False if effect is over.
        """
        self.elapsed_ms += dt_ms
        if self.elapsed_ms >= self.duration_ms:
            self.finished = True
            return False
        
        # Lazy init if particles don't exist yet (waits for valid rect)
        if not self.particles and rect.isValid():
            self._init_particles(rect)
            
        return self._update_particles(dt_ms, rect)

    @abstractmethod
    def _update_particles(self, dt_ms: int, rect: QRect) -> bool:
        pass

    @abstractmethod
    def draw(self, painter: QPainter, rect: QRect):
        pass


# --- Concrete Effects ---

class ConfettiEffect(VisualEffect):
    """Colorful confetti falling from top."""
    
    def _init_particles(self, rect: QRect):
        colors = [Qt.GlobalColor.red, Qt.GlobalColor.green, Qt.GlobalColor.blue, 
                  Qt.GlobalColor.yellow, Qt.GlobalColor.cyan, Qt.GlobalColor.magenta]
        
        for _ in range(50):  # Cap at 50 for performance
            self.particles.append(Particle(
                x=random.randint(0, rect.width()),
                y=random.randint(-100, -10),  # Start above screen
                vx=random.uniform(-2, 2),
                vy=random.uniform(2, 5),
                size=random.uniform(5, 10),
                color=QColor(random.choice(colors)),
                rotation=random.uniform(0, 360),
                rot_speed=random.uniform(-5, 5),
                shape_type="rect"
            ))

    def _update_particles(self, dt_ms: int, rect: QRect) -> bool:
        for p in self.particles:
            p.y += p.vy
            p.x += p.vx + math.sin(p.y * 0.05)  # Flutter
            p.rotation += p.rot_speed
            
            # Wrap around horizontal
            if p.x > rect.width(): p.x = 0
            if p.x < 0: p.x = rect.width()
            
        return True

    def draw(self, painter: QPainter, rect: QRect):
        for p in self.particles:
            painter.save()
            painter.translate(p.x, p.y)
            painter.rotate(p.rotation)
            painter.fillRect(int(-p.size/2), int(-p.size/2), int(p.size), int(p.size), p.color)
            painter.restore()


class StarBurstEffect(VisualEffect):
    """Stars exploding from center."""
    
    def _init_particles(self, rect: QRect):
        cx, cy = rect.center().x(), rect.center().y()
        for _ in range(40):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(2, 8)
            self.particles.append(Particle(
                x=cx,
                y=cy,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                size=random.uniform(10, 25),
                color=QColor("gold"),
                shape_type="star"
            ))

    def _update_particles(self, dt_ms: int, rect: QRect) -> bool:
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.1  # Slight gravity
            p.life -= 0.015  # Fade out
            
        # Remove dead particles
        self.particles = [p for p in self.particles if p.life > 0]
        return len(self.particles) > 0

    def draw(self, painter: QPainter, rect: QRect):
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.particles:
            if p.life <= 0: continue
            col = QColor(p.color)
            col.setAlphaF(p.life)
            painter.setBrush(col)
            # Simple diamond star
            pts = [QPointF(p.x, p.y - p.size), QPointF(p.x + p.size/2, p.y),
                   QPointF(p.x, p.y + p.size), QPointF(p.x - p.size/2, p.y)]
            painter.drawPolygon(QPolygonF(pts))


class BubbleRiseEffect(VisualEffect):
    """Bubbles rising from bottom."""
    
    def _init_particles(self, rect: QRect):
        for _ in range(30):
            self.particles.append(Particle(
                x=random.randint(0, rect.width()),
                y=rect.height() + random.randint(10, 100),
                vx=0,
                vy=random.uniform(-1, -4),
                size=random.uniform(10, 30),
                color=QColor(135, 206, 250, 150),  # Light sky blue
                shape_type="circle"
            ))

    def _update_particles(self, dt_ms: int, rect: QRect) -> bool:
        for p in self.particles:
            p.y += p.vy
            p.x += math.sin(p.y * 0.02) * 2  # Wobble
        return True

    def draw(self, painter: QPainter, rect: QRect):
        painter.setPen(QPen(QColor("white"), 2))
        for p in self.particles:
            painter.setBrush(p.color)
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)
            # Reflection dot
            painter.setBrush(QColor("white"))
            painter.drawEllipse(QPointF(p.x - p.size/3, p.y - p.size/3), p.size/4, p.size/4)


class HeartFloatEffect(VisualEffect):
    """Hearts floating upward."""
    
    def _init_particles(self, rect: QRect):
        for _ in range(30):
            self.particles.append(Particle(
                x=random.randint(0, rect.width()),
                y=rect.height() + random.randint(10, 50),
                vx=0,
                vy=random.uniform(-2, -5),
                size=random.uniform(15, 30),
                color=QColor(255, 105, 180),  # Hot pink
                shape_type="heart"
            ))

    def _update_particles(self, dt_ms: int, rect: QRect) -> bool:
        for p in self.particles:
            p.y += p.vy
            p.size += math.sin(p.y * 0.1) * 0.5  # Pulse
        return True

    def draw(self, painter: QPainter, rect: QRect):
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.particles:
            painter.setBrush(p.color)
            # Heart using 2 circles and a triangle
            painter.drawEllipse(QPointF(p.x - p.size/2, p.y), p.size, p.size) 
            painter.drawEllipse(QPointF(p.x + p.size/2, p.y), p.size, p.size)
            triangle = [
                QPointF(p.x - p.size, p.y + p.size/2), 
                QPointF(p.x + p.size*1.5, p.y + p.size/2), 
                QPointF(p.x + 0.25*p.size, p.y + p.size*2.5)
            ]
            painter.drawPolygon(QPolygonF(triangle))


# --- Factory ---

class CelebrationFactory:
    """
    Creates visual effects with no immediate repeats.
    Tracks last effect to ensure variety.
    """
    
    def __init__(self):
        self._effect_classes = [ConfettiEffect, StarBurstEffect, BubbleRiseEffect, HeartFloatEffect]
        self._last_effect_idx = -1

    def create_effect(self) -> VisualEffect:
        """Returns a new effect instance, ensuring no immediate repeats."""
        if len(self._effect_classes) <= 1:
            idx = 0
        else:
            options = [i for i in range(len(self._effect_classes)) if i != self._last_effect_idx]
            idx = random.choice(options)
        
        self._last_effect_idx = idx
        return self._effect_classes[idx]()
