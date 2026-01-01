"""
Game Manager - Orchestrates the Gamified Learning Flow

Connects: Database (eggs), ProblemFactory (questions), AudioService (voice), UI (views)
Pattern: Reading Eggs style Map → Activity → Reward loop

FIXES APPLIED (AI Review):
- Added public start_application() method (Z.ai)
- Proper encapsulation - _welcome remains private (Z.ai)
- Safe task creation for background exceptions (Z.ai)
- Proper Director state transitions (Codex)

Phase 3 Updates:
- Uses MathWorld enum for world selection
- Supports Addition and Subtraction strategies
- Passes visual_config to ActivityView
"""

import asyncio
from typing import Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from config import MAP_LEVELS_COUNT, REWARD_CORRECT, REWARD_COMPLETION
from core.audio_service import AudioService
from core.container import ServiceContainer
from core.database import DatabaseService
from core.director import AppState, Director
from core.hint_engine import RuleBasedHintEngine
from core.problem_factory import ProblemFactory
from core.problem_strategy import MathWorld, VisualMode
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
    
    Phase 3: Supports multiple MathWorlds via enum-based selection.
    """
    
    # Level ranges for each MathWorld (can be configured)
    WORLD_LEVEL_RANGES = {
        MathWorld.COUNTING: (1, 10),      # Levels 1-10: Counting
        MathWorld.ADDITION: (11, 20),     # Levels 11-20: Addition
        MathWorld.SUBTRACTION: (21, 30),  # Levels 21-30: Subtraction
    }
    
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
        self.current_world: MathWorld = MathWorld.COUNTING  # Phase 3: Track current world
        self.current_eggs = 0
        self._initialized = False
        self._wrong_attempts = 0
        self._current_item_name = None  # For VoiceBank item lookup
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
    
    def _determine_world_for_level(self, level: int) -> MathWorld:
        """
        Determine which MathWorld a level belongs to.
        
        Uses WORLD_LEVEL_RANGES to map level numbers to worlds.
        Falls back to COUNTING for levels outside defined ranges.
        
        Args:
            level: 1-indexed level number
            
        Returns:
            MathWorld enum value
        """
        for world, (start, end) in self.WORLD_LEVEL_RANGES.items():
            if start <= level <= end:
                return world
        return MathWorld.COUNTING
    
    def _get_level_index_for_world(self, level: int, world: MathWorld) -> int:
        """
        Convert global level to 0-indexed world-relative level.
        
        Args:
            level: Global 1-indexed level number
            world: The MathWorld the level belongs to
            
        Returns:
            0-indexed level within the world
        """
        start, _ = self.WORLD_LEVEL_RANGES.get(world, (1, 10))
        return level - start
    
    def _start_level(self, level: int, world: Optional[MathWorld] = None):
        """
        Start a level - generate problem and show activity view.
        
        Phase 3: Uses MathWorld enum for world selection.
        
        Args:
            level: 1-indexed level number
            world: Optional MathWorld override (auto-detected if None)
        """
        self._cancel_pending()
        self.current_level = level
        self._wrong_attempts = 0  # Reset hints for new level
        
        # Phase 3: Determine world from level or use override
        self.current_world = world or self._determine_world_for_level(level)
        self.factory.set_world(self.current_world)
        
        # Get world-relative level index (0-based)
        level_idx = self._get_level_index_for_world(level, self.current_world)
        
        # Generate problem using strategy pattern
        data = self.factory.generate(level_idx, self.current_world)
        self._current_item_name = data['item_name']  # For VoiceBank lookup
        
        # Phase 3: Extract visual_config for activity view
        visual_config = data.get('visual_config', {
            'mode': 'scatter',
            'group_a': data['target'],
            'group_b': 0,
            'emoji': data['emoji'],
        })
        
        # Configure activity view with visual_config
        self.activity_view.set_activity(
            level=level,
            prompt=data['prompt'],
            options=data['options'],
            correct_answer=data['target'],
            host_text=data['host'],
            emoji=data['emoji'],
            eggs=self.current_eggs,
            item_name=data['item_name'],  # For VoiceBank
            visual_config=visual_config,  # Phase 3: New visual config
            world=self.current_world,  # Phase 3: Pass world info
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
        
        # 2. Item-specific question 
        item_category = f"items_{self._current_item_name}"
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

    def _get_hint_category_for_world(self) -> str:
        """Get hint category based on current MathWorld."""
        category_map = {
            MathWorld.COUNTING: "counting",
            MathWorld.ADDITION: "addition",
            MathWorld.SUBTRACTION: "subtraction",
        }
        return category_map.get(self.current_world, "counting")
    
    def _process_hint_after_delay(self) -> None:
        """Process hint after encouragement audio finishes."""
        hint_category = self._get_hint_category_for_world()
        hint = self.hint_engine.get_hint(hint_category, self._wrong_attempts)
        if hint:
            self._track_task(self._play_hint_and_resume(hint.message))
        else:
            self._resume_after_hint()
