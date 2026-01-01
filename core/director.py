"""
Director - Application State Machine
v2: With Z.ai fixes for transition validation, race protection, and timeouts.

FIXES APPLIED (Z.ai Review):
1. Strict transition validation with _VALID_TRANSITIONS
2. Race protection with _is_transitioning flag
3. Watchdog timeout for TUTOR_SPEAKING (15s)
4. Audio ducking in state handlers
"""
import logging
from enum import Enum, auto
from typing import Dict, List

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer


class AppState(Enum):
    """Application states for the game loop."""
    IDLE = auto()           # Map view, no activity
    INPUT_ACTIVE = auto()   # Child can interact
    EVALUATING = auto()     # Processing answer
    TUTOR_SPEAKING = auto() # TTS playing
    CELEBRATION = auto()    # Success animation


class Director(QObject):
    """
    Central state machine for the application.
    
    Prevents race conditions and ensures valid state transitions.
    
    Z.ai Fixes:
    1. Transition validation (guard clauses)
    2. Race protection during transitions
    3. Watchdog timeout for TUTOR_SPEAKING
    4. Audio ducking coordination
    """
    
    state_changed = pyqtSignal(AppState)
    
    # Valid state transitions (Z.ai fix #1)
    # Updated: Added TUTOR_SPEAKING to IDLE transitions for welcome/announcements
    _VALID_TRANSITIONS: Dict[AppState, List[AppState]] = {
        AppState.IDLE: [AppState.INPUT_ACTIVE, AppState.TUTOR_SPEAKING],
        AppState.INPUT_ACTIVE: [AppState.EVALUATING, AppState.IDLE],
        AppState.EVALUATING: [AppState.INPUT_ACTIVE, AppState.CELEBRATION, AppState.TUTOR_SPEAKING],
        AppState.TUTOR_SPEAKING: [AppState.INPUT_ACTIVE, AppState.IDLE, AppState.CELEBRATION],
        AppState.CELEBRATION: [AppState.INPUT_ACTIVE, AppState.IDLE],
    }
    
    # Timeout for TUTOR_SPEAKING state (ms)
    TUTOR_TIMEOUT_MS = 15000
    
    def __init__(self, container):
        super().__init__()
        self.container = container
        self._current_state = AppState.IDLE
        self._is_transitioning = False  # Z.ai fix #2
        
        # Watchdog timer for TUTOR_SPEAKING (Z.ai fix #3)
        self._tutor_watchdog = QTimer(self)
        self._tutor_watchdog.setSingleShot(True)
        self._tutor_watchdog.timeout.connect(self._force_tutor_timeout)

    @property
    def current_state(self) -> AppState:
        return self._current_state

    @pyqtSlot(AppState)
    def set_state(self, new_state: AppState):
        """
        Transition to a new state with validation.
        
        Z.ai Fixes:
        - Validates transition is allowed
        - Prevents race conditions during transition
        - Starts/stops watchdog timers
        """
        # Z.ai fix #2: Prevent race conditions during transition
        if self._is_transitioning:
            logging.warning(f"[Director] Ignoring state request to {new_state} during transition")
            return
        
        # Skip if same state
        if self._current_state == new_state:
            return
        
        # Z.ai fix #1: Validate transition
        valid_targets = self._VALID_TRANSITIONS.get(self._current_state, [])
        if new_state not in valid_targets:
            logging.warning(f"[Director] Invalid transition: {self._current_state} -> {new_state}")
            return
        
        # Begin transition
        self._is_transitioning = True
        old_state = self._current_state
        self._current_state = new_state
        
        # Stop any active timers from previous state
        self._tutor_watchdog.stop()
        
        # State-specific handlers
        if new_state == AppState.TUTOR_SPEAKING:
            self._handle_tutor_start()
        elif new_state == AppState.INPUT_ACTIVE:
            self._handle_input_active()
        elif new_state == AppState.CELEBRATION:
            self._handle_celebration_start()
        
        # Emit signal
        self.state_changed.emit(new_state)
        
        # End transition
        self._is_transitioning = False
        
        logging.debug(f"[Director] {old_state.name} -> {new_state.name}")

    def _handle_tutor_start(self):
        """Called when entering TUTOR_SPEAKING state."""
        # Start watchdog timer (Z.ai fix #3)
        self._tutor_watchdog.start(self.TUTOR_TIMEOUT_MS)
        
        # Duck music audio
        try:
            from core.audio_service import AudioService
            audio = self.container.resolve(AudioService)
            audio.duck_music(True)
        except Exception:
            pass

    def _handle_input_active(self):
        """Called when entering INPUT_ACTIVE state."""
        # Restore music audio
        try:
            from core.audio_service import AudioService
            audio = self.container.resolve(AudioService)
            audio.duck_music(False)
        except Exception:
            pass

    def _handle_celebration_start(self):
        """Called when entering CELEBRATION state."""
        # Play celebration SFX is handled by GameManager
        pass

    def _force_tutor_timeout(self):
        """
        Watchdog timeout for TUTOR_SPEAKING (Z.ai fix #3).
        Forces return to INPUT_ACTIVE if audio hangs.
        """
        if self._current_state == AppState.TUTOR_SPEAKING:
            logging.warning("[Director] Tutor speech timed out, forcing INPUT_ACTIVE")
            # Reset transitioning flag in case it's stuck
            self._is_transitioning = False
            self.set_state(AppState.INPUT_ACTIVE)

    def force_skip(self):
        """
        External skip request (e.g., from tap-to-skip overlay).
        Used during TUTOR_SPEAKING or CELEBRATION.
        """
        if self._current_state in [AppState.TUTOR_SPEAKING, AppState.CELEBRATION]:
            logging.info(f"[Director] Skip requested from {self._current_state.name}")
            self._is_transitioning = False  # Allow transition
            self.set_state(AppState.INPUT_ACTIVE)
