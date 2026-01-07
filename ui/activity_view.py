"""
Activity View - Counting Question UI

Displays the problem, answer options, and handles input with debounce.
Uses JuicyButtons for tactile feedback (SFX).
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont

from config import (
    MIN_TOUCH_TARGET, BUTTON_GAP, DEBOUNCE_DELAY_MS,
    FONT_FAMILY, FONT_SIZE_BODY, FONT_SIZE_HEADING, COLORS
)
from ui.components import JuicyButton, JuicyLabel, SkipOverlay
from core.sfx import SFX
from core.director import AppState


class ActivityView(QWidget):
    """
    Question/answer activity view with rage-click protection.
    
    SAFETY FEATURES:
    - 96px minimum button size
    - 300ms debounce after click
    - Visual feedback on selection
    - SFX feedback via JuicyButtons
    """
    
    # Signals
    answer_submitted = Signal(bool)  # True = correct
    back_to_map = Signal()
    
    
    def __init__(self, director, audio_service=None):
        super().__init__()
        self.director = director
        self.audio = audio_service
        self._correct_answer = None
        self._interaction_locked = False
        
        # Connect to Director
        self.director.state_changed.connect(self._on_state_change)
        
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._unlock_interaction)
        
        self._build_ui()
        
        # Z.ai Fix: Skip overlay for tap-to-skip during blocked states
        # Import here to avoid circular dependency
        self._skip_overlay = SkipOverlay(self, self.director)
    
    def _build_ui(self):
        """Construct the activity UI."""
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QHBoxLayout()
        
        # Back Button with Click Sound
        back_btn = JuicyButton("← Map", self.audio, SFX.CLICK)
        back_btn.setFont(QFont(FONT_FAMILY, 16))
        back_btn.setFixedSize(100, 50)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border-radius: 10px;
            }}
        """)
        back_btn.clicked.connect(self.back_to_map.emit)
        header.addWidget(back_btn)
        
        header.addStretch()
        
        self.level_label = QLabel("Level 1")
        self.level_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_HEADING, QFont.Weight.Bold))
        header.addWidget(self.level_label)
        
        header.addStretch()
        
        # Juicy Egg Label (Animated)
        self.egg_label = JuicyLabel("🥚 0")
        self.egg_label.set_base_font_size(24) # Slightly larger than body
        self.egg_label.setFont(QFont(FONT_FAMILY, 24))
        header.addWidget(self.egg_label)
        
        layout.addLayout(header)
        
        # Question
        self.question_label = QLabel("How many?")
        self.question_label.setFont(QFont(FONT_FAMILY, 32, QFont.Weight.Bold))
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.question_label)
        
        # Visual display (emojis to count)
        self.visual_label = QLabel("🍎")
        self.visual_label.setFont(QFont("Segoe UI Emoji", 48))
        self.visual_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visual_label.setStyleSheet("padding: 40px;")
        self.visual_label.setWordWrap(True)
        layout.addWidget(self.visual_label)
        
        # Answer buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(BUTTON_GAP)
        buttons_layout.addStretch()
        
        self._option_buttons = []
        for i in range(3):
            # Initially no sound assigned, we set it dynamically or use default 'click'
            # For answer buttons, we might want to manually play correct/wrong LATER,
            # so we let the button handle the 'click' sound unless we override logic.
            # But here we want custom sounds for correct/wrong.
            # So let's use 'click' for immediate feedback, then overlay correct/wrong.
            # actually better: play NO sound here, and play result sound in handler?
            # User requested immediate tactile. "Click" is good for touch registration.
            btn = JuicyButton("?", self.audio, SFX.CLICK) 
            btn.setFixedSize(MIN_TOUCH_TARGET, MIN_TOUCH_TARGET)
            btn.setFont(QFont(FONT_FAMILY, 28, QFont.Weight.Bold))
            btn.setStyleSheet(self._option_style())
            # Use specific connection to receive the object
            btn.clicked.connect(lambda checked, b=btn: self._on_option_clicked(b))
            self._option_buttons.append(btn)
            buttons_layout.addWidget(btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # Feedback
        self.feedback_label = QLabel("Tap the correct number!")
        self.feedback_label.setFont(QFont(FONT_FAMILY, FONT_SIZE_BODY))
        self.feedback_label.setStyleSheet("color: #555555;")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.feedback_label)
        
        layout.addStretch()
    
    def _option_style(self, state: str = "normal") -> str:
        """Get button stylesheet based on state."""
        if state == "correct":
            return f"""
                QPushButton {{
                    background-color: {COLORS['success']};
                    color: white;
                    border-radius: 48px;
                    border: 4px solid #2E7D32;
                }}
            """
        elif state == "incorrect":
            return f"""
                QPushButton {{
                    background-color: {COLORS['error']};
                    color: white;
                    border-radius: 48px;
                    border: 4px solid #C62828;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border-radius: 48px;
                    border: 4px solid #1565C0;
                }}
                QPushButton:hover {{
                    background-color: #42A5F5;
                }}
                QPushButton:pressed {{
                    background-color: #1E88E5;
                    padding-top: 4px; /* Simulates press depth */
                }}
            """
    
    def set_activity(self, level: int, prompt: str, options: list,
                     correct_answer: int, host_text: str, emoji: str, eggs: int):
        """Configure the activity for a new problem."""
        self._correct_answer = correct_answer
        self._interaction_locked = False
        
        self.level_label.setText(f"Level {level}")
        self.question_label.setText(prompt)
        self.egg_label.setText(f"🥚 {eggs}")
        
        # Create visual representation
        visual_text = (emoji + " ") * correct_answer
        self.visual_label.setText(visual_text)
        
        # Configure answer buttons
        for btn, value in zip(self._option_buttons, options):
            btn.setText(str(value))
            btn.setProperty("value", value)
            btn.setStyleSheet(self._option_style())
            btn.setEnabled(True)
            # Update audio service reference if it changed (unlikely but safe)
            btn.audio = self.audio
        
        self.feedback_label.setText("Tap the correct number!")
        self.feedback_label.setStyleSheet("color: #555555;")
    
    def _on_option_clicked(self, button: QPushButton):
        """Handle answer button click with debounce."""
        # Rage-click shield
        if self._interaction_locked:
            return
        
        value = button.property("value")
        if value is None or self._correct_answer is None:
            return
        
        # Lock immediately
        self._interaction_locked = True
        
        correct = (value == self._correct_answer)
        
        if correct:
            if self.audio: self.audio.play_sfx(SFX.SUCCESS)
            button.setStyleSheet(self._option_style("correct"))
            self.feedback_label.setText("🎉 Correct!")
            self.feedback_label.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold;")
            
            for btn in self._option_buttons:
                btn.setEnabled(False)
        else:
            if self.audio: self.audio.play_sfx(SFX.ERROR)
            button.setStyleSheet(self._option_style("incorrect"))
            self.feedback_label.setText("Oops! Try again.")
            self.feedback_label.setStyleSheet(f"color: {COLORS['error']};")
        
        self.answer_submitted.emit(correct)
    
    def reset_interaction(self):
        """Unlock UI for retry after debounce."""
        # Code Review Fix: Stop existing timer before starting new one to prevent race conditions
        self._debounce_timer.stop()
        self._debounce_timer.start(DEBOUNCE_DELAY_MS)
    
    def _unlock_interaction(self):
        """Re-enable button clicks."""
        self._interaction_locked = False
        for btn in self._option_buttons:
            if btn.isEnabled():
                btn.setStyleSheet(self._option_style())
    
    def show_reward(self, earned: int, total: int):
        """Display reward earned."""
        if self.audio: self.audio.play_sfx(SFX.LEVEL_COMPLETE)
        self.egg_label.setText(f"🥚 {total}")
        self.egg_label.pop() # Trigger Animation
        self.feedback_label.setText(f"🎉 +{earned} eggs!")

    def _on_state_change(self, state: AppState):
        """
        React to global state changes.
        
        Z.ai Fix: Use SkipOverlay instead of setEnabled(False) to allow tap-to-skip.
        """
        if state == AppState.INPUT_ACTIVE:
            self._skip_overlay.hide()
            self._set_buttons_enabled(True)
        elif state in (AppState.EVALUATING, AppState.TUTOR_SPEAKING, AppState.CELEBRATION):
            # Show skip overlay (catches taps without blocking them entirely)
            self._skip_overlay.show()
            self._set_buttons_enabled(False)
        elif state == AppState.IDLE:
            self._skip_overlay.hide()
            self._set_buttons_enabled(False)

    def _set_buttons_enabled(self, enabled: bool):
        """Enable/disable answer buttons without disabling entire widget."""
        for btn in self._option_buttons:
            btn.setEnabled(enabled)

    def show_visual_hint(self, hint_name: str):
        """
        Display a visual hint (e.g., pulsing animation on correct area).
        Stub for now - to be implemented with animations.
        """
        # TODO: Implement visual hints based on hint_name
        # Examples: "pulse_correct_area", "highlight_groups", "arrow_following"
        print(f"[ActivityView] Visual Hint: {hint_name}")


