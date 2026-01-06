from __future__ import annotations

import random

from config import CONCRETE_ITEMS
from .base import ProblemData, ProblemStrategy

class CountingStrategy(ProblemStrategy):
    """Generate counting problems with linear difficulty scaling."""

    def generate(self, difficulty: int) -> ProblemData:
        # Cursor fix: Input validation - ensure non-negative difficulty
        difficulty = max(0, difficulty)
        max_n = 3 + (difficulty * 2)
        max_n = min(max_n, 20)
        target = random.randint(1, max_n)
        item = random.choice(CONCRETE_ITEMS)

        audio_sequence = [
            "question_how_many",
            f"items_{item['name']}",
        ]
        
        # FIX: _generate_distractors now returns [target, d1, d2] shuffled
        options = self._generate_distractors(target, count=2, min_val=1, max_val=max_n)

        return ProblemData(
            correct_answer=target,
            prompt_text=f"How many {item['name']}?",
            group_a_count=target,
            group_b_count=0,
            item_name=item["name"],
            operator_type="none",
            audio_sequence=audio_sequence,
            options=options,
        )

