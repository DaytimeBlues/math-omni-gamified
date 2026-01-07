"""
Math Omni v2 - Gamified Learning Platform
Entry point using qasync for async Qt operations

Target: 5-year-old children (Foundation Year)
Core Tech: PySide6 + qasync for non-blocking TTS

FIXES APPLIED (AI Review):
- Safe logging config fallback (ChatGPT 5.2)
- Child-safe "Oops" dialog with retry (ChatGPT 5.2)
- Global async exception handler (ChatGPT 5.2)
- Window disabled during init (ChatGPT 5.2)
- High DPI awareness (Z.ai)
"""

import sys
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Callable

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer, Qt
from qasync import QEventLoop

from config import FONT_FAMILY
from core.database import DatabaseService
from core.audio_service import AudioService
from core.hint_engine import RuleBasedHintEngine
from core.problem_factory import ProblemFactory
from ui.game_manager import GameManager
from core.utils import safe_create_task
from core.container import ServiceContainer
from ui.premium_ui import MASTER_STYLESHEET


logger = logging.getLogger(__name__)


# =============================================================================
# LOGGING SETUP (Finding 1: Safe Fallback)
# =============================================================================

def configure_logging() -> Path:
    """Configure rotating file logging (1MB max, 5 backups)."""
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(console_handler)
    root.addHandler(file_handler)
    
    logger.info("Logging initialized: %s", log_file.resolve())
    return log_file


def safe_configure_logging() -> Optional[Path]:
    """ChatGPT 5.2 Fix: Safe logging setup with fallback."""
    try:
        return configure_logging()
    except Exception:
        # Fallback: console-only logging, keep app alive
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).exception("Logging init failed; using basicConfig fallback")
        return None


# =============================================================================
# CHILD-SAFE ERROR DIALOGS (Finding 2)
# =============================================================================

def show_oops(parent, text: str, *, retry_coro: Optional[Callable] = None):
    """
    ChatGPT 5.2 Fix: Child-safe error dialog with optional retry.
    
    Uses friendly "Oops!" language instead of technical error messages.
    """
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Warning)
    box.setWindowTitle("Oops!")
    box.setText(text)

    retry_btn = None
    if retry_coro is not None:
        retry_btn = box.addButton("Try again", QMessageBox.ButtonRole.AcceptRole)
    box.addButton("Close", QMessageBox.ButtonRole.RejectRole)

    box.exec()

    if retry_btn is not None and box.clickedButton() == retry_btn:
        safe_create_task(retry_coro())
    else:
        parent.close()


def create_stylesheet() -> str:
    """Uses MASTER_STYLESHEET from premium_ui for Omni Kids design."""
    return MASTER_STYLESHEET


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """
    Entry point using qasync.
    
    WHY QASYNC?
    - edge-tts generates speech asynchronously
    - UI must never freeze while audio generates
    - Kids will rage-tap if app appears frozen
    """
    # ChatGPT 5.2 Fix: Safe logging with fallback
    log_file = safe_configure_logging()
    logger.info("Math Omni starting up... (log_file=%s)", log_file)
    
    # High DPI awareness
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
    
    # Force Fusion style for predictable QSS
    app.setStyle("Fusion")
    
    # Set app font explicitly
    from PySide6.QtGui import QFont
    app.setFont(QFont(FONT_FAMILY, 12))
    
    # qasync bridges Qt's event loop with asyncio
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Apply dynamic stylesheet
    app.setStyleSheet(create_stylesheet())
    
    # --- Service Container ---
    db_service = DatabaseService()
    audio_service = AudioService()
    
    container = ServiceContainer()
    container.register(DatabaseService, db_service)
    container.register(AudioService, audio_service)
    container.register(ProblemFactory, ProblemFactory())
    container.register(RuleBasedHintEngine, RuleBasedHintEngine())
    
    # Register VoiceBank for proper DI
    from core.voice_bank import VoiceBank
    container.register(VoiceBank, VoiceBank())
    
    # Init Game Manager with Container
    window = GameManager(container)
    
    # ChatGPT 5.2 Fix: Disable window during init to prevent premature taps
    window.setEnabled(False)
    window.show()
    
    # ChatGPT 5.2 Fix: Track if we've shown an error (prevent multiple dialogs)
    error_shown = {"flag": False}
    
    def child_safe_fatal(msg: str):
        """Show a single child-safe error message."""
        if error_shown["flag"]:
            return
        error_shown["flag"] = True
        show_oops(window, msg)
    
    # ChatGPT 5.2 Fix: Global async exception handler (Finding 3)
    def handle_async_exception(loop_ref, context):
        exc = context.get("exception")
        logger.error("Async exception: %s", context.get("message"), exc_info=exc)
        QTimer.singleShot(0, lambda: child_safe_fatal("Oops! Something went wrong."))
    
    loop.set_exception_handler(handle_async_exception)
    
    # ChatGPT 5.2 Fix: Global Python excepthook (Finding 3)
    def excepthook(exc_type, exc, tb):
        logger.critical("Unhandled exception", exc_info=(exc_type, exc, tb))
        QTimer.singleShot(0, lambda: child_safe_fatal("Oops! Something went wrong."))
    
    sys.excepthook = excepthook
    
    # ChatGPT 5.2 Fix: Async init with retry capability (Finding 2)
    async def init_async():
        try:
            await db_service.initialize()
            await window.start_application()
            window.setEnabled(True)  # Enable interaction after successful init
        except Exception:
            logger.exception("Startup initialization failed")
            window.setEnabled(False)
            QTimer.singleShot(0, lambda: show_oops(
                window,
                "Something went wrong. You can try again.",
                retry_coro=init_async
            ))
    
    QTimer.singleShot(0, lambda: safe_create_task(init_async()))
    
    # LLM Council Fix: Lifecycle cleanup on quit
    # CRITICAL: Use run_until_complete instead of safe_create_task
    # to ensure DB closes before event loop terminates.
    async def cleanup():
        try:
            await db_service.close()
            audio_service.cleanup()
            # Code Review Fix: Add VoiceBank cleanup
            voice_bank = container.resolve(VoiceBank)
            voice_bank.cleanup()
            logger.info("Cleanup completed successfully")
        except Exception:
            logger.exception("Cleanup failed")
    
    def on_about_to_quit():
        # LLM Council Fix: Synchronous wait to prevent race condition
        try:
            loop.run_until_complete(cleanup())
        except RuntimeError:
            # Loop already closed - best effort cleanup
            logger.warning("Event loop closed before cleanup could complete")
    
    app.aboutToQuit.connect(on_about_to_quit)

    # Run event loop
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception:
        logger.exception("Unhandled fatal error")
        sys.exit(1)
