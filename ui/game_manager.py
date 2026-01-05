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
import logging
from typing import Optional, Union, Set

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMenu
from PyQt6.QtGui import QAction, QKeySequence

logger = logging.getLogger(__name__)

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
from ui.progress_report_view import ProgressReportView
from core.progress_report import ProgressReportGenerator
from ui.landing_page_view import LandingPageView

# Z.ai Fix: Valid modes for input validation
VALID_MODES = {"counting", "addition", "subtraction", "patterns", "measurement", "data"}


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
        
        # World Configuration (string modes match ProblemFactory)
        self.current_world_mode = "counting"  # "counting", "addition", "subtraction"
        
        # State
        self.current_level = None
        self.current_eggs = 0
        self.is_practice_mode = False
        self._initialized = False
        self._wrong_attempts = 0
        self._current_item_name = None  # For VoiceBank item lookup
        self._pending_tasks: set[asyncio.Task] = set()
        self._hint_timer: Optional[QTimer] = None
        
        # User Profile (Persistence)
        from core.user_profile import StudentProfile
        self.profile = StudentProfile.load()
        self.current_eggs = self.profile.eggs
        self.factory.set_profile(self.profile)
        
        # Hint Engine (Rule-Based, No AI)
        self.hint_engine = self.container.resolve(RuleBasedHintEngine)
        
        # Voice Bank - Cursor DI Fix: Resolve from container instead of direct instantiation
        self.voice_bank = container.resolve(VoiceBank)
        self.audio.set_voice_stop_callback(self.voice_bank.stop)
        
        # State tracking
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create views (Inject Director)
        self.landing_view = LandingPageView(self.profile)
        self.map_view = MapView(self.db)
        self.activity_view = ActivityView(self.director, self.audio) 
        
        self.stack.addWidget(self.landing_view)
        self.stack.addWidget(self.map_view)
        self.stack.addWidget(self.activity_view)
        
        # Celebration Overlay
        self.celebration = CelebrationOverlay(self)
        
        # Connect signals
        self.landing_view.domain_selected.connect(self._on_domain_selected)
        self.map_view.level_selected.connect(self._start_level)
        self.activity_view.back_to_map.connect(self._show_map)
        self.activity_view.answer_submitted.connect(self._process_answer)
        
        # Reports
        self.report_gen = ProgressReportGenerator(self.profile)
        self._setup_menus()
        
        # Start at landing page
        self.stack.setCurrentWidget(self.landing_view)
        self.director.set_state(AppState.IDLE)

    def resizeEvent(self, event):
        """Ensure overlay covers entire window on resize."""
        self.celebration.resize(self.size())
        super().resizeEvent(event)

    def _track_task(self, coro) -> asyncio.Task:
        """
        Create and track an asyncio task to allow cancellation.
        Z.ai Fix: Better exception logging for failed tasks.
        """
        task = asyncio.create_task(coro)
        self._pending_tasks.add(task)
        
        def cleanup(t):
            self._pending_tasks.discard(t)
            if not t.cancelled():
                exc = t.exception()
                if exc:
                    logger.error("Background task failed", exc_info=exc)
        
        task.add_done_callback(cleanup)
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
    
    def _compute_difficulty(self, level: int) -> int:
        """
        Compute difficulty score from level number.
        Difficulty is 0-indexed (level 1 = difficulty 0).
        """
        return max(0, level - 1)
    
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

    def _setup_menus(self):
        """Setup application menus (Progress Reports)."""
        menu_bar = self.menuBar()
        report_menu = menu_bar.addMenu("📊 Reports")
        
        daily_action = QAction("Daily Summary", self)
        daily_action.triggered.connect(lambda: self.show_report("daily"))
        report_menu.addAction(daily_action)
        
        weekly_action = QAction("Weekly Progress", self)
        weekly_action.triggered.connect(lambda: self.show_report("weekly"))
        report_menu.addAction(weekly_action)
        
        skills_action = QAction("Skills Breakdown", self)
        skills_action.triggered.connect(lambda: self.show_report("skills"))
        report_menu.addAction(skills_action)

    def show_report(self, report_type: str):
        """Show report dialog."""
        print(f"[GameManager] ACTION: Opening Report View ({report_type})")
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Progress Report - {report_type.title()}")
        dialog.setMinimumSize(900, 700)
        
        layout = QVBoxLayout(dialog)
        report_view = ProgressReportView(self.profile, dialog)
        report_view.report_generator = self.report_gen
        layout.addWidget(report_view)
        
        # Initial trigger
        if report_type == "daily": report_view.generate_daily_report()
        elif report_type == "weekly": report_view.generate_weekly_report()
        elif report_type == "skills": report_view.generate_skills_report()
        
        dialog.exec()

    def _on_domain_selected(self, domain_key: str):
        """
        Handle domain selection from Landing Page.
        Maps curriculum domains to math modes and shows the map view.
        """
        print(f"[GameManager] ACTION: Domain selected: {domain_key}")
        
        # 1. Play 'Mission Start' sequence (Sidereal Voyager Edition)
        import random
        mission_lines = [
            "Mission start! Welcome to the hub—let’s find some numbers together.",
            "Engines on. Explorer is ready—let’s count and discover.",
            "New mission unlocked. Show me the next constellation!"
        ]
        self._track_task(self.voice_bank.play_random_async(random.choice(mission_lines)))

        # Map domain to internal mode
        domain_mode_map = {
            "counting": "counting",
            "number": "counting",
            "addition": "addition",
            "subtraction": "subtraction",
            "patterns": "patterns",
            "measurement": "measurement",
            "data": "data",
        }
        
        self.current_world_mode = domain_mode_map.get(domain_key, "counting")
        self._track_task(self._show_domain_map(domain_key))

    async def _show_domain_map(self, domain_key: str):
        """Show map view configured for the selected domain."""
        await self.map_view.refresh(self.current_eggs)
        # Future: self.map_view.set_domain(domain_key)
        self.stack.setCurrentWidget(self.map_view)
        self.director.set_state(AppState.IDLE)
    
    # ==========================================================================
    # PRIVATE METHODS
    # ==========================================================================
    
    async def _welcome(self):
        """Welcome message and initial data load."""
        self.current_eggs = await self.db.get_eggs()
        await self.map_view.refresh(self.current_eggs)
        
        # Refresh landing page with progress data (synchronous method)
        self.landing_view.refresh(self.current_eggs)
        
        self.director.set_state(AppState.TUTOR_SPEAKING)
        
        # Use premium voice bank for greeting - event-driven
        await self.voice_bank.play_random_async("welcome")
        
        self.director.set_state(AppState.IDLE)
    
    async def _play_audio_sequence(self, clips: list[str]):
        """Plays a list of clips in order, waiting for each."""
        for clip in clips:
            await self.voice_bank.play_random_async(clip)
            # Small gap for natural speech pacing
            await asyncio.sleep(0.2)
        
        self.director.set_state(AppState.INPUT_ACTIVE)

    def _start_level(self, level_or_mode: Union[int, str]):
        """Start a level or practice session."""
        self._cancel_pending()
        
        if isinstance(level_or_mode, str):
            # Z.ai Fix: Validate mode before using
            if level_or_mode not in VALID_MODES:
                logger.error("Invalid mode requested: %s", level_or_mode)
                return
            # Practice Mode Branch
            self.is_practice_mode = True
            self.current_level = 0
            self.current_mode = level_or_mode
            self.difficulty_score = 5  # Fixed mid-range difficulty for practice
            logger.info("Starting practice mode (%s)", self.current_mode)
        else:
            # Regular Level Branch
            self.is_practice_mode = False
            self.current_level = level_or_mode
            self.difficulty_score = self._compute_difficulty(level_or_mode)
            
        # Determine Mode based on level
            if level_or_mode > 20:
                self.current_mode = "subtraction"
            elif level_or_mode > 10:
                self.current_mode = "addition"
            else:
                self.current_mode = "counting"
            logger.info("Starting level %s (mode=%s, difficulty=%s)", self.current_level, self.current_mode, self.difficulty_score)

        self._wrong_attempts = 0  # Reset hints for new level

        # Generate problem via strategy
        data = self.factory.generate(self.difficulty_score, self.current_mode)
        self._current_item_name = data.item_name  # For VoiceBank lookup

        # Configure activity view
        self.activity_view.render_problem(
            level=self.current_level,
            eggs=self.current_eggs,
            problem=data,
        )
        
        # Switch view
        self.stack.setCurrentWidget(self.activity_view)
        
        # Speak prompt with proper state transitions (Codex fix)
        self.director.set_state(AppState.TUTOR_SPEAKING)
        self._track_task(self._play_audio_sequence(data.audio_sequence))
    
    def _process_answer(self, correct: bool, chosen: int, target: int):
        """Handle answer submission."""
        self.director.set_state(AppState.EVALUATING)
        
        if not correct:
            self._wrong_attempts += 1
            # Record error in profile
            if self.profile:
                self.profile.record_error(target, chosen, self.current_mode)
                # Only save if not in practice mode
                if not self.is_practice_mode:
                    self.profile.save()
            
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
        if self.is_practice_mode:
            print(f"[GameManager] SUCCESS: Practice complete. Skipping economy updates.")
            self.activity_view.show_reward(0, self.current_eggs)
        else:
            # 1. Economy
            self.current_eggs = await self.db.add_eggs(REWARD_CORRECT)
            
            # Sync to profile
            self.profile.eggs = self.current_eggs
            self.profile.progress[self.current_mode] = max(self.profile.progress.get(self.current_mode, 1), self.current_level)
            self.profile.save()
            
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
        msg = f"LEVEL {self.current_level} COMPLETE!" if not self.is_practice_mode else "PRACTICE COMPLETE!"
        self.celebration.start(msg)
        
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

    def _show_landing(self):
        """Return to landing page (Year 1 Curriculum Hub)."""
        self._cancel_pending()
        self.celebration.stop()
        self._track_task(self.landing_view.refresh(self.current_eggs))
        self.stack.setCurrentWidget(self.landing_view)
        self.director.set_state(AppState.IDLE)
        

    async def _announce_level_legacy(self, level: int, item_name: str) -> None:
        """Legacy announcer for simple counting."""
        # 1. Level Start phrase
        await self.voice_bank.play_random_async("level_start")
        
        # 2. Item-specific question 
        item_category = f"items_{item_name}"
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
        hint = self.hint_engine.get_hint("counting", self._wrong_attempts)
        if hint:
            self._track_task(self._play_hint_and_resume(hint.message))
        else:
            self._resume_after_hint()
