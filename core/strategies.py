"""
core/strategies.py
Problem Generation Strategies - Strategy Pattern Implementation

Provides pluggable problem generation strategies for different operation types.
Each strategy generates pedagogically appropriate problems following CPA stages.
"""
import random
from abc import ABC, abstractmethod
from typing import List, Set

from config import CONCRETE_ITEMS
from core.contracts import (
    ProblemData,
    Operation,
    VisualType,
    AudioTokens,
    CPAStage,
)


class ProblemStrategy(ABC):
    """
    Abstract base class for problem generation strategies.
    
    Each concrete strategy implements the generate() method to produce
    ProblemData objects appropriate for their operation type.
    """
    
    @abstractmethod
    def generate(self, difficulty: int) -> ProblemData:
        """
        Generate a problem for the given difficulty level.
        
        Args:
            difficulty: Difficulty level (1-10, where 1 is easiest)
            
        Returns:
            A ProblemData object with all fields populated
        """
        pass
    
    @staticmethod
    def _generate_distractors(
        target: int,
        count: int = 3,
        min_value: int = 0,
        max_spread: int = 2
    ) -> List[int]:
        """
        Generate distractor options including the correct answer.
        
        Uses improved logic to avoid distractors being too close to each other
        (DeepSeek review recommendation).
        
        Args:
            target: The correct answer
            count: Total number of options to generate
            min_value: Minimum allowed value for distractors
            max_spread: Maximum distance from target for distractors
            
        Returns:
            Shuffled list of options including the target
        """
        options: Set[int] = {target}
        
        # Generate spread-out distractors
        possible_offsets = [-2, -1, 1, 2]
        random.shuffle(possible_offsets)
        
        for offset in possible_offsets:
            if len(options) >= count:
                break
            distractor = target + offset
            # Ensure distractor is valid and not too close to existing options
            if distractor >= min_value and distractor not in options:
                # Check minimum distance from existing distractors
                too_close = False
                for existing in options:
                    if existing != target and abs(distractor - existing) < 2:
                        too_close = True
                        break
                if not too_close:
                    options.add(distractor)
        
        # Fallback: fill remaining slots if needed
        attempts = 0
        while len(options) < count and attempts < 20:
            offset = random.choice([-3, 3, -4, 4])
            distractor = target + offset
            if distractor >= min_value and distractor not in options:
                options.add(distractor)
            attempts += 1
        
        # Last resort: add sequential numbers
        while len(options) < count:
            options.add(max(options) + 1)
        
        result = list(options)
        random.shuffle(result)
        return result


class CountingStrategy(ProblemStrategy):
    """
    Strategy for generating counting problems (World 1).
    
    Difficulty scaling:
    - Levels 1-3: Count 1-3 items
    - Levels 4-6: Count 1-10 items
    - Levels 7-10: Count 1-20 items
    """
    
    def generate(self, difficulty: int) -> ProblemData:
        """Generate a counting problem."""
        # Scale max count based on difficulty
        max_n = 3 + (difficulty * 2)
        max_n = min(max_n, 20)  # Cap at 20 for foundation year
        
        target = random.randint(1, max_n)
        item = random.choice(CONCRETE_ITEMS)
        
        # Generate distractors
        options = self._generate_distractors(
            target=target,
            count=3,
            min_value=1
        )
        
        # Audio sequence: question prompt + number
        audio_sequence = [
            AudioTokens.Q_HOW_MANY,
            AudioTokens.number(min(target, 20))
        ]
        
        return ProblemData(
            type=Operation.COUNTING.value,
            operand_a=target,
            operand_b=None,
            target=target,
            options=options,
            visual_config={
                "type": VisualType.COUNT.value,
                "item_name": item['name'],
                "emoji": item['emoji'],
                "count": target,
            },
            audio_sequence=audio_sequence
        )


