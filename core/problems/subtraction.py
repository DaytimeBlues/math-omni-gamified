from __future__ import annotations

import random

from .base import ProblemData, ProblemStrategy


class SubtractionStrategy(ProblemStrategy):
    """Generate simple subtraction problems with natural voice variations."""

    # Simplified W3 Lead-in tokens (each is a complete phrase clip)
    W3_LEADINS = [
        "w3_takeaway_v01",  # "If we take away..."
        "w3_takeaway_v02",  # "Let's take away..."
        "w3_takeaway_v03",  # "Now take away..."
        "w3_takeaway_v04",  # "Take away..."
        "w3_takeaway_v05",  # "What if ... fly away?"
        "w3_takeaway_v06",  # "Let's send away..."
        "w3_takeaway_v07",  # "We can take away..."
        "w3_takeaway_v08",  # "Let's try taking away..."
        "w3_takeaway_v09",  # "Can you take away...?"
        "w3_takeaway_v10",  # "Okay, take away..."
    ]

    # Zero-result tokens (complete phrases)
    W3_ZERO_RESULTS = [
        "w3_zero_v01",  # "We took them all away. None are left."
        "w3_zero_v02",  # "All gone. That means zero left."
        "w3_zero_v03",  # "None left to count. That's zero."
    ]

    def generate(self, difficulty: int) -> ProblemData:
        # Check Curriculum first
        from .curriculum import WORLD_3_CURRICULUM
        if difficulty in WORLD_3_CURRICULUM:
            spec = WORLD_3_CURRICULUM[difficulty]
            return ProblemData(
                correct_answer=spec["target"],
                prompt_text=f"{spec['a']} - {spec['b']} = ?",
                group_a_count=spec['a'],
                group_b_count=spec['b'],
                item_name=spec['item'],
                operator_type="subtract",
                audio_sequence=spec['audio'],
                options=self._generate_distractors(spec["target"], count=2, min_val=0, max_val=max(10, spec['a'])),
            )

        # Fallback: Procedural
        max_start = 5 if difficulty < 25 else 10
        minuend = random.randint(2, max_start)
        subtrahend = random.randint(1, minuend) 
        result = minuend - subtrahend

        item = random.choice(["apples", "cats", "stars"])

        leadin = random.choice(self.W3_LEADINS)
        audio = [
            f"numbers_{minuend:02d}",
            leadin,
            f"numbers_{subtrahend:02d}",
            "op_equals",
            "q_left",
        ]

        if result == 0:
             # Inject the zero logic into the audio sequence if procedurally generated?
             # Curriculum handles it explicitly.
             pass

        return ProblemData(
            correct_answer=result,
            prompt_text=f"{minuend} - {subtrahend} = ?",
            group_a_count=minuend,
            group_b_count=subtrahend,
            item_name=item,
            operator_type="subtract",
            audio_sequence=audio,
            options=self._generate_distractors(result, count=2, min_val=0, max_val=max_start),
        )
    
    def get_zero_result_feedback(self) -> str:
        """Return audio token for zero-result celebration (called after correct answer)."""
        return random.choice(self.W3_ZERO_RESULTS)
