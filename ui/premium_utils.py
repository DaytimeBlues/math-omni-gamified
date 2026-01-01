"""
Premium UI Utilities - Dynamic Background & Animations

Provides QPainter-based rendering for premium visual effects.
"""

from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QRect
from PyQt6.QtWidgets import QWidget


def draw_premium_background(widget: QWidget):
    """
    Draw a warm gradient background with subtle decorative shapes.
    
    Call this from your widget's paintEvent():
        def paintEvent(self, event):
            draw_premium_background(self)
            super().paintEvent(event)
    """
    painter = QPainter(widget)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # 1. Warm gradient (top to bottom)
    gradient = QLinearGradient(0, 0, 0, widget.height())
    gradient.setColorAt(0.0, QColor("#FFF9F0"))  # Warm Cloud
    gradient.setColorAt(1.0, QColor("#FFF0E1"))  # Peachier
    
    painter.fillRect(widget.rect(), gradient)
    
    # 2. Subtle decorative shapes (depth without distraction)
    painter.setPen(Qt.PenStyle.NoPen)
    
    # Big faint circle bottom left
    painter.setBrush(QColor(255, 220, 150, 40))  # Warm yellow, low opacity
    painter.drawEllipse(-50, widget.height() - 200, 300, 300)
    
    # Small faint circle top right
    painter.setBrush(QColor(72, 219, 251, 30))  # Sky blue, very low opacity
    painter.drawEllipse(widget.width() - 150, -50, 200, 200)
    
    painter.end()


def create_shake_animation(widget: QWidget, duration: int = 400) -> QSequentialAnimationGroup:
    """
    Create a left-right shake animation for wrong answer feedback.
    
    Usage:
        anim = create_shake_animation(button)
        anim.start()
    """
    anim_group = QSequentialAnimationGroup(widget)
    
    original_geo = widget.geometry()
    
    # Shake pattern: right, left, right, left, center
    offsets = [10, -10, 8, -8, 5, -5, 0]
    
    for offset in offsets:
        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(duration // len(offsets))
        anim.setStartValue(widget.geometry())
        
        new_geo = QRect(original_geo)
        new_geo.moveLeft(original_geo.left() + offset)
        anim.setEndValue(new_geo)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        anim_group.addAnimation(anim)
    
    return anim_group


def create_pulse_animation(widget: QWidget, duration: int = 1000) -> QPropertyAnimation:
    """
    Create a pulsing animation for the current level indicator.
    
    Usage:
        anim = create_pulse_animation(button)
        anim.setLoopCount(-1)  # Infinite
        anim.start()
    """
    # Note: For true scale animation, you'd need QGraphicsView.
    # This is a simple geometry-based approximation.
    anim = QPropertyAnimation(widget, b"geometry")
    anim.setDuration(duration)
    
    original = widget.geometry()
    
    # Grow by 5px on each side
    grown = QRect(
        original.left() - 5,
        original.top() - 5,
        original.width() + 10,
        original.height() + 10
    )
    
    anim.setStartValue(original)
    anim.setKeyValueAt(0.5, grown)  # Midpoint: grown
    anim.setEndValue(original)      # End: back to original
    
    anim.setEasingCurve(QEasingCurve.Type.InOutSine)
    
    return anim
