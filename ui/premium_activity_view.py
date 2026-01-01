"""
Premium Activity View - "Reading Eggs" Quality Design

Claude's Implementation:
- Cream gradient background
- White rounded card for content
- Chunky 3D buttons with shadows
- Pill-shaped egg counter
- Generous whitespace

Phase 3 Updates:
- Supports visual_config schema with scatter, merge, take_away modes
- Dynamic visual rendering based on MathWorld
- Animated transitions for merge/take_away operations

Reference: The uploaded target design screenshot
"""

from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor

from config import (
    MIN_TOUCH_TARGET, BUTTON_GAP, DEBOUNCE_DELAY_MS,
    FONT_FAMILY, FONT_SIZE_BODY, FONT_SIZE_HEADING, COLORS
)
from core.sfx import SFX
from core.director import AppState


# =============================================================================
# PREMIUM STYLES (Matching Reference Design)
# =============================================================================

PREMIUM_BG = """
    background: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #FEF9E7,
        stop:0.5 #FAF0DC,
        stop:1 #F5E6C8
    );
"""

QUESTION_CARD_STYLE = """
    QFrame#QuestionCard {
        background-color: #FFFEF8;
        border-radius: 30px;
        padding: 30px;
    }
"""

EGG_COUNTER_STYLE = """
    QFrame#EggCounter {
        background-color: #FFF8E0;
        border: 3px solid #FFB347;
        border-radius: 25px;
        padding: 5px 15px;
    }
"""

BACK_BUTTON_STYLE = """
    QPushButton#BackButton {
        background-color: #FFB347;
        border-radius: 25px;
        border: none;
        color: #2C3E50;
        font-weight: bold;
    }
    QPushButton#BackButton:hover {
        background-color: #FFC464;
    }
    QPushButton#BackButton:pressed {
        background-color: #E69A2E;
    }
"""


def add_soft_shadow(widget, blur=25, offset_y=8, opacity=30):
    """Add a soft, premium drop shadow to any widget."""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(0, 0, 0, opacity))
    shadow.setOffset(0, offset_y)
    widget.setGraphicsEffect(shadow)


