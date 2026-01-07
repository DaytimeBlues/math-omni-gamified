"""
Problem Factory - Strategy-driven problem generation.

Cursor Code Quality Fix:
- Added register_strategy() for dynamic strategy registration (Plugin Packs)
- Full type hints throughout
"""

from __future__ import annotations
from core.problems import (
    AdditionStrategy,
    CountingStrategy,
    ProblemData,
    ProblemStrategy,
    SubtractionStrategy,
)

class ProblemFactory:
    """Context class that selects the appropriate problem strategy."""

    def __init__(self):
        self._strategies: dict[str, ProblemStrategy] = {
            "counting": CountingStrategy(),
            "addition": AdditionStrategy(),
            "subtraction": SubtractionStrategy(),
        }
        self._current_mode: str = "counting"

    @property
    def current_mode(self) -> str:
        return self._current_mode

    def set_mode(self, mode: str) -> None:
        if mode not in self._strategies:
            raise ValueError(f"Unknown mode: {mode}")
        self._current_mode = mode

    def set_profile(self, profile):
        """Propagate profile to all strategies."""
        for strategy in self._strategies.values():
            strategy.set_profile(profile)
    
    # Cursor Registry Pattern: Enables future Plugin Packs
    def register_strategy(self, mode: str, strategy: ProblemStrategy) -> None:
        """
        Register a new problem strategy dynamically.
        
        Usage for Plugin Packs:
            factory.register_strategy("fractions", FractionsStrategy())
        """
        if not isinstance(strategy, ProblemStrategy):
            raise TypeError(f"Strategy must be a ProblemStrategy subclass, got {type(strategy)}")
        self._strategies[mode] = strategy

    def unregister_strategy(self, mode: str) -> bool:
        """Remove a registered strategy. Returns True if removed."""
        if mode in ("counting", "addition", "subtraction"):
            raise ValueError(f"Cannot unregister core strategy: {mode}")
        return self._strategies.pop(mode, None) is not None
    
    @property
    def available_modes(self) -> list[str]:
        """List all registered strategy modes."""
        return list(self._strategies.keys())

    def generate(self, difficulty: int, mode: str | None = None) -> ProblemData:
        # Input validation: ensure difficulty is non-negative
        if difficulty < 0:
            difficulty = 0
        
        strategy_key = mode or self._current_mode
        if strategy_key not in self._strategies:
            raise ValueError(f"Unknown mode: {strategy_key}")

        strategy = self._strategies[strategy_key]
        return strategy.generate(difficulty)

