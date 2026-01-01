"""
Problem Factory - Dynamic Math Problem Generation

Generates math problems using pluggable strategies for counting, addition,
and subtraction operations with linear difficulty scaling.

Architecture:
- Uses Strategy pattern for different operation types
- ProblemData dataclass ensures schema consistency
- Backward compatible with legacy dict format
"""

import random
from typing import Optional, Union

from config import CONCRETE_ITEMS
from core.contracts import (
    ProblemData,
    Operation,
    WorldID,
    MathWorld,
    LevelConfig,
    get_level_config,
    get_operation_for_world,
    WORLD_OPERATION_MAP,
    WORLD_2_LEVELS,
    WORLD_3_LEVELS,
)
from core.strategies import (
    ProblemStrategy,
    CountingStrategy,
    AdditionStrategy,
    SubtractionStrategy,
    get_strategy,
)


# Pedagogically appropriate prompts that don't give away the answer
HOST_PROMPTS = {
    Operation.COUNTING.value: [
        "How many can you count?",
        "Let's count together!",
        "Can you count these?",
        "Count carefully!",
        "How many do you see?",
        "Take your time and count!",
    ],
    Operation.ADDITION.value: [
        "How many altogether?",
        "Let's add them together!",
        "Count all of them!",
        "Put them together and count!",
        "How many when we combine?",
    ],
    Operation.SUBTRACTION.value: [
        "How many are left?",
        "What's left after we take away?",
        "Count what remains!",
        "How many stay?",
        "After we remove some, how many?",
    ],
}


class ProblemFactory:
    """
    Generates math problems scaled to level index.
    
    Supports:
    - World 1: Counting (default, backward compatible)
    - World 2: Addition
    - World 3: Subtraction
    
    Usage:
        factory = ProblemFactory()
        
        # Legacy counting (backward compatible)
        problem = factory.generate(level_idx=5)
        
        # New operation-specific generation
        problem = factory.generate_problem(
            operation="addition",
            difficulty=3
        )
    """
    
    def __init__(self):
        """Initialize factory with strategy instances."""
        self._strategies = {
            Operation.COUNTING.value: CountingStrategy(),
            Operation.ADDITION.value: AdditionStrategy(),
            Operation.SUBTRACTION.value: SubtractionStrategy(),
        }
    
    @staticmethod
    def generate(level_idx: int) -> dict:
        """
        Generate a counting problem for the given level (legacy API).
        
        Backward compatible with existing code.
        
        Args:
            level_idx: Level index (0-9)
            
        Returns:
            Dictionary with problem data in legacy format
            
        Level 0 -> Counts 1-3
        Level 9 -> Counts 10-20
        """
        strategy = CountingStrategy()
        problem_data = strategy.generate(difficulty=level_idx)
        
        # Convert to legacy format
        result = problem_data.to_dict()
        result["level"] = level_idx + 1
        result["host"] = random.choice(HOST_PROMPTS[Operation.COUNTING.value])
        
        return result
    
    def generate_problem(
        self,
        operation: str,
        difficulty: int,
        level_config: Optional[LevelConfig] = None
    ) -> ProblemData:
        """
        Generate a problem using the strategy pattern.
        
        Args:
            operation: Operation type ('counting', 'addition', 'subtraction')
            difficulty: Difficulty level (1-10)
            level_config: Optional level configuration for curriculum context
            
        Returns:
            ProblemData object with all fields populated
        """
        strategy = self._strategies.get(operation)
        if strategy is None:
            raise ValueError(f"Unknown operation: {operation}")
        
        return strategy.generate(difficulty=difficulty)
    
    def generate_for_level(self, level_id: str) -> ProblemData:
        """
        Generate a problem for a specific curriculum level.
        
        Args:
            level_id: Level ID in format "W2-L01", "W3-L05", etc.
            
        Returns:
            ProblemData appropriate for that level
            
        Raises:
            ValueError: If level_id is invalid or not found
        """
        config = get_level_config(level_id)
        if config is None:
            raise ValueError(f"Unknown level_id: {level_id}")
        
        return self.generate_problem(
            operation=config.operation.value,
            difficulty=config.level_number,
            level_config=config
        )
    
    def generate_as_dict(
        self,
        operation: str,
        difficulty: int,
        level_idx: int = 0
    ) -> dict:
        """
        Generate a problem and return as legacy dict format.
        
        Args:
            operation: Operation type
            difficulty: Difficulty level
            level_idx: Level index for display (defaults to 0)
            
        Returns:
            Dictionary compatible with existing game components
        """
        problem_data = self.generate_problem(operation, difficulty)
        result = problem_data.to_dict()
        result["level"] = level_idx + 1
        result["host"] = random.choice(HOST_PROMPTS.get(
            operation,
            HOST_PROMPTS[Operation.COUNTING.value]
        ))
        return result
    
    def generate_for_world(
        self,
        world: WorldID,
        level_in_world: int
    ) -> dict:
        """
        Generate a problem for a specific world and level.
        
        This is the primary API for Phase 3, replacing index-based generation.
        
        Args:
            world: WorldID enum (W1=Counting, W2=Addition, W3=Subtraction)
            level_in_world: Level number within the world (1-10)
            
        Returns:
            Dictionary with problem data including visual_config
        """
        operation = get_operation_for_world(world)
        return self.generate_as_dict(
            operation=operation,
            difficulty=level_in_world,
            level_idx=level_in_world - 1
        )
