# demo_premium_screen.py
"""
Premium UI Reference - LLM-provided demo
Run this standalone to see the target aesthetic.
Then transplant working components into the main app.
"""
import sys
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


COLORS = {
    "bg": "#FCF4E3",
    "bg_border": "rgba(255,255,255,220)",
    "card": "#FBF8F0",
    "text": "#2C3E50",
    "primary": "#4DA8DA",
    "primary_dark": "#2B8BC0",
    "accent": "#FFB347",
    "accent_dark": "#E69A2E",
}


def apply_shadow(widget: QWidget, blur: int = 28, y: int = 10, alpha: int = 45):
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(blur)
    eff.setOffset(0, y)
    eff.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(eff)


class EggIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Egg body
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(COLORS["accent"]))
        p.drawEllipse(4, 2, 20, 24)

        # Highlight
        p.setBrush(QColor(255, 255, 255, 110))
        p.drawEllipse(8, 6, 8, 10)

        # Outline
        pen = QPen(QColor(COLORS["accent_dark"]))
        pen.setWidth(2)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(4, 2, 20, 24)


class PremiumButton(QPushButton):
    def __init__(self, text: str, variant: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("variant", variant)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_shadow(self, blur=26, y=10, alpha=40)

        # Ensure QSS sees the dynamic property
        self.style().unpolish(self)
        self.style().polish(self)


class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", True)
        apply_shadow(self, blur=40, y=14, alpha=35)
        self.style().unpolish(self)
        self.style().polish(self)


class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Premium UI Reference")

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30)

        phone = QFrame()
        phone.setObjectName("PhoneShell")
        phone.setFixedSize(440, 860)
        apply_shadow(phone, blur=45, y=18, alpha=35)

        phone_layout = QVBoxLayout(phone)
        phone_layout.setContentsMargins(26, 26, 26, 26)
        phone_layout.setSpacing(24)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)

        back = PremiumButton("←", "accent_circle")
        back.setFixedSize(58, 58)

        title = QLabel("Level 1")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        egg_pill = QWidget()
        egg_pill.setObjectName("EggPill")
        egg_pill.setFixedHeight(46)

        egg_layout = QHBoxLayout(egg_pill)
        egg_layout.setContentsMargins(14, 8, 14, 8)
        egg_layout.setSpacing(10)

        egg_layout.addWidget(EggIcon())
        egg_count = QLabel("0")
        egg_count.setObjectName("EggCount")
        egg_layout.addWidget(egg_count)

        header.addWidget(back, 0, Qt.AlignmentFlag.AlignLeft)
        header.addStretch(1)
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)
        header.addStretch(1)
        header.addWidget(egg_pill, 0, Qt.AlignmentFlag.AlignRight)

        phone_layout.addLayout(header)

        phone_layout.addSpacing(40)

        card = Card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 22)

        question = QLabel("1 + 1")
        question.setObjectName("Question")
        question.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(question)

        phone_layout.addWidget(card)
        phone_layout.addStretch(1)

        grid = QGridLayout()
        grid.setHorizontalSpacing(22)
        grid.setVerticalSpacing(18)

        for i, t in enumerate(["2", "0", "4", "7"]):
            btn = PremiumButton(t, "primary")
            btn.setFixedSize(170, 92)
            grid.addWidget(btn, i // 2, i % 2)

        phone_layout.addLayout(grid)

        root.addWidget(phone, 0, Qt.AlignmentFlag.AlignHCenter)

        self.setStyleSheet(self._qss())

    def _qss(self) -> str:
        return f"""
        QWidget {{
            color: {COLORS["text"]};
            background: transparent;
        }}

        QFrame#PhoneShell {{
            background-color: {COLORS["bg"]};
            border-radius: 56px;
            border: 10px solid {COLORS["bg_border"]};
        }}

        QLabel#Title {{
            color: {COLORS["primary"]};
            font-size: 26px;
            font-weight: 900;
        }}

        QWidget#EggPill {{
            background-color: #FFF6DC;
            border: 3px solid {COLORS["accent"]};
            border-radius: 23px;
        }}

        QLabel#EggCount {{
            color: {COLORS["accent_dark"]};
            font-size: 20px;
            font-weight: 900;
        }}

        QFrame[card="true"] {{
            background-color: {COLORS["card"]};
            border-radius: 40px;
            border: 3px solid rgba(255,255,255,200);
        }}

        QLabel#Question {{
            font-size: 54px;
            font-weight: 900;
            letter-spacing: 1px;
        }}

        QPushButton {{
            border: none;
            outline: none;
        }}

        QPushButton:focus {{
            border: 3px solid rgba(255,255,255,170);
        }}

        /* Primary answer buttons */
        QPushButton[variant="primary"] {{
            background-color: {COLORS["primary"]};
            color: white;
            border-radius: 28px;
            font-size: 30px;
            font-weight: 900;
            border-bottom: 10px solid {COLORS["primary_dark"]};
            padding-top: 14px;
            padding-bottom: 6px;
        }}

        QPushButton[variant="primary"]:pressed {{
            background-color: {COLORS["primary_dark"]};
            border-bottom: 4px solid {COLORS["primary_dark"]};
            padding-top: 20px;
            padding-bottom: 0px;
        }}

        /* Accent circular back button */
        QPushButton[variant="accent_circle"] {{
            background-color: {COLORS["accent"]};
            color: {COLORS["text"]};
            border-radius: 29px;
            font-size: 26px;
            font-weight: 900;
            border-bottom: 8px solid {COLORS["accent_dark"]};
            padding-top: 6px;
            padding-bottom: 0px;
        }}

        QPushButton[variant="accent_circle"]:pressed {{
            background-color: {COLORS["accent_dark"]};
            border-bottom: 3px solid {COLORS["accent_dark"]};
            padding-top: 11px;
            padding-bottom: 0px;
        }}
        """


def main():
    app = QApplication(sys.argv)

    # Critical for predictable QSS metrics across platforms.
    app.setStyle("Fusion")

    # Avoid Comic Sans fallback entirely.
    # Replace "Lexend" with your installed font; if unavailable, Qt will fall back.
    app.setFont(QFont("Lexend", 12))

    w = DemoWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
