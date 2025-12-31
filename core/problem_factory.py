"""
Problem Factory - Dynamic Math Problem Generation

Generates counting problems with linear difficulty scaling.
"""

import random
from config import CONCRETE_ITEMS

# Pedagogically appropriate prompts that don't give away the answer
HOST_PROMPTS = [
    "How many can you count?",
    "Let's count together!",
    "Can you count these?",
    "Count carefully!",
    "How many do you see?",
    "Take your time and count!",
]


class ProblemFactory:
    """Generates math problems scaled to level index."""
    
    @staticmethod
    def generate(level_idx: int) -> dict:
        """
        Generate a counting problem for the given level.
        
        Level 0 -> Counts 1-3
        Level 9 -> Counts 10-20
        """
        # Linear difficulty scaling
        max_n = 3 + (level_idx * 2)
        max_n = min(max_n, 20)  # Cap at 20 for foundation year
        target = random.randint(1, max_n)
        item = random.choice(CONCRETE_ITEMS)
        
        # Generate distractors (close to target for challenge)
        options = {target}
        attempts = 0
        while len(options) < 3 and attempts < 20:
            offset = random.choice([-1, 1, -2, 2])
            distractor = target + offset
            if distractor > 0 and distractor != target:
                options.add(distractor)
            attempts += 1
        
        # Ensure we always have 3 options
        while len(options) < 3:
            options.add(max(1, target + len(options)))
        
        options_list = list(options)
        random.shuffle(options_list)
        
        return {
            "level": level_idx + 1,
            "target": target,
            "options": options_list,
            "prompt": f"How many {item['name']}?",
            "emoji": item['emoji'],
            "item_name": item['name'],  # For VoiceBank category lookup
            "host": random.choice(HOST_PROMPTS)  # No longer gives away answer!
        }
