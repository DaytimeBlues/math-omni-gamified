"""
Game Manager - Orchestrates the Gamified Learning Flow

Connects: Database (eggs), ProblemFactory (questions), AudioService (voice), UI (views)
Pattern: Reading Eggs style Map → Activity → Reward loop

FIXES APPLIED (AI Review):
- Added public start_application() method (Z.ai)
- Proper encapsulation - _welcome remains private (Z.ai)
- Safe task creation for background exceptions (Z.ai)
- Proper Director state transitions (Codex)
"""

import asyncio

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from config import MAP_LEVELS_COUNT, REWARD_CORRECT, REWARD_COMPLETION
from core.audio_service import AudioService
from core.container import ServiceContainer
from core.database import DatabaseService
from core.director import AppState, Director
from core.hint_engine import RuleBasedHintEngine
from core.problem_factory import ProblemFactory
from core.sfx import SFX
from core.utils import safe_create_task
from core.personalized_audio import PersonalizedAudio
from ui.premium_activity_view import PremiumActivityView as ActivityView  # Premium UI
from ui.celebration import CelebrationOverlay
from ui.premium_map_view import PremiumMapView as MapView  # Premium UI


class GameManager(QMainWindow):
    """
    Main game controller using QStackedWidget for view switching.
    Managed by 'Director' state machine.
    """
    
    def __init__(self, container: ServiceContainer):
        super().__init__()
        self.setWindowTitle("Math Omni v2 🥚")
        self.setMinimumSize(1280, 800)
        
        # Core Infrastructure
        self.container = container
        self.director = Director(container)
        
        # Resolve Services
        self.db = container.resolve(DatabaseService)
        self.audio = container.resolve(AudioService)
        self.factory = container.resolve(ProblemFactory)
        
        # State
        self.current_level = None
        self.current_eggs = 0
        self._initialized = False
        self._wrong_attempts = 0
        
        # Hint Engine (Rule-Based, No AI)
        self.hint_engine = RuleBasedHintEngine()
        
        # Personalized Audio (pre-generated clips for Aurelia)
        self.personalized = PersonalizedAudio()
        
        # UI Stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create views (Inject Director)
        self.map_view = MapView(self.db)
        self.activity_view = ActivityView(self.director, self.audio) 
        
        self.stack.addWidget(self.map_view)
        self.stack.addWidget(self.activity_view)
        
        # Celebration Overlay
        self.celebration = CelebrationOverlay(self)
        
        # Connect signals
        self.map_view.level_selected.connect(self._start_level)
        self.activity_view.back_to_map.connect(self._show_map)
        self.activity_view.answer_submitted.connect(self._process_answer)
        
        # Start at map
        self.stack.setCurrentWidget(self.map_view)
        self.director.set_state(AppState.IDLE)

    def resizeEvent(self, event):
        """Ensure overlay covers entire window on resize."""
        self.celebration.resize(self.size())
        super().resizeEvent(event)
    
    # ==========================================================================
    # PUBLIC API
    # ==========================================================================
    
    async def start_application(self) -> None:
        """
        Public initialization method.
        FIX: Z.ai - External code calls this instead of _welcome() directly.
        """
        if self._initialized:
            return
        self._initialized = True
        await self._welcome()
    
    # ==========================================================================
    # PRIVATE METHODS
    # ==========================================================================
    
    async def _welcome(self):
        """Welcome message and initial data load."""
        self.current_eggs = await self.db.get_eggs()
        await self.map_view.refresh(self.current_eggs)
        self.director.set_state(AppState.TUTOR_SPEAKING)
        
        # Use personalized greeting if available
        if self.personalized.has_clip("welcome"):
            self.personalized.play("welcome")
            await asyncio.sleep(2.5)  # Wait for clip to finish
        else:
            await self.audio.speak("Welcome to Math Omni! Let's count together!")
        
        self.director.set_state(AppState.IDLE)
    
    def _start_level(self, level: int):
        """Start a level - generate problem and show activity view."""
        self.current_level = level
        self._wrong_attempts = 0  # Reset hints for new level
        
        # Generate problem (0-indexed)
        data = self.factory.generate(level - 1)
        
        # Configure activity view
        self.activity_view.set_activity(
            level=level,
            prompt=data['prompt'],
            options=data['options'],
            correct_answer=data['target'],
            host_text=data['host'],
            emoji=data['emoji'],
            eggs=self.current_eggs
        )
        
        # Switch view
        self.stack.setCurrentWidget(self.activity_view)
        
        # Speak prompt with proper state transitions (Codex fix)
        self.director.set_state(AppState.TUTOR_SPEAKING)
        safe_create_task(self._announce_level(level, data['host']))
    
    def _process_answer(self, correct: bool):
        """Handle answer submission."""
        self.director.set_state(AppState.EVALUATING)
        
        if not correct:
            self._wrong_attempts += 1
            self.audio.play_sfx(SFX.ERROR)
            
            # Get hint from engine based on attempt count
            hint = self.hint_engine.get_hint("counting", self._wrong_attempts)
            if hint and hint.hint_type == "audio" and hint.message:
                safe_create_task(self._play_hint_and_resume(hint.message))
            elif hint and hint.hint_type == "visual":
                # Visual hints handled by ActivityView (pulse, highlight)
                self.activity_view.show_visual_hint(hint.name)
                self._resume_after_hint()
            else:
                safe_create_task(self._play_hint_and_resume("Let's try again!"))
            return
        
        # Success - run async handler
        safe_create_task(self._handle_success())
    
    async def _handle_success(self):
        """Async success handler - update economy, progress, audio."""
        # 1. Economy
        self.current_eggs = await self.db.add_eggs(REWARD_CORRECT)
        self.activity_view.show_reward(REWARD_CORRECT, self.current_eggs)
        
        # 2. Progress
        await self.db.unlock_level(self.current_level)
        
        # 3. Audio & Celebration
        self.audio.play_sfx(SFX.SUCCESS)
        self.director.set_state(AppState.TUTOR_SPEAKING)
        
        # Use personalized success clip if available
        if self.personalized.has_clip("great_job"):
            self.personalized.play_random_success()
            await asyncio.sleep(1.5)  # Wait for clip
        else:
            await self.audio.speak("Great job!")
        
        self.director.set_state(AppState.CELEBRATION)
        self.celebration.start(f"LEVEL {self.current_level} COMPLETE!")
        
        # 4. Wait for celebration (2.5s)
        await asyncio.sleep(2.5)
        self._show_map()
    
    def _show_map(self):
        """Return to map view."""
        self.celebration.stop()  # Ensure closed if skipped
        safe_create_task(self.map_view.refresh(self.current_eggs))
        self.stack.setCurrentWidget(self.map_view)
        self.director.set_state(AppState.IDLE)

    async def _announce_level(self, level: int, host_text: str) -> None:
        """Speak the level intro then enable input (Codex fix)."""
        await self.audio.speak(f"Level {level}. {host_text}")
        self.director.set_state(AppState.INPUT_ACTIVE)

    async def _play_hint_and_resume(self, message: str) -> None:
        """Speak a hint and return the UI to interactive state (Codex fix)."""
        self.director.set_state(AppState.TUTOR_SPEAKING)
        await self.audio.speak(message)
        self._resume_after_hint()

    def _resume_after_hint(self) -> None:
        """Unlock interaction and return to input-ready state (Codex fix)."""
        self.director.set_state(AppState.INPUT_ACTIVE)
        self.activity_view.reset_interaction()
