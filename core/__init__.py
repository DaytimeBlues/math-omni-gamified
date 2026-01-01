# Core module initialization
"""
Core module exports for Math Omni.

Provides:
- Contracts: ProblemData, WorldID, Operation, CPAStage, AudioTokens
- Strategies: ProblemStrategy, CountingStrategy, AdditionStrategy, SubtractionStrategy
- Services: ProblemFactory, HintEngine, VoiceBank, DatabaseService, etc.
"""

from core.contracts import (
    ProblemData,
    WorldID,
    MathWorld,  # Alias for WorldID
    Operation,
    CPAStage,
    VisualType,
    AudioTokens,
    LevelConfig,
    make_level_id,
    parse_level_id,
    get_level_config,
    get_operation_for_world,
    WORLD_OPERATION_MAP,
)

from core.strategies import (
    ProblemStrategy,
    CountingStrategy,
    AdditionStrategy,
    SubtractionStrategy,
    get_strategy,
    STRATEGY_REGISTRY,
)

__all__ = [
    # Contracts
    "ProblemData",
    "WorldID",
    "MathWorld",
    "Operation",
    "CPAStage",
    "VisualType",
    "AudioTokens",
    "LevelConfig",
    "make_level_id",
    "parse_level_id",
    "get_level_config",
    "get_operation_for_world",
    "WORLD_OPERATION_MAP",
    # Strategies
    "ProblemStrategy",
    "CountingStrategy",
    "AdditionStrategy",
    "SubtractionStrategy",
    "get_strategy",
    "STRATEGY_REGISTRY",
]
