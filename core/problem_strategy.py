"""
Problem Strategy - Strategy Pattern for Math Problem Generation

Phase 3: Supports Counting, Addition, and Subtraction worlds.

Architecture:
- MathWorld enum defines available math domains
- ProblemStrategy abstract base class defines the contract
- Concrete strategies implement world-specific problem generation
- Visual modes: 'scatter' (counting), 'merge' (addition), 'take_away' (subtraction)
"""

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional

from config import CONCRETE_ITEMS


class MathWorld(Enum):
    """
    Available math worlds/domains.
    
    Each world has its own problem generation strategy and visual mode.
    """
    COUNTING = auto()      # Foundation: How many?
    ADDITION = auto()      # Phase 3: Combining groups
    SUBTRACTION = auto()   # Phase 3: Taking away


class VisualMode(Enum):
    """
    Visual presentation modes for activity view.
    
    - SCATTER: Items displayed in random/grouped arrangement (counting)
    - MERGE: Two groups shown separately, then combined (addition)
    - TAKE_AWAY: Full group shown, some removed (subtraction)
    """
    SCATTER = "scatter"
    MERGE = "merge"
    TAKE_AWAY = "take_away"


@dataclass
class VisualConfig:
    """
    Configuration for how items are displayed in the activity view.
    
    Attributes:
        mode: The visual presentation mode
        group_a: First group of items (or main group for scatter/take_away)
        group_b: Second group for merge mode, or items to remove for take_away
        emoji: The emoji to display
        animation: Optional animation hint (e.g., 'slide_in', 'fade_out')
    """
    mode: VisualMode
    group_a: int
    group_b: int = 0
    emoji: str = "🍎"
    animation: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "mode": self.mode.value,
            "group_a": self.group_a,
            "group_b": self.group_b,
            "emoji": self.emoji,
            "animation": self.animation,
        }


