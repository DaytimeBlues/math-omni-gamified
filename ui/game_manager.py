"""
Game Manager - Orchestrates the Gamified Learning Flow

Connects: Database (eggs), ProblemFactory (questions), AudioService (voice), UI (views)
Pattern: Reading Eggs style Map → Activity → Reward loop

FIXES APPLIED (AI Review):
- Added public start_application() method (Z.ai)
- Proper encapsulation - _welcome remains private (Z.ai)
- Safe task creation for background exceptions (Z.ai)
"""

import asyncio
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtCore import QTimer

from config import MAP_LEVELS_COUNT, REWARD_CORRECT, REWARD_COMPLETION
from ui.map_view import MapView
from ui.activity_view import ActivityView
from ui.celebration import CelebrationOverlay
from core.utils import safe_create_task


class GameManager(QMainWindow):
    """
    Main game controller using QStackedWidget for view switching.
    
    FLOW:
    1. Start → MapView (select level)
    2. MapView → ActivityView (answer questions)
    3. Correct Answer → Reward → MapView
    """
    
    def __init__(self, db, audio, factory):
        super().__init__()
        self.setWindowTitle("Math Omni v2 🥚")
        self.setMinimumSize(1280, 800)
        
        # Services (injected)
        self.db = db
        self.audio = audio
        self.factory = factory
        
        # State
        self.current_level = None
        self.current_eggs = 0
        self._initialized = False
        
        # UI Stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create views
        self.map_view = MapView(db)
        self.activity_view = ActivityView(audio) # Pass audio to activity
        
        self.stack.addWidget(self.map_view)
        self.stack.addWidget(self.activity_view)
        
        # Celebration Overlay (Child of Window, top Z-order)
        self.celebration = CelebrationOverlay(self)
        
        # Connect signals
        self.map_view.level_selected.connect(self._start_level)
        self.activity_view.back_to_map.connect(self._show_map)
        self.activity_view.answer_submitted.connect(self._process_answer)
        
        # Start at map
        self.stack.setCurrentWidget(self.map_view)

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
        await self.audio.speak("Welcome to Math Omni! Let's count together!")
    
    def _start_level(self, level: int):
        """Start a level - generate problem and show activity view."""
        self.current_level = level
        
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
        
        # Speak prompt
        safe_create_task(
            self.audio.speak(f"Level {level}. {data['host']}")
        )
    
    def _process_answer(self, correct: bool):
        """Handle answer submission."""
        if not correct:
            self.activity_view.reset_interaction()
            safe_create_task(self.audio.speak("Let's try again!"))
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
        await self.audio.speak("Great job!")
        self.celebration.start(f"LEVEL {self.current_level} COMPLETE!")
        
        # 4. Wait for celebration (2.5s)
        await asyncio.sleep(2.5)
        self._show_map()
    
    def _show_map(self):
        """Return to map view."""
        self.celebration.stop() # Ensure closed if skipped
        safe_create_task(self.map_view.refresh(self.current_eggs))
        self.stack.setCurrentWidget(self.map_view)
