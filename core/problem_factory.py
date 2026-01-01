"""
Problem Factory - Dynamic Math Problem Generation

Phase 3: Uses Strategy Pattern for multi-world support.
Supports Counting, Addition, and Subtraction problem generation.

Architecture:
- ProblemFactory delegates to registered strategies
- MathWorld enum selects the appropriate strategy
- Backwards compatible with legacy generate(level_idx) calls
"""

from typing import Optional, Union

from core.problem_strategy import (
    MathWorld,
    ProblemData,
    ProblemStrategy,
    StrategyRegistry,
    CountingStrategy,
    VisualMode,
)


class ProblemFactory:
    """
    Factory for generating math problems using the Strategy Pattern.
    
    Supports multiple MathWorlds (Counting, Addition, Subtraction).
    Maintains backwards compatibility with legacy level-based generation.
    """
    
    def __init__(self, default_world: MathWorld = MathWorld.COUNTING):
        """
        Initialize factory with a default world.
        
        Args:
            default_world: Default MathWorld for legacy generate() calls
        """
        self._default_world = default_world
        self._current_world = default_world
        self._strategy_cache: dict[MathWorld, ProblemStrategy] = {}
    
    def set_world(self, world: MathWorld) -> None:
        """
        Set the current world for problem generation.
        
        Args:
            world: The MathWorld to use for subsequent generate() calls
        """
        self._current_world = world
    
    @property
    def current_world(self) -> MathWorld:
        """Get the currently active MathWorld."""
        return self._current_world
    
    def _get_strategy(self, world: MathWorld) -> ProblemStrategy:
        """Get or create strategy for the given world (cached)."""
        if world not in self._strategy_cache:
            self._strategy_cache[world] = StrategyRegistry.get_strategy(world)
        return self._strategy_cache[world]
    
    def generate(self, level_idx: int, world: Optional[MathWorld] = None) -> dict:
        """
        Generate a math problem for the given level.
        
        Args:
            level_idx: 0-based level index
            world: Optional MathWorld override (uses current_world if None)
            
        Returns:
            Dictionary with problem data (backwards compatible format)
        """
        target_world = world or self._current_world
        strategy = self._get_strategy(target_world)
        problem = strategy.generate(level_idx)
        
        # Convert to dict for backwards compatibility
        result = problem.to_dict()
        
        # Add legacy 'host' key (alias for host_text)
        result['host'] = result.get('host_text', result.get('host', ''))
        
        return result
    
    def generate_problem(self, level_idx: int, world: Optional[MathWorld] = None) -> ProblemData:
        """
        Generate a math problem and return the full ProblemData object.
        
        Args:
            level_idx: 0-based level index
            world: Optional MathWorld override (uses current_world if None)
            
        Returns:
            ProblemData object with full type information
        """
        target_world = world or self._current_world
        strategy = self._get_strategy(target_world)
        return strategy.generate(level_idx)
    
    @staticmethod
    def get_visual_mode(world: MathWorld) -> VisualMode:
        """
        Get the default visual mode for a MathWorld.
        
        Returns:
            VisualMode enum value
        """
        mode_map = {
            MathWorld.COUNTING: VisualMode.SCATTER,
            MathWorld.ADDITION: VisualMode.MERGE,
            MathWorld.SUBTRACTION: VisualMode.TAKE_AWAY,
        }
        return mode_map.get(world, VisualMode.SCATTER)