@dataclass
class ProblemData:
    """
    Unified problem data structure for all math worlds.
    
    Attributes:
        world: The MathWorld this problem belongs to
        level: 1-indexed level number
        target: The correct answer
        options: List of answer choices (including target)
        prompt: Question text to display
        host_text: Voiceover/encouragement text
        emoji: Item emoji for display
        item_name: Item name for VoiceBank lookup
        visual_config: Configuration for visual presentation
        expression: Optional math expression (e.g., "3 + 2")
    """
    world: MathWorld
    level: int
    target: int
    options: List[int]
    prompt: str
    host_text: str
    emoji: str
    item_name: str
    visual_config: VisualConfig
    expression: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for backwards compatibility."""
        return {
            "world": self.world.name,
            "level": self.level,
            "target": self.target,
            "options": self.options,
            "prompt": self.prompt,
            "host": self.host_text,
            "emoji": self.emoji,
            "item_name": self.item_name,
            "visual_config": self.visual_config.to_dict(),
            "expression": self.expression,
        }


class ProblemStrategy(ABC):
    """
    Abstract base class for problem generation strategies.
    
    Each concrete strategy implements world-specific problem generation
    while adhering to a common interface.
    """
    
    @property
    @abstractmethod
    def world(self) -> MathWorld:
        """Return the MathWorld this strategy handles."""
        pass
    
    @property
    @abstractmethod
    def visual_mode(self) -> VisualMode:
        """Return the default visual mode for this strategy."""
        pass
    
    @abstractmethod
    def generate(self, level_idx: int) -> ProblemData:
        """
        Generate a problem for the given level index (0-based).
        
        Args:
            level_idx: 0-based level index (0-9 typically)
            
        Returns:
            ProblemData with all necessary information for display
        """
        pass
    
    def _select_item(self) -> dict:
        """Select a random concrete item."""
        return random.choice(CONCRETE_ITEMS)
    
    def _generate_distractors(self, target: int, count: int = 2, 
                               min_val: int = 0, max_val: int = 20) -> List[int]:
        """
        Generate distractor options close to the target.
        
        Args:
            target: The correct answer
            count: Number of distractors to generate
            min_val: Minimum allowed value (default 0)
            max_val: Maximum allowed value (default 20)
            
        Returns:
            List of distractor values
        """
        options = set()
        attempts = 0
        offsets = [-1, 1, -2, 2, -3, 3]
        
        while len(options) < count and attempts < 20:
            offset = random.choice(offsets)
            distractor = target + offset
            if min_val <= distractor <= max_val and distractor != target:
                options.add(distractor)
            attempts += 1
        
        # Ensure we have enough distractors
        while len(options) < count:
            fallback = random.randint(min_val, max_val)
            if fallback != target:
                options.add(fallback)
        
        return list(options)[:count]


# =============================================================================
# COUNTING STRATEGY (Foundation)
# =============================================================================

class CountingStrategy(ProblemStrategy):
    """
    Strategy for counting problems (Phase 1/2).
    
    "How many X?" - Child counts scattered items.
    Visual: SCATTER mode with grouped display.
    """
    
    HOST_PROMPTS = [
        "How many can you count?",
        "Let's count together!",
        "Can you count these?",
        "Count carefully!",
        "How many do you see?",
        "Take your time and count!",
    ]
    
    @property
    def world(self) -> MathWorld:
        return MathWorld.COUNTING
    
    @property
    def visual_mode(self) -> VisualMode:
        return VisualMode.SCATTER
    
    def generate(self, level_idx: int) -> ProblemData:
        """
        Generate a counting problem.
        
        Level 0 -> Counts 1-3
        Level 9 -> Counts 10-20
        """
        # Linear difficulty scaling
        max_n = 3 + (level_idx * 2)
        max_n = min(max_n, 20)  # Cap at 20 for foundation year
        target = random.randint(1, max_n)
        
        item = self._select_item()
        distractors = self._generate_distractors(target, count=2, min_val=1)
        
        options = [target] + distractors
        random.shuffle(options)
        
        visual_config = VisualConfig(
            mode=self.visual_mode,
            group_a=target,
            emoji=item['emoji'],
        )
        
        return ProblemData(
            world=self.world,
            level=level_idx + 1,
            target=target,
            options=options,
            prompt=f"How many {item['name']}?",
            host_text=random.choice(self.HOST_PROMPTS),
            emoji=item['emoji'],
            item_name=item['name'],
            visual_config=visual_config,
        )


# =============================================================================
# ADDITION STRATEGY (Phase 3)
# =============================================================================

class AdditionStrategy(ProblemStrategy):
    """
    Strategy for addition problems (Phase 3).
    
    "X + Y = ?" - Child sees two groups merge.
    Visual: MERGE mode with animated combination.
    """
    
    HOST_PROMPTS = [
        "Let's add them together!",
        "Put them all together!",
        "How many in total?",
        "Add the groups!",
        "What's the sum?",
        "Count them all!",
    ]
    
    @property
    def world(self) -> MathWorld:
        return MathWorld.ADDITION
    
    @property
    def visual_mode(self) -> VisualMode:
        return VisualMode.MERGE
    
    def generate(self, level_idx: int) -> ProblemData:
        """
        Generate an addition problem.
        
        Level 0 -> Sums up to 5 (1+1 to 2+3)
        Level 9 -> Sums up to 20 (larger addends)
        """
        # Progressive difficulty
        if level_idx < 3:
            # Easy: sums 2-5
            max_sum = 5
            max_addend = 3
        elif level_idx < 6:
            # Medium: sums 5-10
            max_sum = 10
            max_addend = 6
        else:
            # Hard: sums 10-20
            max_sum = 20
            max_addend = 10
        
        # Generate addends
        a = random.randint(1, max_addend)
        b = random.randint(1, min(max_addend, max_sum - a))
        target = a + b
        
        item = self._select_item()
        distractors = self._generate_distractors(target, count=2, min_val=2, max_val=max_sum)
        
        options = [target] + distractors
        random.shuffle(options)
        
        expression = f"{a} + {b}"
        
        visual_config = VisualConfig(
            mode=self.visual_mode,
            group_a=a,
            group_b=b,
            emoji=item['emoji'],
            animation="slide_merge",
        )
        
        return ProblemData(
            world=self.world,
            level=level_idx + 1,
            target=target,
            options=options,
            prompt=f"{a} + {b} = ?",
            host_text=random.choice(self.HOST_PROMPTS),
            emoji=item['emoji'],
            item_name=item['name'],
            visual_config=visual_config,
            expression=expression,
        )


# =============================================================================
# SUBTRACTION STRATEGY (Phase 3)
# =============================================================================

class SubtractionStrategy(ProblemStrategy):
    """
    Strategy for subtraction problems (Phase 3).
    
    "X - Y = ?" - Child sees items taken away.
    Visual: TAKE_AWAY mode with animated removal.
    """
    
    HOST_PROMPTS = [
        "How many are left?",
        "Take some away!",
        "What's left over?",
        "Subtract them!",
        "How many remain?",
        "Count what's left!",
    ]
    
    @property
    def world(self) -> MathWorld:
        return MathWorld.SUBTRACTION
    
    @property
    def visual_mode(self) -> VisualMode:
        return VisualMode.TAKE_AWAY
    
    def generate(self, level_idx: int) -> ProblemData:
        """
        Generate a subtraction problem.
        
        Level 0 -> Simple subtractions (5-1, 4-2)
        Level 9 -> Larger numbers (15-7, 20-9)
        """
        # Progressive difficulty
        if level_idx < 3:
            # Easy: start with 3-5
            max_start = 5
        elif level_idx < 6:
            # Medium: start with 6-10
            max_start = 10
        else:
            # Hard: start with 10-20
            max_start = 20
        
        # Generate operands (ensure positive result)
        start = random.randint(3, max_start)
        subtract = random.randint(1, start - 1)
        target = start - subtract
        
        item = self._select_item()
        distractors = self._generate_distractors(target, count=2, min_val=0, max_val=start)
        
        options = [target] + distractors
        random.shuffle(options)
        
        expression = f"{start} - {subtract}"
        
        visual_config = VisualConfig(
            mode=self.visual_mode,
            group_a=start,
            group_b=subtract,  # Number to remove
            emoji=item['emoji'],
            animation="fade_out",
        )
        
        return ProblemData(
            world=self.world,
            level=level_idx + 1,
            target=target,
            options=options,
            prompt=f"{start} - {subtract} = ?",
            host_text=random.choice(self.HOST_PROMPTS),
            emoji=item['emoji'],
            item_name=item['name'],
            visual_config=visual_config,
            expression=expression,
        )


# =============================================================================
# STRATEGY REGISTRY
# =============================================================================

class StrategyRegistry:
    """
    Registry for problem generation strategies.
    
    Provides factory method to get appropriate strategy for a MathWorld.
    """
    
    _strategies = {
        MathWorld.COUNTING: CountingStrategy,
        MathWorld.ADDITION: AdditionStrategy,
        MathWorld.SUBTRACTION: SubtractionStrategy,
    }
    
    @classmethod
    def get_strategy(cls, world: MathWorld) -> ProblemStrategy:
        """Get strategy instance for the given world."""
        strategy_class = cls._strategies.get(world)
        if not strategy_class:
            raise ValueError(f"No strategy registered for world: {world}")
        return strategy_class()
    
    @classmethod
    def register(cls, world: MathWorld, strategy_class: type):
        """Register a new strategy for a world."""
        cls._strategies[world] = strategy_class
