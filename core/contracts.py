"""
core/contracts.py
Shared Interface Contracts for Math Omni

Defines strict schemas for problem data, identifiers, and audio tokens
to ensure code compatibility across all components.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


# =============================================================================
# IDENTIFIERS
# =============================================================================

class WorldID(str, Enum):
    """World identifiers for the learning map."""
    W1 = "W1"  # Counting
    W2 = "W2"  # Addition
    W3 = "W3"  # Subtraction


# Alias for backward compatibility and clarity
MathWorld = WorldID


# World to Operation mapping
WORLD_OPERATION_MAP = {
    WorldID.W1: "counting",
    WorldID.W2: "addition",
    WorldID.W3: "subtraction",
}


def get_operation_for_world(world: WorldID) -> str:
    """Get the operation type for a given world."""
    return WORLD_OPERATION_MAP.get(world, "counting")


class Operation(str, Enum):
    """Supported math operations."""
    COUNTING = "counting"
    ADDITION = "addition"
    SUBTRACTION = "subtraction"


class CPAStage(str, Enum):
    """Concrete-Pictorial-Abstract learning stages."""
    CONCRETE = "concrete"
    PICTORIAL = "pictorial"
    ABSTRACT = "abstract"


def make_level_id(world: WorldID, level: int) -> str:
    """
    Generate a level ID string.
    
    Args:
        world: The world identifier (W1, W2, W3)
        level: The level number (1-10)
        
    Returns:
        Level ID in format "W2-L01", "W3-L10", etc.
    """
    return f"{world.value}-L{level:02d}"


def parse_level_id(level_id: str) -> tuple[WorldID, int]:
    """
    Parse a level ID string back to its components.
    
    Args:
        level_id: String in format "W2-L01"
        
    Returns:
        Tuple of (WorldID, level_number)
        
    Raises:
        ValueError: If the format is invalid
    """
    if not level_id or "-L" not in level_id:
        raise ValueError(f"Invalid level_id format: {level_id}")
    
    parts = level_id.split("-L")
    if len(parts) != 2:
        raise ValueError(f"Invalid level_id format: {level_id}")
    
    world = WorldID(parts[0])
    level = int(parts[1])
    return world, level


# =============================================================================
# AUDIO TOKEN NAMING
# =============================================================================

class AudioTokens:
    """
    Audio token naming conventions for VoiceBank keys.
    
    Naming scheme:
    - numbers_0.wav ... numbers_20.wav
    - op_plus.wav, op_take_away.wav, op_equals.wav
    - q_altogether.wav, q_left.wav, q_how_many.wav
    """
    
    @staticmethod
    def number(n: int) -> str:
        """Get audio token for a number (0-20)."""
        if not 0 <= n <= 20:
            raise ValueError(f"Number must be 0-20, got {n}")
        return f"numbers_{n}"
    
    # Operators
    OP_PLUS = "op_plus"
    OP_TAKE_AWAY = "op_take_away"
    OP_EQUALS = "op_equals"
    
    # Question prompts
    Q_ALTOGETHER = "q_altogether"
    Q_LEFT = "q_left"
    Q_HOW_MANY = "q_how_many"


# =============================================================================
# VISUAL CONFIGURATION TYPES
# =============================================================================

class VisualType(str, Enum):
    """Types of visual representations for problems."""
    COUNT = "count"          # Single group counting
    MERGE = "merge"          # Two groups combining (addition)
    TAKE_AWAY = "take_away"  # Items being removed (subtraction)


# =============================================================================
# PROBLEM DATA SCHEMA
# =============================================================================

@dataclass
class ProblemData:
    """
    Unified schema for all math problem types.
    
    Attributes:
        type: The operation type ('counting', 'addition', 'subtraction')
        operand_a: First operand (the main number)
        operand_b: Second operand (None for counting problems)
        target: The correct answer
        options: List of answer choices (including distractors)
        visual_config: Configuration for visual representation
        audio_sequence: Sequence of VoiceBank keys for audio narration
    """
    type: str  # 'counting', 'addition', 'subtraction'
    operand_a: int
    operand_b: Optional[int]
    target: int
    options: List[int]
    visual_config: Dict = field(default_factory=dict)
    audio_sequence: List[str] = field(default_factory=list)
    
    @property
    def prompt_text(self) -> str:
        """Generate the display text for the problem prompt."""
        if self.type == Operation.ADDITION.value:
            return f"{self.operand_a} + {self.operand_b} = ?"
        elif self.type == Operation.SUBTRACTION.value:
            return f"{self.operand_a} - {self.operand_b} = ?"
        # For counting, include item name if available
        item_name = self.visual_config.get("item_name", "items")
        return f"How many {item_name}?"
    
    @property
    def is_valid(self) -> bool:
        """Check if the problem data is valid."""
        # Target must be in options
        if self.target not in self.options:
            return False
        
        # Options should be unique
        if len(self.options) != len(set(self.options)):
            return False
        
        # Binary operations need operand_b
        if self.type in (Operation.ADDITION.value, Operation.SUBTRACTION.value):
            if self.operand_b is None:
                return False
        
        # All options should be non-negative
        if any(opt < 0 for opt in self.options):
            return False
            
        return True

    def to_dict(self) -> dict:
        """
        Convert to legacy dict format for backward compatibility.
        
        Returns:
            Dictionary compatible with existing game components.
        """
        return {
            "type": self.type,
            "level": 1,  # Will be overridden by caller
            "target": self.target,
            "options": self.options,
            "prompt": self.prompt_text,
            "emoji": self.visual_config.get("emoji", "🔢"),
            "item_name": self.visual_config.get("item_name", "items"),
            "host": self._generate_host_prompt(),
            "operand_a": self.operand_a,
            "operand_b": self.operand_b,
            "visual_config": self.visual_config,
            "audio_sequence": self.audio_sequence,
        }
    
    def _generate_host_prompt(self) -> str:
        """Generate a pedagogically appropriate host prompt."""
        if self.type == Operation.COUNTING.value:
            return f"How many {self.visual_config.get('item_name', 'items')}?"
        elif self.type == Operation.ADDITION.value:
            return "How many altogether?"
        elif self.type == Operation.SUBTRACTION.value:
            return "How many are left?"
        return "What's the answer?"


# =============================================================================
# CURRICULUM STRUCTURE
# =============================================================================

@dataclass
class LevelConfig:
    """Configuration for a specific level."""
    level_id: str
    world: WorldID
    level_number: int
    operation: Operation
    cpa_stage: CPAStage
    max_value: int
    description: str = ""


# World 2: Addition curriculum (Dr. Maria's pedagogy)
WORLD_2_LEVELS = [
    LevelConfig(
        level_id="W2-L01",
        world=WorldID.W2,
        level_number=1,
        operation=Operation.ADDITION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=3,
        description="Combining groups up to 3"
    ),
    LevelConfig(
        level_id="W2-L02",
        world=WorldID.W2,
        level_number=2,
        operation=Operation.ADDITION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=4,
        description="Combining groups up to 4"
    ),
    LevelConfig(
        level_id="W2-L03",
        world=WorldID.W2,
        level_number=3,
        operation=Operation.ADDITION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=5,
        description="Combining groups up to 5"
    ),
    LevelConfig(
        level_id="W2-L04",
        world=WorldID.W2,
        level_number=4,
        operation=Operation.ADDITION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=5,
        description="Mastering sums to 5"
    ),
    LevelConfig(
        level_id="W2-L05",
        world=WorldID.W2,
        level_number=5,
        operation=Operation.ADDITION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=5,
        description="Fluency with sums to 5"
    ),
    LevelConfig(
        level_id="W2-L06",
        world=WorldID.W2,
        level_number=6,
        operation=Operation.ADDITION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=7,
        description="Combining groups up to 7"
    ),
    LevelConfig(
        level_id="W2-L07",
        world=WorldID.W2,
        level_number=7,
        operation=Operation.ADDITION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=8,
        description="Combining groups up to 8"
    ),
    LevelConfig(
        level_id="W2-L08",
        world=WorldID.W2,
        level_number=8,
        operation=Operation.ADDITION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=9,
        description="Combining groups up to 9"
    ),
    LevelConfig(
        level_id="W2-L09",
        world=WorldID.W2,
        level_number=9,
        operation=Operation.ADDITION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=10,
        description="Sums up to 10"
    ),
    LevelConfig(
        level_id="W2-L10",
        world=WorldID.W2,
        level_number=10,
        operation=Operation.ADDITION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=10,
        description="Mastering sums to 10"
    ),
]

# World 3: Subtraction curriculum (Dr. Maria's pedagogy)
WORLD_3_LEVELS = [
    LevelConfig(
        level_id="W3-L01",
        world=WorldID.W3,
        level_number=1,
        operation=Operation.SUBTRACTION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=3,
        description="Taking away from 3"
    ),
    LevelConfig(
        level_id="W3-L02",
        world=WorldID.W3,
        level_number=2,
        operation=Operation.SUBTRACTION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=4,
        description="Taking away from 4"
    ),
    LevelConfig(
        level_id="W3-L03",
        world=WorldID.W3,
        level_number=3,
        operation=Operation.SUBTRACTION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=5,
        description="Taking away from 5"
    ),
    LevelConfig(
        level_id="W3-L04",
        world=WorldID.W3,
        level_number=4,
        operation=Operation.SUBTRACTION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=5,
        description="Mastering subtraction from 5"
    ),
    LevelConfig(
        level_id="W3-L05",
        world=WorldID.W3,
        level_number=5,
        operation=Operation.SUBTRACTION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=5,
        description="Fluency subtracting from 5"
    ),
    LevelConfig(
        level_id="W3-L06",
        world=WorldID.W3,
        level_number=6,
        operation=Operation.SUBTRACTION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=7,
        description="Taking away from 7"
    ),
    LevelConfig(
        level_id="W3-L07",
        world=WorldID.W3,
        level_number=7,
        operation=Operation.SUBTRACTION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=8,
        description="Taking away from 8"
    ),
    LevelConfig(
        level_id="W3-L08",
        world=WorldID.W3,
        level_number=8,
        operation=Operation.SUBTRACTION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=9,
        description="Taking away from 9"
    ),
    LevelConfig(
        level_id="W3-L09",
        world=WorldID.W3,
        level_number=9,
        operation=Operation.SUBTRACTION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=10,
        description="Subtracting from 10"
    ),
    LevelConfig(
        level_id="W3-L10",
        world=WorldID.W3,
        level_number=10,
        operation=Operation.SUBTRACTION,
        cpa_stage=CPAStage.CONCRETE,
        max_value=10,
        description="Mastering subtraction from 10"
    ),
]


def get_level_config(level_id: str) -> Optional[LevelConfig]:
    """Get the configuration for a specific level."""
    all_levels = WORLD_2_LEVELS + WORLD_3_LEVELS
    for level in all_levels:
        if level.level_id == level_id:
            return level
    return None
