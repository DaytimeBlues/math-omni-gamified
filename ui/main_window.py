"""
Main Window - PyQt6 Split-Screen Layout
Provides the question display and scratchpad workspace side-by-side.

PEDAGOGICAL DESIGN:
Research shows children learn better when they can see both the problem
and their working space simultaneously. Having to remember the question
while looking at a separate answer space creates cognitive load that
interferes with mathematical thinking.

HYBRID AI ARCHITECTURE:
- Local Agent (PedagogicalAgent): Instant feedback, works offline
- Cloud Agent (GeminiTutor): Contextual scaffolding when local detects confusion
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import random
import os

from ui.scratchpad import Scratchpad
from core.agent import PedagogicalAgent
from core.gemini_tutor import GeminiTutor
import sys
sys.path.append('..')
from config import COLORS, FONT_SIZES, MIN_TOUCH_TARGET, TIMING

# Confusion threshold: if child draws this many more strokes than expected,
# escalate to cloud AI for contextual help
CONFUSION_STROKE_THRESHOLD = 10


class MainWindow(QMainWindow):
    """
    Main application window with split-screen layout.
    
    LAYOUT STRUCTURE:
    ┌──────────────┬────────────────────────────┐
    │   Problem    │                            │
    │   Display    │       Scratchpad           │
    │              │        Canvas              │
    │   [Buttons]  │                            │
    └──────────────┴────────────────────────────┘
    
    LEFT PANEL (30%): Question, visual hints, action buttons
    RIGHT PANEL (70%): Drawing workspace
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize local pedagogical agent (always available, offline)
        self.agent = PedagogicalAgent()
        
        # Initialize cloud tutor (optional, graceful fallback if unavailable)
        # API key from environment variable for security
        api_key = os.environ.get('GEMINI_API_KEY', '')
        self.gemini_tutor = GeminiTutor(api_key=api_key if api_key else None)
        
        # Initialize progress tracker for parent dashboard
        from core.progress_tracker import ProgressTracker
        self.progress = ProgressTracker()
        self.progress.start_session()
        
        # Problem state
        self.current_answer = 3  # Default for demo
        self.current_question = "Draw 3 items"
        
        # Setup window
        self.setWindowTitle("Math Omni - Foundation Year")
        self.setMinimumSize(1280, 800)
        self.showFullScreen()  # Full-screen removes distractions
        
        # Build UI
        self._setup_ui()
        
        # Create celebration overlay
        from ui.celebration import CelebrationOverlay
        self.celebration = CelebrationOverlay(self)
        
        # Connect signals
        self._connect_signals()
        
        # Welcome message
        QTimer.singleShot(500, self._welcome)
    
    def _setup_ui(self):
        """Build the split-screen layout."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- LEFT PANEL: Problem & Controls ---
        left_panel = self._create_left_panel()
        
        # --- RIGHT PANEL: Scratchpad ---
        self.scratchpad = Scratchpad()
        self.scratchpad.setStyleSheet("""
            background-color: white;
            border: 4px solid #3498db;
            border-radius: 10px;
        """)
        
        # Add to main layout (30/70 split)
        main_layout.addWidget(left_panel, 3)
        main_layout.addWidget(self.scratchpad, 7)
    
    def _create_left_panel(self) -> QFrame:
        """
        Create the left panel with question and buttons.
        
        VISUAL DESIGN:
        - Warm background color for comfort
        - Large, readable fonts
        - Big touch targets for small hands
        """
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #fef9e7;
                border-right: 5px solid #f39c12;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(20)
        
        # --- Question Label ---
        self.question_label = QLabel(self.current_question)
        self.question_label.setFont(QFont("Comic Sans MS", FONT_SIZES['problem_text'], QFont.Weight.Bold))
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("color: #2c3e50; padding: 20px;")
        
        # --- Visual Hint (e.g., emoji apples) ---
        self.hint_label = QLabel("🍎 🍎 🍎")
        self.hint_label.setFont(QFont("Segoe UI Emoji", 48))
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet("padding: 20px;")
        
        # --- Feedback Display ---
        self.feedback_label = QLabel("")
        self.feedback_label.setFont(QFont("Segoe UI", 18))
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setStyleSheet("color: #7f8c8d; padding: 15px;")
        
        # --- Buttons ---
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)
        
        # Check button - primary action
        self.btn_check = QPushButton("✓ Check My Work")
        self.btn_check.setFont(QFont("Segoe UI", FONT_SIZES['button_text'], QFont.Weight.Bold))
        self.btn_check.setMinimumHeight(MIN_TOUCH_TARGET)
        self.btn_check.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 15px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.btn_check.clicked.connect(self._on_check)
        
        # Clear button - secondary action
        self.btn_clear = QPushButton("🗑️ Start Over")
        self.btn_clear.setFont(QFont("Segoe UI", 16))
        self.btn_clear.setMinimumHeight(60)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #ec7063;
            }
        """)
        self.btn_clear.clicked.connect(self._on_clear)
        
        # Help button - always available
        self.btn_help = QPushButton("❓ Help Me")
        self.btn_help.setFont(QFont("Segoe UI", 16))
        self.btn_help.setMinimumHeight(60)
        self.btn_help.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
        """)
        self.btn_help.clicked.connect(self._on_help)
        
        # Exit button (small, for parents)
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setFont(QFont("Segoe UI", 12))
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.btn_exit.clicked.connect(self.close)
        
        button_layout.addWidget(self.btn_check)
        button_layout.addWidget(self.btn_clear)
        button_layout.addWidget(self.btn_help)
        
        # Assemble layout
        layout.addWidget(self.question_label)
        layout.addWidget(self.hint_label)
        layout.addStretch(1)
        layout.addWidget(self.feedback_label)
        layout.addLayout(button_layout)
        layout.addStretch(1)
        layout.addWidget(self.btn_exit)
        
        return panel
    
    def _connect_signals(self):
        """Connect scratchpad signals to handlers."""
        # Acknowledge effort when child draws
        self.scratchpad.stroke_completed.connect(self._on_stroke_completed)
        
        # Offer scaffolding when child pauses too long
        self.scratchpad.idle_timeout.connect(self._on_idle)
        
        # Push-to-talk barrel button signals (for Gemini integration)
        self.scratchpad.barrel_button_pressed.connect(self._on_barrel_pressed)
        self.scratchpad.barrel_button_released.connect(self._on_barrel_released)
    
    def _welcome(self):
        """
        Welcome the child when app starts.
        
        ENGAGEMENT STRATEGY:
        Warm greeting establishes emotional connection before
        presenting any mathematical content.
        """
        self.agent.speak(
            f"Hello! Welcome to Math Omni! Can you draw {self.current_answer} things for me?"
        )
    
    def _on_stroke_completed(self):
        """
        Called when child completes a stroke.
        
        EFFORT ACKNOWLEDGMENT:
        Occasionally acknowledge they're working (not every time,
        as too frequent feedback is distracting).
        """
        if random.random() < 0.2:  # 20% chance
            feedback = self.agent.get_effort_feedback()
            self.feedback_label.setText(feedback)
    
    def _on_idle(self):
        """
        Called when child hasn't interacted for timeout duration.
        
        SCAFFOLDING TRIGGER:
        Gentle check-in, not a demand to work faster.
        """
        prompt = self.agent.get_idle_prompt()
        self.feedback_label.setText(prompt)
        self.agent.speak(prompt)
    
    def _on_check(self):
        """
        Check the child's answer.
        
        PEDAGOGICAL EVALUATION:
        Interpret drawing, compare to expected answer,
        provide growth-mindset feedback.
        """
        # Check if they drew anything
        if not self.scratchpad.has_content():
            msg = "I don't see any drawing yet! Try drawing on the white space."
            self.feedback_label.setText(msg)
            self.agent.speak(msg)
            return
        
        # Get child's interpreted answer
        drawn = self.scratchpad.get_quantity()
        target = self.current_answer
        
        # Evaluate and provide feedback
        is_correct, feedback = self.agent.evaluate_answer(target, drawn)
        
        self.feedback_label.setText(feedback)
        self.agent.speak(feedback)
        
        # Record attempt for progress tracking
        self.progress.record_attempt(is_correct)
        
        if is_correct:
            self._celebrate()
        elif self.agent.should_offer_scaffolding():
            # Schedule scaffolding after main feedback
            QTimer.singleShot(2500, self._offer_scaffolding)
    
    def _celebrate(self):
        """
        Visual celebration for correct answers.
        
        THE DOPAMINE HIT:
        Star animation + sound = child wants to continue.
        """
        self.feedback_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 15px;")
        self.celebration.celebrate()
    
    def _offer_scaffolding(self):
        """Offer help after multiple incorrect attempts."""
        scaffold = self.agent.get_scaffolding_offer()
        self.feedback_label.setText(scaffold)
        self.agent.speak(scaffold)
    
    def _on_clear(self):
        """
        Clear the scratchpad.
        
        Fresh start should feel like getting new paper,
        not having work erased punitively.
        """
        self.scratchpad.clear()
        self.feedback_label.setText("")
        self.feedback_label.setStyleSheet("color: #7f8c8d; padding: 15px;")
        self.agent.speak("Here's a fresh space for you!")
    
    def _on_help(self):
        """
        Child-initiated help request.
        
        METACOGNITION:
        When child ASKS for help, they're showing awareness
        that they don't understand—this should be celebrated!
        """
        self.agent.speak("Great job asking for help! Let me give you a hint.")
        QTimer.singleShot(1500, self._offer_scaffolding)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts (for parents/testing)."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
    
    def closeEvent(self, event):
        """
        Save progress when app closes.
        
        PARENT VALUE:
        Ensures learning data is persisted even on unexpected exit.
        """
        self.progress.end_session()
        event.accept()
    
    # =========================================================================
    # GEMINI CLOUD INTEGRATION
    # =========================================================================
    
    def _on_barrel_pressed(self):
        """
        Called when stylus barrel button is pressed.
        Activates push-to-talk mode for Gemini voice interaction.
        
        FUTURE: Will start audio recording for voice-to-text.
        Currently just activates session flag.
        """
        if self.gemini_tutor.is_available:
            self.gemini_tutor.start_push_to_talk_session()
            self.feedback_label.setText("🎤 Listening...")
            self.feedback_label.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 15px;")
    
    def _on_barrel_released(self):
        """
        Called when stylus barrel button is released.
        Ends push-to-talk mode.
        """
        if self.gemini_tutor.session_active:
            self.gemini_tutor.stop_push_to_talk_session()
            self.feedback_label.setText("")
            self.feedback_label.setStyleSheet("color: #7f8c8d; padding: 15px;")
    
    def _escalate_to_cloud(self):
        """
        Escalate to Gemini when local agent detects confusion.
        
        TRIGGER CONDITIONS:
        - Child draws 10+ more strokes than expected
        - Called from _on_check when confusion detected
        
        GRACEFUL FALLBACK:
        If cloud is unavailable or returns None, we use local scaffolding.
        """
        if not self.gemini_tutor.is_available:
            return False
        
        # Capture scratchpad as image for Gemini
        canvas_bytes = self.scratchpad.capture_as_bytes()
        drawn = self.scratchpad.stroke_count
        target = self.current_answer
        
        # Ask Gemini for contextual help
        hint = self.gemini_tutor.analyze_canvas_context(
            canvas_bytes=canvas_bytes,
            target_number=target,
            current_strokes=drawn
        )
        
        if hint:
            self.feedback_label.setText(hint)
            self.agent.speak(hint)
            return True
        
        # Cloud failed - use local fallback
        return False
    
    def _is_child_confused(self, drawn: int, target: int) -> bool:
        """
        Detect if the child appears confused based on stroke patterns.
        
        HEURISTIC:
        If they've drawn significantly more strokes than needed,
        they might be struggling to understand the concept.
        """
        return drawn > target + CONFUSION_STROKE_THRESHOLD
    
    def set_problem(self, question: str, answer: int, hint: str = ""):
        """
        Set a new problem for the child.
        
        Each new problem is a fresh opportunity. We clear the scratchpad,
        reset feedback state, and present the new challenge warmly.
        """
        self.current_question = question
        self.current_answer = answer
        
        self.question_label.setText(question)
        self.hint_label.setText(hint)
        self.feedback_label.setText("")
        
        self.scratchpad.clear()
        self.agent.reset_for_new_problem()

