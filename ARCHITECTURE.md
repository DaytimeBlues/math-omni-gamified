# Math Omni v2 — Comprehensive Multi-Platform Code Review Reference Guide (Integrated)

## Executive Summary
This document contains the complete source code and technical documentation for **Math Omni v2**. It integrates critical fixes from Google AI Studio, Z.ai, ChatGPT, and DeepSeek reviews, specifically addressing the **cross-platform audio support** and **async exception handling**.

## 1. Verified Implementation Status

| Feature | Status | Notes |
| :--- | :--- | :--- |
| **Audio Backend** | ✅ **QtMultimedia** | Replaced PowerShell subprocess. NOW CROSS-PLATFORM. |
| **Async Task Safety** | ✅ **Safe Task Helper** | `safe_create_task` wrapper logs all background exceptions. |
| **Encapsulation** | ✅ **Public API** | `start_application` is public, `_welcome` is protected. |
| **Styling** | ✅ **Dynamic** | Config-driven CSS extraction. |
| **Lifecycle** | ✅ **Hooks** | `aboutToQuit` triggers cleanup. |
| **Protocol** | ⏳ **Deferred** | Service protocols deferred to Phase 2. |

---

## 2. Complete Source Code

### `main.py`
```python
"""
Math Omni v2 - Gamified Learning Platform
Entry point using qasync for async Qt operations
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
        QPushButton:hover {{ opacity: 0.9; }}
        QPushButton:disabled {{
            background-color: {COLORS['locked']};
            color: #888888;
        }}
    """

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
    
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    app.setStyleSheet(create_stylesheet())
    
    db = DatabaseService()
    audio = AudioService()
    factory = ProblemFactory()
    
    window = GameManager(db, audio, factory)
    window.show()
    
    async def init_async():
        try:
            await db.initialize()
            await window.start_application()
        except Exception as e:
            QMessageBox.critical(window, "Startup Error", f"Failed: {e}")
            print(f"[main] Initialization error: {e}")
    
    QTimer.singleShot(0, lambda: safe_create_task(init_async()))
    
    async def cleanup():
        try:
            await db.close()
            await audio.cleanup()
        except Exception as e:
            print(f"[main] Cleanup error: {e}")
    
    app.aboutToQuit.connect(lambda: safe_create_task(cleanup()))
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[FATAL] Unhandled exception: {e}")
        sys.exit(1)
```

### `core/audio_service.py` (CROSS-PLATFORM UPDATED)
```python
"""
Async Audio Service - Cross-Platform QtMultimedia

Uses edge-tts for neural voice synthesis and QMediaPlayer for playback.
Replaces previous Windows-specific PowerShell implementation.
"""
import os
import hashlib
import asyncio
import edge_tts
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, QObject

CACHE_DIR = os.path.join("cache", "audio")

class AudioService(QObject):
    def __init__(self):
        super().__init__()
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.voice = "en-US-JennyNeural"
        
        # Qt Audio Setup
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        self._playback_future = None
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.errorOccurred.connect(self._on_error)

    async def speak(self, text: str):
        if not text: return
            
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.stop()
            if self._playback_future and not self._playback_future.done():
                self._playback_future.cancel()
        
        try:
            filename = f"{hashlib.md5(text.encode()).hexdigest()}.mp3"
            filepath = os.path.join(CACHE_DIR, filename)
            abs_path = os.path.abspath(filepath)

            if not os.path.exists(filepath):
                communicate = edge_tts.Communicate(text, self.voice)
                await communicate.save(filepath)

            await self._play_audio(abs_path)
            
        except Exception as e:
            print(f"[AudioService] Error: {e}")
            if self._playback_future and not self._playback_future.done():
                try: self._playback_future.set_result(False)
                except: pass

    async def _play_audio(self, abs_path: str):
        self._playback_future = asyncio.Future()
        url = QUrl.fromLocalFile(abs_path)
        self.player.setSource(url)
        self.player.play()
        try:
            await self._playback_future
        except asyncio.CancelledError:
            self.player.stop()

    def _on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self._playback_future and not self._playback_future.done():
                try: self._playback_future.set_result(True)
                except: pass
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
             if self._playback_future and not self._playback_future.done():
                try: self._playback_future.set_exception(Exception("Invalid Media"))
                except: pass

    def _on_error(self):
        err = self.player.errorString()
        print(f"[AudioService] Error: {err}")
        if self._playback_future and not self._playback_future.done():
            try: self._playback_future.set_exception(Exception(f"QtPlayer Error: {err}"))
            except: pass
    
    async def cleanup(self) -> None:
        self.player.stop()
        if self._playback_future and not self._playback_future.done():
            self._playback_future.cancel()
```

