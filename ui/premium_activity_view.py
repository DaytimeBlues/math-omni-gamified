"""
Premium Activity View - "Reading Eggs" Quality Design

Claude's Implementation:
- Cream gradient background
- White rounded card for content
- Chunky 3D buttons with shadows
- Pill-shaped egg counter
- Generous whitespace

Reference: The uploaded target design screenshot
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QPropertyAnimation, 
    QEasingCurve, QParallelAnimationGroup, QPoint, QRect
)
from PyQt6.QtGui import QFont, QColor

from config import (
    MIN_TOUCH_TARGET, BUTTON_GAP, DEBOUNCE_DELAY_MS,
    FONT_FAMILY, FONT_SIZE_BODY, FONT_SIZE_HEADING, COLORS, CONCRETE_ITEMS
)
from core.sfx import SFX
from core.director import AppState
from core.problems import ProblemData
from ui.components import SkipOverlay


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

ITEM_EMOJI_MAP = {item["name"]: item["emoji"] for item in CONCRETE_ITEMS}

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
    
    # signal(is_correct, chosen, target)
    answer_submitted = pyqtSignal(bool, int, int)
    back_to_map = pyqtSignal()
    
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
        """Build the white rounded card for question display. RESPONSIVE UPDATE (Frontend Audit v3.0)"""
        print("[PremiumActivityView] LAYOUT: Building responsive question card")
        
        card = QFrame()
        card.setObjectName("QuestionCard")
        card.setStyleSheet(QUESTION_CARD_STYLE)
        
        # Responsive sizing: percentage-based with sensible limits instead of hard fixed pixels
        card.setMinimumSize(320, 200)   # Supports 4:3 @ 800x600
        card.setMaximumSize(800, 500)   # Caps growth on ultrawide
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        
        add_soft_shadow(card, blur=30, offset_y=10, opacity=25)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15) # Slightly tighter for small screens
        card_layout.setContentsMargins(30, 25, 30, 25)
        
        # Question text
        self.question_label = QLabel("How many?")
        self.question_label.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold)) # Slightly smaller base font, scalable?
        self.question_label.setStyleSheet(f"color: {COLORS['text']}; background: transparent;")
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.question_label.setWordWrap(True)
        # Label should take minimal vertical space needed
        self.question_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        card_layout.addWidget(self.question_label)
        
        # Visual display (VisualBoard)
        from ui.visual_board import VisualBoard
        self.visual_board = VisualBoard()
        
        # CRITICAL: Board must expand both ways to fill the card body
        self.visual_board.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        # Takes remaining space (stretch=1)
        card_layout.addWidget(self.visual_board, stretch=1)
        
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
    # ACTIVITY LOGIC (Refactored)
    # ==========================================================================
    
    def render_problem(self, level: int, eggs: int, problem: ProblemData):
        """Configure the activity view from a ProblemData payload."""
        from ui.premium_utils import draw_premium_background  # Lazy import
        
        self._correct_answer = problem.correct_answer
        self._interaction_locked = True
        
        emoji = ITEM_EMOJI_MAP.get(problem.item_name, "🔢")

        self.level_label.setText(f"Level {level}")
        self.question_label.setText(problem.prompt_text)
        self.egg_label.setText(str(eggs))
        self._leavers = [] # Track items to animate
        
        # Render Visuals via Board
        self._render_visuals(problem, emoji)
        
        # Cursor Optimization: Schedule Take-Away Animation
        if problem.operator_type == "subtract" and self._leavers:
            # Wait 1.5s (after "Number A... Take away...")
            QTimer.singleShot(1500, self._play_take_away_animation)
        
        # Reset and HIDE buttons until audio finishes
        for i, btn in enumerate(self._option_buttons):
            if i < len(problem.options):
                btn._base_text = str(problem.options[i])
                btn.reset()
                btn.setVisible(False)
            else:
                btn.hide() # Should not happen if data is correct

        self.feedback_label.setText("Listen carefully...")
    
    def _render_visuals(self, problem: ProblemData, emoji: str):
        """Delegate visual rendering to board."""
        if problem.operator_type == "subtract":
            # For subtraction: Show A (total), CROSSOUT B (subtracted)
            # Example: 5 - 2. Show 5 items. Cross out last 2.
            self._leavers = self.visual_board.render(
                emoji, 
                count=problem.group_a_count, 
                mode="crossout", 
                subtract_count=problem.group_b_count,
                animate_crossout=False # We will trigger the animation manually
            )
        else:
            # For addition/counting: Show the total (correct_answer) currently
            # Ideally for addition we show two groups, but for now showing the sum is safe.
            # Or better: ProblemData should probably specify exactly what to show.
            # "Add" problem usually shows "2 + 3" or "5 total"?
            # Curriculum says: "op_plus", "op_equals".
            
            # Simple approach: Display the final count for counting
            # For Addition: Display total?
            target_count = problem.correct_answer
            self.visual_board.render(emoji, count=target_count, mode="normal")
            self._leavers = []

    def _play_take_away_animation(self):
        """
        Premium 'Take Away' Animation (Cursor/Z.ai Merge).
        Items shrink, fade to ghost mode, and move slightly.
        """
        if not self._leavers:
            return
            
        print(f"[PremiumActivityView] ANIM: Playing take-away for {len(self._leavers)} items")
        anim_group = QParallelAnimationGroup(self)
        
        for item in self._leavers:
            # 1. Scale/Geometry Animation
            geo_anim = QPropertyAnimation(item, b"geometry")
            geo_anim.setDuration(800)
            start_geo = item.geometry()
            center = start_geo.center()
            # Shrink to 70% size
            end_rect = QRect(0, 0, int(start_geo.width()*0.7), int(start_geo.height()*0.7))
            end_rect.moveCenter(center)
            
            geo_anim.setStartValue(start_geo)
            geo_anim.setEndValue(end_rect)
            geo_anim.setEasingCurve(QEasingCurve.Type.OutBack)
            anim_group.addAnimation(geo_anim)
            
            # 2. Swap to Ghost Pixmap (coordinated with animation end)
            # Actually, we can just call set_ghost_mode(True, animate=False) at start
            # since the shrink is the primary visual cue.
            item.set_ghost_mode(True, animate=False)

        if self.audio:
            self.audio.play_sfx(SFX.POP) # Add subtle 'pop' sound for each!
            
        anim_group.start()
            
    def paintEvent(self, event):
        """Draw premium background."""
        from ui.premium_utils import draw_premium_background
        draw_premium_background(self)
    
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
            
            # Audit Fix: Shake button on wrong answer
            from ui.premium_utils import create_shake_animation
            self._shake_anim = create_shake_animation(button)
            self._shake_anim.start()
        
        self.answer_submitted.emit(correct, answer, self._correct_answer)
    
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


