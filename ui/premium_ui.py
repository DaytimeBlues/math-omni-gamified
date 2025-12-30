"""
Premium UI Components - "Omni Kids" Design Language

Implements:
- PremiumButton with shadows and 3D press effect
- Master QSS stylesheet
- Gradient background helper

Design: Gemini 3 Pro
Fixes: ChatGPT 5.2 (no margin jitter, locked style, focus states)
"""

from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect, QWidget
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt

from config import COLORS, FONT_FAMILY


# =============================================================================
# MASTER QSS STYLESHEET
# =============================================================================

MASTER_STYLESHEET = f"""
/* General App Setting */
/* LLM Fix: Removed "Comic Sans MS" fallback - use Segoe UI instead */
QWidget {{
    font-family: "{FONT_FAMILY}", "Segoe UI", sans-serif;
    color: {COLORS['text']};
}}

/* ===============================================
   PREMIUM BUTTONS - The core interactive element
   Technique: Thick bottom border simulates depth.
   ChatGPT Fix: Use padding instead of margin to avoid layout jitter.
=============================================== */

/* Base Button Class */
QPushButton {{
    border-radius: 30px;
    padding: 15px 25px;
    padding-bottom: 23px;  /* Extra padding to absorb press effect */
    font-weight: 800;
    outline: none;
}}

/* PRIMARY BUTTON (Answer Options) */
QPushButton[buttonStyle="primary"] {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    border-bottom: 8px solid {COLORS['primary_dark']};
}}

QPushButton[buttonStyle="primary"]:hover {{
    background-color: {COLORS['primary_hover']};
}}

QPushButton[buttonStyle="primary"]:pressed {{
    background-color: {COLORS['primary_dark']};
    border-bottom: 2px solid {COLORS['primary_dark']};
    padding-bottom: 29px;  /* Absorb the border difference */
}}

QPushButton[buttonStyle="primary"]:focus {{
    border: 3px solid {COLORS['focus']};
    border-bottom: 8px solid {COLORS['primary_dark']};
}}

/* SUCCESS STATE (Correct Answer) - CVD: includes ✓ in text */
QPushButton[buttonStyle="success"] {{
    background-color: {COLORS['success']};
    color: white;
    border: none;
    border-bottom: 8px solid {COLORS['success_dark']};
}}

/* ERROR STATE (Wrong Answer) - CVD: includes ✗ in text */
QPushButton[buttonStyle="error"] {{
    background-color: {COLORS['error']};
    color: white;
    border: none;
    border-bottom: 8px solid {COLORS['error_dark']};
}}

/* LOCKED BUTTON (Map levels not yet unlocked) */
QPushButton[buttonStyle="locked"] {{
    background-color: {COLORS['locked']};
    color: #9E9E9E;
    border: none;
    border-bottom: 8px solid {COLORS['locked_dark']};
}}

/* ACCENT BUTTON (Navigation, Back) */
QPushButton[buttonStyle="accent"] {{
    background-color: {COLORS['accent']};
    color: {COLORS['text']};
    border: none;
    border-bottom: 8px solid {COLORS['accent_dark']};
}}

QPushButton[buttonStyle="accent"]:pressed {{
    background-color: {COLORS['accent_dark']};
    border-bottom: 2px solid {COLORS['accent_dark']};
    padding-bottom: 29px;
}}

/* DISABLED (fallback) */
QPushButton:disabled {{
    background-color: {COLORS['locked']};
    color: #9E9E9E;
    border-bottom: 8px solid {COLORS['locked_dark']};
}}
"""


# =============================================================================
# PREMIUM BUTTON CLASS
# =============================================================================

class PremiumButton(QPushButton):
    """
    A premium-looking button with drop shadow and 3D press effect.
    
    ChatGPT Fixes Applied:
    - No margin-top changes (uses padding instead)
    - Shadow blur reduced for locked buttons (performance)
    - Focus state included
    """
    
    def __init__(self, text: str, style_name: str = "primary", 
                 add_shadow: bool = True, parent=None):
        super().__init__(text, parent)
        
        self._base_text = text
        self._style_name = style_name
        
        # Set dynamic property for QSS targeting
        self.setProperty("buttonStyle", style_name)
        
        # Add drop shadow (optional for performance on many buttons)
        if add_shadow:
            self._add_shadow(style_name)
        
        # Ensure QSS re-evaluates
        self.style().unpolish(self)
        self.style().polish(self)
    
    def _add_shadow(self, style_name: str):
        """Add soft shadow - reduced blur for locked buttons (ChatGPT perf fix)."""
        shadow = QGraphicsDropShadowEffect(self)
        
        if style_name == "locked":
            shadow.setBlurRadius(10)  # Smaller blur for locked
            shadow.setOffset(0, 4)
        else:
            shadow.setBlurRadius(20)
            shadow.setOffset(0, 8)
        
        shadow.setColor(QColor(0, 0, 0, 40))  # ~15% opacity
        self.setGraphicsEffect(shadow)
    
    def set_status(self, status: str, text_override: str = None):
        """
        Change button style dynamically.
        
        Args:
            status: "primary", "success", "error", "locked", "accent"
            text_override: Optional new text (for CVD indicators)
        """
        self._style_name = status
        self.setProperty("buttonStyle", status)
        
        # CVD-friendly text indicators (ChatGPT recommendation)
        if text_override:
            self.setText(text_override)
        elif status == "success":
            self.setText(f"✓ {self._base_text}")
        elif status == "error":
            self.setText(f"✗ {self._base_text}")
        else:
            self.setText(self._base_text)
        
        # Re-polish for style change
        self.style().unpolish(self)
        self.style().polish(self)
    
    def reset(self):
        """Reset to primary state."""
        self.set_status("primary")
        self.setText(self._base_text)


# =============================================================================
# BACKGROUND HELPERS
# =============================================================================

def apply_gradient_background(widget: QWidget):
    """
    Apply warm gradient background to a widget.
    ChatGPT Fix: Requires setObjectName for selector to work.
    """
    widget.setObjectName("GradientContainer")
    widget.setStyleSheet(f"""
        QWidget#GradientContainer {{
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 {COLORS['background_start']},
                stop:1 {COLORS['background_end']}
            );
        }}
    """)


def get_egg_counter_style() -> str:
    """Return QSS for the premium egg counter container."""
    return f"""
        QWidget#EggContainer {{
            background-color: #FFFCE0;
            border: 3px solid {COLORS['accent']};
            border-radius: 30px;
            padding-left: 10px;
            padding-right: 15px;
        }}
    """
