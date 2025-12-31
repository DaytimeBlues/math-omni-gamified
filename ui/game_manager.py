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
from core.voice_bank import VoiceBank, get_success_category, get_wrong_category, get_hint_category
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
        self._current_item_name = None  # For VoiceBank item lookup
        
        # Hint Engine (Rule-Based, No AI)
        self.hint_engine = self.container.resolve(RuleBasedHintEngine)
        
        # Voice Bank (Replacing PersonalizedAudio and robots)
        self.voice_bank = VoiceBank()
        
        # State tracking
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
        
        # Use premium voice bank for greeting
        duration = self.voice_bank.play_random("welcome")
        if duration > 0:
            await asyncio.sleep(duration)
        # No fallback needed - VoiceBank has 10 welcome clips
        
        self.director.set_state(AppState.IDLE)
    
    def _start_level(self, level: int):
        """Start a level - generate problem and show activity view."""
        self.current_level = level
        self._wrong_attempts = 0  # Reset hints for new level
        
        # Generate problem (0-indexed)
        data = self.factory.generate(level - 1)
        self._current_item_name = data['item_name']  # For VoiceBank lookup
        
        # Configure activity view
        self.activity_view.set_activity(
            level=level,
            prompt=data['prompt'],
            options=data['options'],
            correct_answer=data['target'],
            host_text=data['host'],
            emoji=data['emoji'],
            eggs=self.current_eggs,
            item_name=data['item_name']  # For VoiceBank
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
            
            # Use voice bank for encouragement
            category = get_wrong_category(self._wrong_attempts)
            duration = self.voice_bank.play_random(category)
            
            # Provide hint after encouragement
            if self._wrong_attempts <= 3:
                if duration > 0:
                    QTimer.singleShot(int(duration * 1000), lambda: self._process_hint_after_delay())
                else:
                    self._process_hint_after_delay()
            else:
                self._resume_after_hint()
            return
        
        # Success - run async handler
        safe_create_task(self._handle_success())
    
    async def _handle_success(self):
        """Async success handler - update economy, progress, audio."""
        # 1. Economy
        self.current_eggs = await self.db.add_eggs(REWARD_CORRECT)
        self.activity_view.show_reward(REWARD_CORRECT, self.current_eggs)
        
        # 2. Unlock level progress
        await self.db.unlock_level(self.current_level)
        
        # 3. Audio - Use premium voice bank
        self.director.set_state(AppState.CELEBRATION)
        
        # Success Feedback (from VoiceBank)
        category = get_success_category()
        duration = self.voice_bank.play_random(category)
        if duration > 0:
            await asyncio.sleep(duration)
        
        # Celebration audio
        duration = self.voice_bank.play_random("celebration_rewards")
        if duration > 0:
            await asyncio.sleep(duration)
        
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
        """Speak the level intro using VoiceBank only (no API needed)."""
        # 1. Level Start phrase
        duration = self.voice_bank.play_random("level_start")
        if duration > 0:
            await asyncio.sleep(duration)
        
        # 2. Item-specific question from VoiceBank
        item_category = f"items_{self._current_item_name}"
        duration = self.voice_bank.play_random(item_category)
        if duration > 0:
            await asyncio.sleep(duration)
        
        self.director.set_state(AppState.INPUT_ACTIVE)

    async def _play_hint_and_resume(self, message: str) -> None:
        """Speak a hint using VoiceBank only (no API needed)."""
        self.director.set_state(AppState.TUTOR_SPEAKING)
        
        # Use voice bank for hints
        cat = get_hint_category(self._wrong_attempts)
        duration = self.voice_bank.play_random(cat)
        
        if duration > 0:
            await asyncio.sleep(duration)
        # No fallback needed - VoiceBank has all hint clips
            
        self._resume_after_hint()

    def _resume_after_hint(self) -> None:
        """Unlock interaction and return to input-ready state (Codex fix)."""
        self.director.set_state(AppState.INPUT_ACTIVE)
        self.activity_view.reset_interaction()

    def _process_hint_after_delay(self) -> None:
        """Process hint after encouragement audio finishes."""
        hint = self.hint_engine.get_hint("counting", self._wrong_attempts)
        if hint:
            safe_create_task(self._play_hint_and_resume(hint.message))
        else:
            self._resume_after_hint()
