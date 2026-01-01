from __future__ import annotations

import random

from .base import ProblemData, ProblemStrategy


class AdditionStrategy(ProblemStrategy):
    """Generate simple addition problems with curated progression."""

    def generate(self, difficulty: int) -> ProblemData:
        from .curriculum import WORLD_2_CURRICULUM
        
        # Check if we have a curated spec for this difficulty/level
        if difficulty in WORLD_2_CURRICULUM:
            spec = WORLD_2_CURRICULUM[difficulty]
            a, b, target = spec["a"], spec["b"], spec["target"]
            item = spec["item"]
            audio = spec["audio"]
            max_sum = max(10, target + 5)
        else:
            # Fallback to random for higher difficulties
            max_sum = 5 if difficulty <= 3 else 10
            a = random.randint(1, max_sum - 1)
            b = random.randint(1, max_sum - a)
            target = a + b
            item = random.choice(["apples", "cats", "stars"])
            audio = [
                f"numbers_{a:02d}",
                "op_plus",
                f"numbers_{b:02d}",
                "op_equals",
                "question_what_is",
            ]

        return ProblemData(
            correct_answer=target,
            prompt_text=f"{a} + {b} = ?",
            group_a_count=a,
            group_b_count=b,
            item_name=item,
            operator_type="add",
            audio_sequence=audio,
            options=self._generate_distractors(target, count=2, min_val=1, max_val=max_sum),
        )
