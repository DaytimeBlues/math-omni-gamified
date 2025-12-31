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
from core.hint_engine import RuleBasedHintEngine
from core.problem_factory import ProblemFactory
from core.sfx import SFX
from ui.game_manager import GameManager
from core.utils import safe_create_task
from core.container import ServiceContainer
from ui.premium_ui import MASTER_STYLESHEET


def create_stylesheet() -> str:
    """
    Generate stylesheet dynamically from config values.
    Now uses MASTER_STYLESHEET from premium_ui for Omni Kids design.
    """
    return MASTER_STYLESHEET


def main():
    """
    Entry point using qasync.
    
    WHY QASYNC?
    - UI must never freeze while audio generates
    - Kids will rage-tap if app appears frozen
    """
    # FIX: Z.ai - High DPI awareness
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
    
    # FIX: LLM Review - Force Fusion style for predictable QSS
    # Native Windows style fights stylesheets, Fusion is consistent
    app.setStyle("Fusion")
    
    # FIX: LLM Review - Set app font explicitly (no Comic Sans fallback!)
    # If Lexend isn't installed, falls back to Segoe UI (neutral)
    from PyQt6.QtGui import QFont
    app.setFont(QFont(FONT_FAMILY, 12))
    
    # qasync bridges Qt's event loop with asyncio
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # FIX: Apply dynamic stylesheet from config
    app.setStyleSheet(create_stylesheet())
    
    # --- Phase 2: Service Container ---
    # Create services instances
    db_service = DatabaseService()
    audio_service = AudioService()
    
    container = ServiceContainer()
    container.register(DatabaseService, db_service)
    container.register(AudioService, audio_service)
    container.register(ProblemFactory, ProblemFactory())
    container.register(RuleBasedHintEngine, RuleBasedHintEngine())
    
    # Init Game Manager with Container
    window = GameManager(container)
    window.show()
    
    # FIX: Z.ai - Use public method instead of protected _welcome
    async def init_async():
        try:
            await db_service.initialize()
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
            await db_service.close()
            await audio_service.cleanup()
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
