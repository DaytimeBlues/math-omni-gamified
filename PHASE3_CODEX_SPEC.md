# Phase 3: Addition/Subtraction - Technical Specification

## Executive Summary

Phase 3 introduces Addition and Subtraction math worlds to Math Omni, extending the foundation counting functionality with new problem generation strategies and visual presentation modes.

## Architecture Overview

### Strategy Pattern Implementation

The problem generation system uses the Strategy Pattern to support multiple math domains:

```
┌─────────────────────────────────────────────────────────────────┐
│                      ProblemFactory                              │
│  - set_world(MathWorld)                                         │
│  - generate(level_idx, world?) -> dict                          │
│  - generate_problem(level_idx, world?) -> ProblemData           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    StrategyRegistry                              │
│  - get_strategy(MathWorld) -> ProblemStrategy                   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│CountingStrategy │ │AdditionStrategy │ │SubtractionStrategy  │
│ mode: SCATTER   │ │ mode: MERGE     │ │ mode: TAKE_AWAY     │
└─────────────────┘ └─────────────────┘ └─────────────────────┘
```

### Core Components

#### 1. MathWorld Enum (`core/problem_strategy.py`)

```python
class MathWorld(Enum):
    COUNTING = auto()      # Foundation: How many?
    ADDITION = auto()      # Phase 3: Combining groups
    SUBTRACTION = auto()   # Phase 3: Taking away
```

#### 2. VisualMode Enum

```python
class VisualMode(Enum):
    SCATTER = "scatter"      # Items in grouped rows (counting)
    MERGE = "merge"          # Two groups combined (addition)
    TAKE_AWAY = "take_away"  # Items removed from group (subtraction)
```

#### 3. VisualConfig Dataclass

```python
@dataclass
class VisualConfig:
    mode: VisualMode
    group_a: int          # First/main group count
    group_b: int = 0      # Second group or removal count
    emoji: str = "🍎"
    animation: Optional[str] = None
```

#### 4. ProblemData Dataclass

```python
@dataclass
class ProblemData:
    world: MathWorld
    level: int
    target: int
    options: List[int]
    prompt: str
    host_text: str
    emoji: str
    item_name: str
    visual_config: VisualConfig
    expression: Optional[str] = None  # e.g., "3 + 2"
```

## Visual Modes

### Scatter Mode (Counting)

Items displayed in grouped rows of 5 for subitizing:

```
🍎 🍎 🍎 🍎 🍎
🍎 🍎 🍎
```

### Merge Mode (Addition)

Two groups shown with a plus operator:

```
🍎 🍎 🍎  ➕  🍎 🍎
```

### Take Away Mode (Subtraction)

Full group with removed items indicated:

```
🍎 🍎 🍎  ➖  ❌ ❌
```

## Level-to-World Mapping

The `GameManager` maps levels to worlds using `WORLD_LEVEL_RANGES`:

| World | Level Range | Description |
|-------|-------------|-------------|
| COUNTING | 1-10 | Foundation counting |
| ADDITION | 11-20 | Addition problems |
| SUBTRACTION | 21-30 | Subtraction problems |

## API Reference

### ProblemFactory

```python
class ProblemFactory:
    def __init__(self, default_world: MathWorld = MathWorld.COUNTING)
    def set_world(self, world: MathWorld) -> None
    def generate(self, level_idx: int, world: Optional[MathWorld] = None) -> dict
    def generate_problem(self, level_idx: int, world: Optional[MathWorld] = None) -> ProblemData
```

### GameManager Extensions

```python
class GameManager:
    # Level ranges for each MathWorld
    WORLD_LEVEL_RANGES = {
        MathWorld.COUNTING: (1, 10),
        MathWorld.ADDITION: (11, 20),
        MathWorld.SUBTRACTION: (21, 30),
    }
    
    def _determine_world_for_level(self, level: int) -> MathWorld
    def _get_level_index_for_world(self, level: int, world: MathWorld) -> int
    def _start_level(self, level: int, world: Optional[MathWorld] = None)
```

### PremiumActivityView Extensions

```python
class PremiumActivityView:
    def set_activity(
        self,
        level: int,
        prompt: str,
        options: list,
        correct_answer: int,
        host_text: str,
        emoji: str,
        eggs: int,
        item_name: str = None,
        visual_config: Optional[Dict[str, Any]] = None,  # New
        world = None  # New
    )
    
    def _build_visual_from_config(self, config: Dict[str, Any]) -> str
    def _build_scatter_visual(self, emoji: str, count: int) -> str
    def _build_merge_visual(self, emoji: str, group_a: int, group_b: int) -> str
    def _build_take_away_visual(self, emoji: str, total: int, removed: int) -> str
```

## Difficulty Scaling

### Counting (Levels 1-10)

- Level 1: Counts 1-3
- Level 10: Counts 10-20

### Addition (Levels 11-20)

- Levels 11-13: Sums 2-5 (small addends)
- Levels 14-16: Sums 5-10 (medium addends)
- Levels 17-20: Sums 10-20 (larger addends)

### Subtraction (Levels 21-30)

- Levels 21-23: Start 3-5, simple subtractions
- Levels 24-26: Start 6-10, medium subtractions
- Levels 27-30: Start 10-20, larger subtractions

## Offline-First Guarantees

All problem generation is:
- **Deterministic**: Uses local random number generation
- **No network required**: All data is computed client-side
- **Asset-local**: Emojis and items from `config.CONCRETE_ITEMS`

## PyQt6 Compatibility

- Uses `pyqtSignal` for event communication
- All animations use `QPropertyAnimation` with `QEasingCurve`
- Visual updates through `QLabel.setText()`
- No web views or external rendering

## Testing Strategy

### Unit Tests

1. `test_problem_strategy.py` - Strategy pattern implementations
2. `test_problem_factory.py` - Factory generation with world selection

### Integration Tests

1. `test_game_manager.py` - Level-to-world mapping
2. `test_premium_activity_view.py` - Visual mode rendering

## Migration Notes

### Backwards Compatibility

- `ProblemFactory.generate()` accepts optional `world` parameter
- Default world is `MathWorld.COUNTING`
- Legacy calls without `visual_config` fall back to scatter mode

### Breaking Changes

None - all changes are additive.

## Files Modified

| File | Changes |
|------|---------|
| `core/problem_strategy.py` | New: Enum, dataclasses, strategy classes |
| `core/problem_factory.py` | Updated: Strategy pattern delegation |
| `ui/game_manager.py` | Updated: MathWorld enum usage, world mapping |
| `ui/premium_activity_view.py` | Updated: visual_config handling |

## Future Extensions (Phase 4+)

- **Multiplication World**: Grid/array visual mode
- **Division World**: Sharing/grouping visual mode
- **Mixed Operations**: Operator selection problems
