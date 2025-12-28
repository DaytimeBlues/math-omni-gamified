"""
Mathematical Learning Application for Foundation Year (Prep)
Designed for HP Omni with Touch/Stylus Support - PyQt6 Version

Target User: 5-year-old girl in Australia
Curriculum: Australian Curriculum: Mathematics (Foundation Year)

PEDAGOGICAL PHILOSOPHY:
This app uses the Concrete-Pictorial-Abstract (CPA) approach where:
1. CONCRETE: On-screen manipulatives the child can touch/drag
2. PICTORIAL: Visual representations (diagrams, number lines)  
3. ABSTRACT: Numerals only after conceptual understanding

TECHNICAL CHOICE - PyQt6 over Kivy:
- Native Windows Ink support via QTabletEvent
- Native look and feel on Windows
- Better stylus pressure sensitivity handling
- QHBoxLayout makes split-screen layouts simple
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """
    Application entry point.
    
    FULL-SCREEN RATIONALE:
    Full-screen removes desktop distractions—crucial for 5-year-olds
    who are easily pulled away by other visual elements on the screen.
    """
    app = QApplication(sys.argv)
    
    # Apply child-friendly application-wide styling
    app.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI', 'Comic Sans MS', sans-serif;
        }
        QPushButton {
            border-radius: 15px;
            padding: 15px 25px;
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton:hover {
            opacity: 0.9;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