class AdditionStrategy(ProblemStrategy):
    """
    Strategy for generating addition problems (World 2).
    
    Pedagogical approach (Dr. Maria):
    - Concrete stage: Show group A, then group B, then slide together
    - Levels 1-5: Sums up to 5
    - Levels 6-10: Sums up to 10
    """
    
    def generate(self, difficulty: int) -> ProblemData:
        """Generate an addition problem."""
        # Determine max sum based on difficulty
        if difficulty <= 3:
            max_sum = 5
        elif difficulty <= 5:
            max_sum = 5
        else:
            max_sum = 10
        
        # Generate operands ensuring positive values
        a = random.randint(1, max_sum - 1)
        b = random.randint(1, max_sum - a)
        target = a + b
        
        # Select concrete item
        item = random.choice(CONCRETE_ITEMS)
        
        # Generate distractors (never negative)
        options = self._generate_distractors(
            target=target,
            count=3,
            min_value=0
        )
        
        # Audio sequence for addition
        audio_sequence = [
            AudioTokens.number(a),
            AudioTokens.OP_PLUS,
            AudioTokens.number(b),
            AudioTokens.OP_EQUALS,
            AudioTokens.Q_ALTOGETHER
        ]
        
        return ProblemData(
            type=Operation.ADDITION.value,
            operand_a=a,
            operand_b=b,
            target=target,
            options=options,
            visual_config={
                "type": VisualType.MERGE.value,
                "item_name": item['name'],
                "emoji": item['emoji'],
                "group_a_count": a,
                "group_b_count": b,
            },
            audio_sequence=audio_sequence
        )


class SubtractionStrategy(ProblemStrategy):
    """
    Strategy for generating subtraction problems (World 3).
    
    Pedagogical approach (Dr. Maria):
    - Concrete removal stage: Show total, then animate items fading/moving away
    - Levels 1-5: Starting from 5
    - Levels 6-10: Starting from 10
    """
    
    def generate(self, difficulty: int) -> ProblemData:
        """Generate a subtraction problem."""
        # Determine max starting value based on difficulty
        if difficulty <= 3:
            max_start = 5
        elif difficulty <= 5:
            max_start = 5
        else:
            max_start = 10
        
        # Generate operands ensuring non-negative result
        a = random.randint(2, max_start)
        b = random.randint(1, a - 1)
        target = a - b
        
        # Select concrete item
        item = random.choice(CONCRETE_ITEMS)
        
        # Generate distractors (never negative)
        options = self._generate_distractors(
            target=target,
            count=3,
            min_value=0
        )
        
        # Audio sequence for subtraction
        audio_sequence = [
            AudioTokens.number(a),
            AudioTokens.OP_TAKE_AWAY,
            AudioTokens.number(b),
            AudioTokens.OP_EQUALS,
            AudioTokens.Q_LEFT
        ]
        
        return ProblemData(
            type=Operation.SUBTRACTION.value,
            operand_a=a,
            operand_b=b,
            target=target,
            options=options,
            visual_config={
                "type": VisualType.TAKE_AWAY.value,
                "item_name": item['name'],
                "emoji": item['emoji'],
                "start_count": a,
                "remove_count": b,
            },
            audio_sequence=audio_sequence
        )


# =============================================================================
# STRATEGY REGISTRY
# =============================================================================

STRATEGY_REGISTRY = {
    Operation.COUNTING.value: CountingStrategy(),
    Operation.ADDITION.value: AdditionStrategy(),
    Operation.SUBTRACTION.value: SubtractionStrategy(),
}


def get_strategy(operation: str) -> ProblemStrategy:
    """
    Get the strategy for a given operation type.
    
    Args:
        operation: Operation type string ('counting', 'addition', 'subtraction')
        
    Returns:
        The appropriate ProblemStrategy instance
        
    Raises:
        ValueError: If the operation type is not supported
    """
    strategy = STRATEGY_REGISTRY.get(operation)
    if strategy is None:
        raise ValueError(f"Unknown operation type: {operation}")
    return strategy