### `core/utils.py` (NEW)
```python
"""
Core Utilities
"""
import asyncio
import traceback

def safe_create_task(coro):
    """
    Create an asyncio task that logs exceptions instead of swallowing them.
    """
    task = asyncio.create_task(coro)
    
    def log_exception(t):
        try:
            t.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[Background Task Error] Unhandled exception: {e}")
            traceback.print_exc()

    task.add_done_callback(log_exception)
    return task
```

### `ui/game_manager.py` (UPDATED)
```python
"""
Game Manager - Orchestrates the Gamified Learning Flow
"""
import asyncio
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from config import MAP_LEVELS_COUNT, REWARD_CORRECT
from ui.map_view import MapView
from ui.activity_view import ActivityView
from core.utils import safe_create_task

class GameManager(QMainWindow):
    def __init__(self, db, audio, factory):
        super().__init__()
        self.setWindowTitle("Math Omni v2 🥚")
        self.setMinimumSize(1280, 800)
        self.db = db
        self.audio = audio
        self.factory = factory
        self.current_eggs = 0
        self._initialized = False
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.map_view = MapView(db)
        self.activity_view = ActivityView()
        
        self.stack.addWidget(self.map_view)
        self.stack.addWidget(self.activity_view)
        
        self.map_view.level_selected.connect(self._start_level)
        self.activity_view.back_to_map.connect(self._show_map)
        self.activity_view.answer_submitted.connect(self._process_answer)
        
        self.stack.setCurrentWidget(self.map_view)
    
    async def start_application(self) -> None:
        if self._initialized: return
        self._initialized = True
        await self._welcome()
    
    async def _welcome(self):
        self.current_eggs = await self.db.get_eggs()
        await self.map_view.refresh(self.current_eggs)
        await self.audio.speak("Welcome to Math Omni! Let's count together!")
    
    def _start_level(self, level: int):
        self.current_level = level
        data = self.factory.generate(level - 1)
        
        self.activity_view.set_activity(
            level=level,
            prompt=data['prompt'],
            options=data['options'],
            correct_answer=data['target'],
            host_text=data['host'],
            emoji=data['emoji'],
            eggs=self.current_eggs
        )
        self.stack.setCurrentWidget(self.activity_view)
        safe_create_task(self.audio.speak(f"Level {level}. {data['host']}"))
    
    def _process_answer(self, correct: bool):
        if not correct:
            self.activity_view.reset_interaction()
            safe_create_task(self.audio.speak("Let's try again!"))
            return
        safe_create_task(self._handle_success())
    
    async def _handle_success(self):
        self.current_eggs = await self.db.add_eggs(REWARD_CORRECT)
        self.activity_view.show_reward(REWARD_CORRECT, self.current_eggs)
        await self.db.unlock_level(self.current_level)
        await self.audio.speak("Great job!")
        await asyncio.sleep(1.5)
        self._show_map()
    
    def _show_map(self):
        safe_create_task(self.map_view.refresh(self.current_eggs))
        self.stack.setCurrentWidget(self.map_view)
```

## 3. Review Summary
**Status:** All Critical Priority 1 issues from the cross-platform AI review are now **IMPLEMENTED and VERIFIED**.
1.  **Cross-Platform Audio:** Done (QtMultimedia).
2.  **Async Safety:** Done (`safe_create_task`).
3.  **Encapsulation/Arch:** Done.

**Next Steps (Phase 2):**
*   Service protocols.
*   Cache eviction logic.
*   WCAG Color Contrast verification.
