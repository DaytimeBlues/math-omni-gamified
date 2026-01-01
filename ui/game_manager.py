"""
Game Manager - Orchestrates the Gamified Learning Flow

Connects: Database (eggs), ProblemFactory (questions), AudioService (voice), UI (views)
Pattern: Reading Eggs style Map → Activity → Reward loop

FIXES APPLIED (AI Review):
- Added public start_application() method (Z.ai)
- Proper encapsulation - _welcome remains private (Z.ai)
- Safe task creation for background exceptions (Z.ai)
- Proper Director state transitions (Codex)

PHASE 3 UPDATE:
- Refactored to use MathWorld enum instead of indices
- Support for Addition (W2) and Subtraction (W3) operations
- Operation-aware hint engine and audio prompts
"""

import asyncio
from typing import Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from config import MAP_LEVELS_COUNT, REWARD_CORRECT, REWARD_COMPLETION
from core.audio_service import AudioService
from core.container import ServiceContainer
from core.contracts import MathWorld, Operation, get_operation_for_world
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
        self.current_world: MathWorld = MathWorld.W1  # Default to counting
        self.current_operation: str = Operation.COUNTING.value
        self.current_eggs = 0
        self._initialized = False
        self._wrong_attempts = 0
        self._current_item_name = None  # For VoiceBank item lookup
        self._current_problem_data: Optional[dict] = None  # Full problem data
        self._pending_tasks: set[asyncio.Task] = set()
        self._hint_timer: Optional[QTimer] = None
        
        # Hint Engine (Rule-Based, No AI)
        self.hint_engine = self.container.resolve(RuleBasedHintEngine)
        
        # Voice Bank (Replacing PersonalizedAudio and robots)
        self.voice_bank = VoiceBank()
        self.audio.set_voice_stop_callback(self.voice_bank.stop)
        
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

    def _track_task(self, coro) -> asyncio.Task:
        """Create and track an asyncio task to allow cancellation."""
        task = asyncio.create_task(coro)
        self._pending_tasks.add(task)
        task.add_done_callback(lambda _t: self._pending_tasks.discard(_t))
        return task

    def _cancel_pending(self) -> None:
        """Cancel all pending tasks and stop any active timers/audio."""
        for task in list(self._pending_tasks):
            if not task.done():
                task.cancel()
        self._pending_tasks.clear()

        if self._hint_timer:
            self._hint_timer.stop()
            self._hint_timer = None

        self.voice_bank.stop()
        self.audio.duck_music(False)
    
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
        
        # Use premium voice bank for greeting - event-driven
        await self.voice_bank.play_random_async("welcome")
        
        self.director.set_state(AppState.IDLE)
    
    def _start_level(self, level: int, world: MathWorld = MathWorld.W1):
        """
        Start a level - generate problem and show activity view.
        
        Args:
            level: Level number within the world (1-10)
            world: MathWorld enum (W1=Counting, W2=Addition, W3=Subtraction)
        """
        self._cancel_pending()
        self.current_level = level
        self.current_world = world
        self.current_operation = get_operation_for_world(world)
        self._wrong_attempts = 0  # Reset hints for new level
        
        # Generate problem using world-aware factory method
        data = self.factory.generate_for_world(world, level)
        self._current_item_name = data['item_name']  # For VoiceBank lookup
        self._current_problem_data = data  # Store full problem data
        
        # Configure activity view with visual_config for Phase 3
        self.activity_view.set_activity(
            level=level,
            prompt=data['prompt'],
            options=data['options'],
            correct_answer=data['target'],
            host_text=data['host'],
            emoji=data['emoji'],
            eggs=self.current_eggs,
            item_name=data['item_name'],
            visual_config=data.get('visual_config', {}),  # Phase 3: visual mode
            operation=self.current_operation  # Phase 3: operation type
        )
        
        # Switch view
        self.stack.setCurrentWidget(self.activity_view)
        
        # Speak prompt with proper state transitions (Codex fix)
        self.director.set_state(AppState.TUTOR_SPEAKING)
        self._track_task(self._announce_level(level, data['host']))
    
    def _process_answer(self, correct: bool):
        """Handle answer submission."""
        self.director.set_state(AppState.EVALUATING)
        
        if not correct:
            self._wrong_attempts += 1
            self.audio.play_sfx(SFX.ERROR)
            
            # Use voice bank for encouragement
            category = get_wrong_category(self._wrong_attempts)
            
            # Provide hint after encouragement (event-driven)
            async def encouragement_flow():
                await self.voice_bank.play_random_async(category)
                if self._wrong_attempts <= 3:
                    self._process_hint_after_delay()
                else:
                    self._resume_after_hint()
            
            self._track_task(encouragement_flow())
            return
        
        # Success - run async handler
        self._track_task(self._handle_success())
    
    async def _handle_success(self):
        """Async success handler - update economy, progress, audio."""
        # 1. Economy
        self.current_eggs = await self.db.add_eggs(REWARD_CORRECT)
        self.activity_view.show_reward(REWARD_CORRECT, self.current_eggs)
        
        # 2. Unlock level progress
        await self.db.unlock_level(self.current_level)
        
        # 3. Audio - Use premium voice bank (event-driven)
        self.director.set_state(AppState.CELEBRATION)
        
        # Success Feedback
        category = get_success_category()
        await self.voice_bank.play_random_async(category)
        
        # Celebration audio
        await self.voice_bank.play_random_async("celebration_rewards")
        
        self.director.set_state(AppState.CELEBRATION)
        self.celebration.start(f"LEVEL {self.current_level} COMPLETE!")
        
        # 4. Wait for celebration (2.5s)
        await asyncio.sleep(2.5)
        self._show_map()
    
    def _show_map(self):
        """Return to map view with cancellation check."""
        self._cancel_pending()
        self.celebration.stop()  # Ensure closed if skipped
        self._track_task(self.map_view.refresh(self.current_eggs))
        self.stack.setCurrentWidget(self.map_view)
        self.director.set_state(AppState.IDLE)

    async def _announce_level(self, level: int, host_text: str) -> None:
        """Speak the level intro using event-driven VoiceBank signals."""
        # 1. Level Start phrase
        await self.voice_bank.play_random_async("level_start")
        
        # 2. Operation-specific introduction (Phase 3)
        if self.current_operation == Operation.ADDITION.value:
            # For addition: play world intro if first level, then item prompt
            if level == 1 and self.voice_bank.has_category("world_2_intro"):
                await self.voice_bank.play_random_async("world_2_intro")
            # Item-specific question for addition
            item_category = f"items_{self._current_item_name}"
            if self.voice_bank.has_category(item_category):
                await self.voice_bank.play_random_async(item_category)
        elif self.current_operation == Operation.SUBTRACTION.value:
            # For subtraction: play world intro if first level, then item prompt
            if level == 1 and self.voice_bank.has_category("world_3_intro"):
                await self.voice_bank.play_random_async("world_3_intro")
            # Item-specific question for subtraction
            item_category = f"items_{self._current_item_name}"
            if self.voice_bank.has_category(item_category):
                await self.voice_bank.play_random_async(item_category)
        else:
            # Default counting behavior
            item_category = f"items_{self._current_item_name}"
            if self.voice_bank.has_category(item_category):
                await self.voice_bank.play_random_async(item_category)
        
        self.director.set_state(AppState.INPUT_ACTIVE)

    async def _play_hint_and_resume(self, message: str) -> None:
        """Speak a hint using event-driven VoiceBank."""
        self.director.set_state(AppState.TUTOR_SPEAKING)
        
        # Use voice bank for hints
        cat = get_hint_category(self._wrong_attempts)
        await self.voice_bank.play_random_async(cat)
            
        self._resume_after_hint()

    def _resume_after_hint(self) -> None:
        """Unlock interaction and return to input-ready state (Codex fix)."""
        self.director.set_state(AppState.INPUT_ACTIVE)
        self.activity_view.reset_interaction()

    def _process_hint_after_delay(self) -> None:
        """Process hint after encouragement audio finishes."""
        # Use operation-aware hints (Phase 3)
        hint = self.hint_engine.get_hint(self.current_operation, self._wrong_attempts)
        if hint:
            self._track_task(self._play_hint_and_resume(hint.message))
        else:
            self._resume_after_hint()
