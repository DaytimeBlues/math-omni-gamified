"""
Premium UI Utilities
High-quality shadow effects and animations for the Sidereal Voyager UI.
"""
from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QSequentialAnimationGroup, QEasingCurve, QPoint
from PyQt6.QtGui import QColor


def add_soft_shadow(
    widget: QWidget, 
    blur: int = 20, 
    offset_x: int = 0, 
    offset_y: int = 8, 
    opacity: int = 40, 
    color: str = "#000000"
):
    """
    Applies a 'premium' soft shadow to a widget using QGraphicsDropShadowEffect.
    
    Args:
        widget: The widget to apply the shadow to.
        blur: The blur radius (softness).
        offset_x: Horizontal offset.
        offset_y: Vertical offset.
        opacity: Shadow opacity (0-100).
        color: Hex color string.
    """
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setXOffset(offset_x)
    shadow.setYOffset(offset_y)
    
    c = QColor(color)
    # Convert 0-100 opacity to 0-255 alpha
    c.setAlpha(int(opacity * 2.55)) 
    shadow.setColor(c)
    
    widget.setGraphicsEffect(shadow)


def create_shake_animation(widget: QWidget, amplitude: int = 8, duration: int = 50) -> QSequentialAnimationGroup:
    """
    Creates a 'shake' animation for incorrect answer feedback.
    
    Args:
        widget: The widget to shake.
        amplitude: Pixels to move left/right.
        duration: Duration of each shake step in ms.
        
    Returns:
        A QSequentialAnimationGroup that can be started.
    """
    group = QSequentialAnimationGroup(widget)
    original = widget.pos()
    
    # Shake sequence: left -> right -> left -> center
    offsets = [-amplitude, amplitude, -amplitude // 2, amplitude // 2, 0]
    
    for offset in offsets:
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setEndValue(QPoint(original.x() + offset, original.y()))
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        group.addAnimation(anim)
    
    return group


def draw_premium_background(widget: QWidget):
    """
    Draw the premium cream gradient background directly in a widget's paintEvent.
    Call this from an overridden paintEvent method.
    """
    from PyQt6.QtGui import QPainter, QLinearGradient, QColor
    
    painter = QPainter(widget)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    gradient = QLinearGradient(0, 0, 0, widget.height())
    gradient.setColorAt(0.0, QColor("#FEF9E7"))
    gradient.setColorAt(0.5, QColor("#FAF0DC"))
    gradient.setColorAt(1.0, QColor("#F5E6C8"))
    
    painter.fillRect(widget.rect(), gradient)