class PremiumAnswerButton(QPushButton):
    """
    A chunky 3D button matching the reference design.
    
    Features:
    - Rounded corners (25px radius)
    - Thick bottom border for depth
    - Soft shadow
    - Press animation
    """
    
    def __init__(self, text: str, audio=None, sfx_name=None, parent=None):
        super().__init__(text, parent)
        self._base_text = text
        self._audio = audio
        self._sfx_name = sfx_name
        self._state = "normal"
        
        # Size and font
        self.setFixedSize(150, 80)
        self.setFont(QFont(FONT_FAMILY, 32, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Apply default style
        self._apply_style("normal")
        
        # Add shadow
        add_soft_shadow(self, blur=20, offset_y=6, opacity=35)
    
    def _apply_style(self, state: str):
        """Apply button style based on state."""
        self._state = state
        
        if state == "correct":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #00C897;
                    color: white;
                    border: none;
                    border-bottom: 6px solid #009E77;
                    border-radius: 20px;
                    padding-bottom: 6px;
                }
            """)
        elif state == "incorrect":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    border: none;
                    border-bottom: 6px solid #E65A5A;
                    border-radius: 20px;
                    padding-bottom: 6px;
                }
            """)
        else:  # normal
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4DA8DA;
                    color: white;
                    border: none;
                    border-bottom: 6px solid #2B8BC0;
                    border-radius: 20px;
                    padding-bottom: 6px;
                }
                QPushButton:hover {
                    background-color: #64B5E3;
                }
                QPushButton:pressed {
                    background-color: #2B8BC0;
                    border-bottom: 2px solid #2B8BC0;
                    padding-bottom: 10px;
                }
            """)
    
    def set_status(self, status: str):
        """Set button status: 'normal', 'correct', 'incorrect'."""
        if status == "correct":
            self.setText(f"✓ {self._base_text}")
        elif status == "incorrect":
            self.setText(f"✗ {self._base_text}")
        else:
            self.setText(self._base_text)
        self._apply_style(status)
    
    def reset(self):
        """Reset to normal state."""
        self.setText(self._base_text)
        self._apply_style("normal")
    
    def mousePressEvent(self, event):
        """Play SFX on press if configured."""
        if self._audio and self._sfx_name:
            self._audio.play_sfx(self._sfx_name)
        super().mousePressEvent(event)


class PremiumActivityView(QWidget):
    """
    Premium Activity View matching the reference design.
    
    Phase 3: Supports multiple visual modes:
    - scatter: Items displayed in grouped rows (counting)
    - merge: Two groups shown, then combined (addition)
    - take_away: Full group shown, some fade out (subtraction)
    
    Layout:
    ┌────────────────────────────────────────┐
    │  [←]          Level 1          🥚 90   │  Header
    ├────────────────────────────────────────┤
    │                                        │
    │    ┌──────────────────────────────┐    │
    │    │     How many 🍎?             │    │  Question Card
    │    │                              │    │
    │    │     🍎 🍎 🍎                  │    │  Visual
    │    │                              │    │
    │    └──────────────────────────────┘    │
    │                                        │
    │         [2]  [3]  [4]                  │  Answer Buttons
    │                                        │
    │           Tap the answer!              │  Feedback
    └────────────────────────────────────────┘
    """
    
    answer_submitted = pyqtSignal(bool)
    back_to_map = pyqtSignal()
    
    def __init__(self, director, audio_service=None):
        super().__init__()
        self.director = director
        self.audio = audio_service
        self._correct_answer = None
        self._interaction_locked = False
        self._current_visual_config: Optional[Dict[str, Any]] = None
        self._current_world = None  # Track current MathWorld
        
        # Connect to Director
        self.director.state_changed.connect(self._on_state_change)
        
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._unlock_interaction)
        
        self._build_ui()
        self._skip_overlay = SkipOverlay(self, self.director)
    
    def _build_ui(self):
        """Build the premium UI."""
        # Gradient background
        self.setStyleSheet(PREMIUM_BG)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # --- HEADER ---
        header = self._build_header()
        main_layout.addLayout(header)
        
        # --- QUESTION CARD ---
        question_card = self._build_question_card()
        main_layout.addWidget(question_card, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # --- ANSWER BUTTONS ---
        buttons_layout = self._build_answer_buttons()
        main_layout.addLayout(buttons_layout)
        
        # --- FEEDBACK ---
        self.feedback_label = QLabel("Tap the correct number!")
        self.feedback_label.setFont(QFont(FONT_FAMILY, 18))
        self.feedback_label.setStyleSheet(f"color: {COLORS['text_light']}; background: transparent;")
        self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.feedback_label)
        
        main_layout.addStretch()
    
    def _build_header(self) -> QHBoxLayout:
        """Build header with back button, level, and egg counter."""
        header = QHBoxLayout()
        header.setSpacing(20)
        
        # Back Button (circular)
        back_btn = QPushButton("←")
        back_btn.setObjectName("BackButton")
        back_btn.setFixedSize(50, 50)
        back_btn.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
        back_btn.setStyleSheet(BACK_BUTTON_STYLE)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.back_to_map.emit)
        add_soft_shadow(back_btn, blur=15, offset_y=4, opacity=25)
        header.addWidget(back_btn)
        
        header.addStretch()
        
        # Level Label
        self.level_label = QLabel("Level 1")
        self.level_label.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        self.level_label.setStyleSheet(f"color: {COLORS['text']}; background: transparent;")
        header.addWidget(self.level_label)
        
        # Egg Counter (pill-shaped)
        egg_frame = QFrame()
        egg_frame.setObjectName("EggCounter")
        egg_frame.setStyleSheet(EGG_COUNTER_STYLE)
        egg_frame.setFixedHeight(50)
        add_soft_shadow(egg_frame, blur=12, offset_y=3, opacity=20)
        
        egg_layout = QHBoxLayout(egg_frame)
        egg_layout.setContentsMargins(10, 5, 15, 5)
        egg_layout.setSpacing(8)
        
        egg_icon = QLabel("🥚")
        egg_icon.setFont(QFont("Segoe UI Emoji", 24))
        egg_icon.setStyleSheet("background: transparent; border: none;")
        
        self.egg_label = QLabel("0")
        self.egg_label.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
        self.egg_label.setStyleSheet(f"color: {COLORS['accent_dark']}; background: transparent; border: none;")
        
        egg_layout.addWidget(egg_icon)
        egg_layout.addWidget(self.egg_label)
        
        header.addStretch()
        header.addWidget(egg_frame)
        
        return header
    
    def _build_question_card(self) -> QFrame:
        """Build the white rounded card for question display."""
        card = QFrame()
        card.setObjectName("QuestionCard")
        card.setStyleSheet(QUESTION_CARD_STYLE)
        card.setMinimumSize(500, 250)
        card.setMaximumWidth(700)
        add_soft_shadow(card, blur=30, offset_y=10, opacity=25)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(40, 30, 40, 30)
        
        # Question text
        self.question_label = QLabel("How many?")
        self.question_label.setFont(QFont(FONT_FAMILY, 28, QFont.Weight.Bold))
        self.question_label.setStyleSheet(f"color: {COLORS['text']}; background: transparent;")
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setWordWrap(True)
        card_layout.addWidget(self.question_label)
        
        # Visual display (emojis)
        self.visual_label = QLabel("🍎")
        self.visual_label.setFont(QFont("Segoe UI Emoji", 48))
        self.visual_label.setStyleSheet("background: transparent;")
        self.visual_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visual_label.setWordWrap(True)
        card_layout.addWidget(self.visual_label)
        
        return card
    
    def _build_answer_buttons(self) -> QHBoxLayout:
        """Build the answer button row."""
        layout = QHBoxLayout()
        layout.setSpacing(BUTTON_GAP)
        layout.addStretch()
        
        self._option_buttons = []
        for i in range(3):
            btn = PremiumAnswerButton("?", self.audio, SFX.CLICK)
            btn.clicked.connect(lambda checked, b=btn: self._on_option_clicked(b))
            self._option_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        return layout
    
    # ==========================================================================
    # ACTIVITY LOGIC (Same as original)
    # ==========================================================================
    
    def set_activity(self, level: int, prompt: str, options: list, 
                     correct_answer: int, host_text: str, emoji: str, eggs: int,
                     item_name: str = None, visual_config: Optional[Dict[str, Any]] = None,
                     world = None):
        """
        Configure the activity view for a new problem.
        
        Phase 3: Supports visual_config schema for different visual modes:
        - scatter: Traditional counting display (grouped rows)
        - merge: Two groups shown separately (addition)
        - take_away: Full group with some fading out (subtraction)
        
        Args:
            level: Level number to display
            prompt: Question prompt text
            options: List of answer options
            correct_answer: The correct answer value
            host_text: Text for voice prompt
            emoji: Emoji to display
            eggs: Current egg count
            item_name: Item name for VoiceBank lookup
            visual_config: Optional visual configuration dict
            world: Optional MathWorld enum for context
        """
        self._correct_answer = correct_answer
        self._interaction_locked = True  # Lock until audio finishes
        self._current_visual_config = visual_config
        self._current_world = world
        
        self.level_label.setText(f"Level {level}")
        self.question_label.setText(prompt)
        self.egg_label.setText(str(eggs))
        
        # Phase 3: Build visual based on visual_config mode
        if visual_config:
            visual = self._build_visual_from_config(visual_config)
        else:
            # Fallback to legacy grouped visual (counting)
            visual = self._build_grouped_visual(emoji, correct_answer)
        
        self.visual_label.setText(visual)
        
        # Adjust font size based on total item count
        total_items = self._get_total_items_from_config(visual_config, correct_answer)
        if total_items > 10:
            self.visual_label.setFont(QFont("Segoe UI Emoji", 32))  # Smaller
        elif total_items > 5:
            self.visual_label.setFont(QFont("Segoe UI Emoji", 40))  # Medium
        else:
            self.visual_label.setFont(QFont("Segoe UI Emoji", 48))  # Normal
        
        # Debug: verify visual matches answer
        mode = visual_config.get('mode', 'scatter') if visual_config else 'scatter'
        print(f"[Activity] Level {level} ({mode}): {correct_answer} {emoji}")
        
        # Reset and HIDE buttons until audio finishes
        for i, btn in enumerate(self._option_buttons):
            btn._base_text = str(options[i])
            btn.reset()
            btn.setVisible(False)  # Hide during audio
        
        self.feedback_label.setText("Listen carefully...")
    
    def _get_total_items_from_config(self, visual_config: Optional[Dict[str, Any]], 
                                      fallback: int) -> int:
        """Get total item count from visual_config for font sizing."""
        if not visual_config:
            return fallback
        
        mode = visual_config.get('mode', 'scatter')
        group_a = visual_config.get('group_a', fallback)
        group_b = visual_config.get('group_b', 0)
        
        if mode == 'merge':
            return group_a + group_b
        elif mode == 'take_away':
            return group_a  # Show full group before removal
        else:  # scatter
            return group_a
    
    def _build_visual_from_config(self, config: Dict[str, Any]) -> str:
        """
        Build visual display based on visual_config schema.
        
        Phase 3: Supports three modes:
        - scatter: Items in grouped rows (counting)
        - merge: Two groups with '+' operator (addition)
        - take_away: Full group with strikethrough/faded items (subtraction)
        
        Args:
            config: Visual configuration dictionary with mode, group_a, group_b, emoji
            
        Returns:
            Formatted string for visual_label
        """
        mode = config.get('mode', 'scatter')
        emoji = config.get('emoji', '🍎')
        group_a = config.get('group_a', 0)
        group_b = config.get('group_b', 0)
        
        if mode == 'scatter':
            return self._build_scatter_visual(emoji, group_a)
        elif mode == 'merge':
            return self._build_merge_visual(emoji, group_a, group_b)
        elif mode == 'take_away':
            return self._build_take_away_visual(emoji, group_a, group_b)
        else:
            # Unknown mode, fall back to scatter
            return self._build_scatter_visual(emoji, group_a)
    
    def _build_scatter_visual(self, emoji: str, count: int) -> str:
        """
        Build scatter mode visual (counting).
        Items displayed in grouped rows of 5 for subitizing.
        """
        return self._build_grouped_visual(emoji, count)
    
    def _build_merge_visual(self, emoji: str, group_a: int, group_b: int) -> str:
        """
        Build merge mode visual (addition).
        
        Shows two groups with a '+' between them:
        🍎 🍎 🍎  +  🍎 🍎
        """
        # Build first group
        part_a = " ".join([emoji] * group_a)
        
        # Build second group
        part_b = " ".join([emoji] * group_b)
        
        # Combine with plus sign
        return f"{part_a}  ➕  {part_b}"
    
    def _build_take_away_visual(self, emoji: str, total: int, removed: int) -> str:
        """
        Build take_away mode visual (subtraction).
        
        Shows full group with some items crossed out:
        🍎 🍎 🍎  ➖  ❌ ❌
        
        Or alternatively show remaining and removed:
        🍎 🍎 🍎 | 🍎 🍎 (faded)
        """
        remaining = total - removed
        
        # Show remaining items + minus sign + removed indicator
        remaining_part = " ".join([emoji] * remaining)
        removed_part = " ".join(["❌"] * removed)
        
        return f"{remaining_part}  ➖  {removed_part}"
    
    def _build_grouped_visual(self, emoji: str, count: int) -> str:
        """Build emoji display grouped in rows of 5 for easier counting."""
        if count <= 5:
            # Single row
            return " ".join([emoji] * count)
        
        # Multiple rows of 5
        rows = []
        remaining = count
        while remaining > 0:
            row_count = min(5, remaining)
            rows.append(" ".join([emoji] * row_count))
            remaining -= row_count
        
        return "\n".join(rows)
    
    def _on_option_clicked(self, button: PremiumAnswerButton):
        """Handle answer selection."""
        if self._interaction_locked:
            return
        
        self._interaction_locked = True
        self._debounce_timer.start(DEBOUNCE_DELAY_MS)
        
        answer = int(button._base_text)
        correct = (answer == self._correct_answer)
        
        # Update button appearance
        if correct:
            button.set_status("correct")
            self.feedback_label.setText("🎉 Correct!")
            self.feedback_label.setStyleSheet(f"color: {COLORS['success']}; background: transparent;")
        else:
            button.set_status("incorrect")
            self.feedback_label.setText("Try again!")
            self.feedback_label.setStyleSheet(f"color: {COLORS['error']}; background: transparent;")
        
        self.answer_submitted.emit(correct)
    
    def reset_interaction(self):
        """Reset for new attempt."""
        self._interaction_locked = False
        for btn in self._option_buttons:
            btn.reset()
        self.feedback_label.setText("Tap the correct number!")
        self.feedback_label.setStyleSheet(f"color: {COLORS['text_light']}; background: transparent;")
    
    def show_reward(self, earned: int, total: int):
        """Display reward earned."""
        if self.audio:
            self.audio.play_sfx(SFX.LEVEL_COMPLETE)
        self.egg_label.setText(str(total))
        self.feedback_label.setText(f"🎉 +{earned} eggs!")
    
    def _unlock_interaction(self):
        """Called after debounce timer expires."""
        pass  # Lock managed by Director now
    
    def _on_state_change(self, state: AppState):
        """Handle Director state changes."""
        if state == AppState.INPUT_ACTIVE:
            self._skip_overlay.hide()
            self._set_buttons_enabled(True)
        elif state in (AppState.EVALUATING, AppState.TUTOR_SPEAKING, AppState.CELEBRATION):
            self._skip_overlay.show()
            self._set_buttons_enabled(False)
        elif state == AppState.IDLE:
            self._skip_overlay.hide()
            self._set_buttons_enabled(False)
    
    def _set_buttons_enabled(self, enabled: bool):
        """Enable/disable answer buttons and toggle visibility."""
        for btn in self._option_buttons:
            btn.setEnabled(enabled)
            btn.setVisible(enabled)  # Hide when not interactive
        
        # Update feedback text
        if enabled:
            self._interaction_locked = False
            self.feedback_label.setText("Tap the correct number!")
            self.feedback_label.setStyleSheet(f"color: {COLORS['text_light']}; background: transparent;")
    
    def show_visual_hint(self, hint_name: str):
        """Display a visual hint."""
        print(f"[PremiumActivityView] Visual Hint: {hint_name}")


class SkipOverlay(QWidget):
    """Transparent overlay for tap-to-skip during blocked states."""
    
    clicked = pyqtSignal()
    
    def __init__(self, parent, director):
        super().__init__(parent)
        self.director = director
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.resize(parent.size())
        self.hide()
        
        self.clicked.connect(self._on_skip_requested)
    
    def _on_skip_requested(self):
        self.director.force_skip()
        if hasattr(self.parent(), 'audio') and self.parent().audio:
            self.parent().audio.stop_voice()
    
    def mousePressEvent(self, event):
        self.clicked.emit()
        event.accept()
    
    def resizeEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())
