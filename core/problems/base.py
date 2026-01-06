from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class ProblemData:
    """Unified contract for any math problem."""

    correct_answer: int
    prompt_text: str

    group_a_count: int
    group_b_count: int
    item_name: str
    operator_type: str

    audio_sequence: List[str]
    options: List[int]


class ProblemStrategy(ABC):
    """Strategy interface for generating math problems."""

    def __init__(self):
        self.profile = None

    def set_profile(self, profile):
        """Inject student profile for adaptive difficulty."""
        self.profile = profile

    @abstractmethod
    def generate(self, difficulty: int) -> ProblemData:
        """Generate a problem for the given difficulty level."""
        raise NotImplementedError

    def _generate_distractors(self, target: int, count: int, min_val: int = 1, max_val: int = 20) -> list[int]:
        """
        Generate options including the correct answer and distractors.
        Returns a shuffled list of [target, distractor1, distractor2, ...].
        
        FIX: Previously only returned distractors. Now includes target answer.
        """
        import random
        # Lazy import to avoid circular dependency
        from core.problems.distractor_generator import generate_addition_distractors
        
        # 1. Get base distractors (educationally sound)
        # Note: generate_addition_distractors returns [target, d1, d2]
        base_set = generate_addition_distractors(target)
        # Filter to exclude target AND respect min_val/max_val bounds
        distractors = [d for d in base_set if d != target and d >= min_val and d <= max_val]
        
        # 2. Inject personalized mistakes if available
        if self.profile:
            # Determine problem type from class name
            p_type = "addition" if "Addition" in self.__class__.__name__ else "subtraction"
            if "Counting" in self.__class__.__name__: p_type = "counting"
            
            # Get common errors for this type
            history_errors = self.profile.get_frequent_errors(p_type)
            
            # Try to swap a random distractor with a historical error
            for err in history_errors:
                if err != target and min_val <= err <= max_val and err not in distractors:
                    if len(distractors) > 0:
                        distractors[0] = err # Replace first distractor
                    break
        
        # Ensure correct count of distractors
        while len(distractors) < count:
             d = random.randint(min_val, max_val)
             if d != target and d not in distractors:
                 distractors.append(d)
                 
        # Trim to exactly 'count' distractors
        distractors = distractors[:count]
        
        # FIX: Include target in options and shuffle
        options = [target] + distractors
        random.shuffle(options)
        return options
