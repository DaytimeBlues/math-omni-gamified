"""
core/hint_engine.py
Rule-Based Hint System - Zero Latency, No AI.

Provides pre-defined hints based on activity type and attempt count.
Hints escalate: Visual Cue -> Audio Prompt -> Stronger Visual.
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import random

@dataclass
class Hint:
    """A single hint definition."""
    hint_type: str  # "visual" or "audio"
    name: str       # Identifier for the hint asset/action
    message: str    # Optional text for TTS or display

# Pre-defined hint library by activity type
HINT_LIBRARY: Dict[str, List[Hint]] = {
    "counting": [
        Hint("visual", "pulse_correct_area", ""),
        Hint("audio", "lets_count_together", "Let's count together!"),
        Hint("visual", "highlight_groups", ""),
    ],
    "number_tracing": [
        Hint("visual", "arrow_following", ""),
        Hint("audio", "trace_the_number", "Trace the number with your finger."),
        Hint("visual", "pulsing_outline", ""),
    ],
    "shape_matching": [
        Hint("visual", "pulse_matching_shape", ""),
        Hint("audio", "find_the_same_shape", "Find the same shape!"),
        Hint("visual", "connect_with_line", ""),
    ],
    "addition": [
        Hint("visual", "pulse_correct_area", ""),
        Hint("audio", "count_all_objects", "Count all the objects together."),
        Hint("visual", "group_numbers", ""),
        Hint("audio", "combine_groups", "Put the groups together, then count!"),
    ],
    "subtraction": [
        Hint("visual", "highlight_removal", ""),
        Hint("audio", "count_whats_left", "Count how many are left after some go away."),
        Hint("visual", "animate_take_away", ""),
        Hint("audio", "watch_disappear", "Watch the items disappear, then count what's left."),
    ],
    # Default fallback
    "generic": [
        Hint("audio", "you_can_do_it", "You can do it!"),
        Hint("visual", "pulse_correct_area", ""),
        Hint("audio", "take_your_time", "Take your time."),
    ],
}

class RuleBasedHintEngine:
    """
    Provides deterministic hints based on activity and attempt count.
    No AI, no network calls, zero latency.
    """
    
    def __init__(self):
        self._hint_history: Dict[str, int] = {}  # Track hints given per activity

    def get_hint(self, activity_type: str, attempt_count: int) -> Optional[Hint]:
        """
        Returns the appropriate hint for the given activity and attempt.
        
        Args:
            activity_type: The type of activity (e.g., "counting", "addition").
            attempt_count: How many wrong attempts the child has made.
            
        Returns:
            A Hint object, or None if no hint should be shown yet.
        """
        # Don't give hints on first attempt
        if attempt_count < 1:
            return None
            
        hints = HINT_LIBRARY.get(activity_type, HINT_LIBRARY["generic"])
        
        # Escalate hints based on attempt count (0-indexed list)
        hint_index = min(attempt_count - 1, len(hints) - 1)
        
        return hints[hint_index]

    def get_random_encouragement(self) -> Hint:
        """Returns a random generic encouragement (for idle states)."""
        encouragements = [
            Hint("audio", "you_got_this", "You've got this!"),
            Hint("audio", "keep_trying", "Keep trying!"),
            Hint("audio", "almost_there", "Almost there!"),
        ]
        return random.choice(encouragements)

    def reset_for_activity(self, activity_id: str):
        """Resets hint tracking for a new activity instance."""
        if activity_id in self._hint_history:
            del self._hint_history[activity_id]
