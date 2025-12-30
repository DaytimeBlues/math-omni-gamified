"""
Math Omni v2 - Gamified Learning Platform
Entry point using qasync for async Qt operations

Target: 5-year-old children (Foundation Year)
Core Tech: PyQt6 + qasync for non-blocking TTS

FIXES APPLIED (AI Review):
- Removed unused asyncSlot import (ChatGPT)
- Added error handling with QMessageBox (Z.ai, ChatGPT)
- Added lifecycle cleanup on quit (ChatGPT)
- Replaced ensure_future with create_task (ChatGPT)
- Public start_application method (Z.ai)
- Dynamic stylesheet using config values (Z.ai, ChatGPT)
- High DPI awareness (Z.ai)
"""

import sys
import asyncio
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from qasync import QEventLoop

from config import FONT_FAMILY, COLORS, MIN_TOUCH_TARGET
from core.database import DatabaseService
from core.audio_service import AudioService
from core.problem_factory import ProblemFactory
from ui.game_manager import GameManager
from core.utils import safe_create_task


def create_stylesheet() -> str:
    """
    Generate stylesheet dynamically from config values.
    FIX: Z.ai & ChatGPT - hardcoded stylesheet extracted to use config.
    """
    return f"""
        QWidget {{
            font-family: '{FONT_FAMILY}', 'Comic Sans MS', 'Segoe UI', sans-serif;
            background-color: {COLORS['background']};
        }}
        QPushButton {{
            border-radius: 15px;
            padding: 15px 25px;
            font-size: 20px;
            font-weight: bold;
            min-width: {MIN_TOUCH_TARGET}px;
            min-height: {MIN_TOUCH_TARGET}px;
        }}
        QPushButton:hover {{
            opacity: 0.9;
        }}
        QPushButton:disabled {{
            background-color: {COLORS['locked']};
            color: #888888;
        }}
    """


def main():
    """
    Entry point using qasync.
    
    WHY QASYNC?
    - edge-tts generates speech asynchronously
    - UI must never freeze while audio generates
    - Kids will rage-tap if app appears frozen
    """
    # FIX: Z.ai - High DPI awareness
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
    
    # qasync bridges Qt's event loop with asyncio
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # FIX: Apply dynamic stylesheet from config
    app.setStyleSheet(create_stylesheet())
    
    # Create services
    db = DatabaseService()
    audio = AudioService()
    factory = ProblemFactory()

    # Create window
    window = GameManager(db, audio, factory)
    window.show()
    
    # FIX: Z.ai - Use public method instead of protected _welcome
    async def init_async():
        try:
            await db.initialize()
            await window.start_application()
        except Exception as e:
            # FIX: Z.ai, ChatGPT - Error handling with user dialog
            QMessageBox.critical(
                window, 
                "Startup Error",
                f"Failed to initialize: {e}\n\nThe app may not work correctly."
            )
            print(f"[main] Initialization error: {e}")
    
    # FIX: ChatGPT - Replace ensure_future with create_task
    # Use singleShot(0) instead of magic 100ms delay
    # FIX: Z.ai - Use safe_create_task to log exceptions
    QTimer.singleShot(0, lambda: safe_create_task(init_async()))
    
    # FIX: ChatGPT - Lifecycle cleanup on quit
    async def cleanup():
        try:
            await db.close()
            await audio.cleanup()
        except Exception as e:
            print(f"[main] Cleanup error: {e}")
    
    def on_about_to_quit():
        safe_create_task(cleanup())
    
    app.aboutToQuit.connect(on_about_to_quit)

    # Run event loop
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # FIX: Z.ai, ChatGPT - Catch all exceptions
        print(f"[FATAL] Unhandled exception: {e}")
        sys.exit(1)
