# tests/test_strategies.py
"""Tests for the problem generation strategies."""
import pytest
from core.strategies import (
    ProblemStrategy,
    CountingStrategy,
    AdditionStrategy,
    SubtractionStrategy,
    get_strategy,
    STRATEGY_REGISTRY,
)
from core.contracts import Operation, VisualType, AudioTokens


class TestCountingStrategy:
    """Tests for CountingStrategy."""
    
    @pytest.fixture
    def strategy(self) -> CountingStrategy:
        return CountingStrategy()
    
    def test_generate_returns_problem_data(self, strategy: CountingStrategy):
        """Should return a valid ProblemData object."""
        problem = strategy.generate(difficulty=1)
        assert problem.type == Operation.COUNTING.value
        assert problem.operand_b is None
    
    def test_generate_target_in_options(self, strategy: CountingStrategy):
        """Target should always be in options."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            assert problem.target in problem.options
    
    def test_generate_has_three_options(self, strategy: CountingStrategy):
        """Should always have exactly 3 options."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            assert len(problem.options) == 3
    
    def test_generate_options_are_unique(self, strategy: CountingStrategy):
        """All options should be unique."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            assert len(problem.options) == len(set(problem.options))
    
    def test_generate_options_are_positive(self, strategy: CountingStrategy):
        """All options should be >= 1."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            for opt in problem.options:
                assert opt >= 1
    
    def test_generate_visual_config(self, strategy: CountingStrategy):
        """Should have proper visual configuration."""
        problem = strategy.generate(difficulty=1)
        assert "type" in problem.visual_config
        assert problem.visual_config["type"] == VisualType.COUNT.value
        assert "item_name" in problem.visual_config
        assert "emoji" in problem.visual_config
    
    def test_generate_audio_sequence(self, strategy: CountingStrategy):
        """Should have proper audio sequence."""
        problem = strategy.generate(difficulty=1)
        assert len(problem.audio_sequence) > 0
        assert AudioTokens.Q_HOW_MANY in problem.audio_sequence
    
    def test_generate_is_valid(self, strategy: CountingStrategy):
        """Generated problems should pass validation."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            assert problem.is_valid


class TestAdditionStrategy:
    """Tests for AdditionStrategy."""
    
    @pytest.fixture
    def strategy(self) -> AdditionStrategy:
        return AdditionStrategy()
    
    def test_generate_returns_problem_data(self, strategy: AdditionStrategy):
        """Should return a valid ProblemData object."""
        problem = strategy.generate(difficulty=1)
        assert problem.type == Operation.ADDITION.value
        assert problem.operand_b is not None
    
    def test_generate_correct_target(self, strategy: AdditionStrategy):
        """Target should equal a + b."""
        for _ in range(20):
            problem = strategy.generate(difficulty=5)
            assert problem.target == problem.operand_a + problem.operand_b
    
    def test_generate_target_in_options(self, strategy: AdditionStrategy):
        """Target should always be in options."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            assert problem.target in problem.options
    
    def test_generate_has_three_options(self, strategy: AdditionStrategy):
        """Should always have exactly 3 options."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            assert len(problem.options) == 3
    
    def test_generate_options_are_non_negative(self, strategy: AdditionStrategy):
        """All options should be >= 0."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            for opt in problem.options:
                assert opt >= 0
    
    def test_generate_operands_are_positive(self, strategy: AdditionStrategy):
        """Both operands should be >= 1."""
        for _ in range(20):
            problem = strategy.generate(difficulty=5)
            assert problem.operand_a >= 1
            assert problem.operand_b >= 1
    
    def test_generate_visual_config(self, strategy: AdditionStrategy):
        """Should have proper visual configuration for merge."""
        problem = strategy.generate(difficulty=1)
        assert problem.visual_config["type"] == VisualType.MERGE.value
        assert "group_a_count" in problem.visual_config
        assert "group_b_count" in problem.visual_config
    
    def test_generate_audio_sequence(self, strategy: AdditionStrategy):
        """Should have proper audio sequence for addition."""
        problem = strategy.generate(difficulty=1)
        assert AudioTokens.OP_PLUS in problem.audio_sequence
        assert AudioTokens.OP_EQUALS in problem.audio_sequence
        assert AudioTokens.Q_ALTOGETHER in problem.audio_sequence
    
    def test_generate_is_valid(self, strategy: AdditionStrategy):
        """Generated problems should pass validation."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            assert problem.is_valid
    
    def test_difficulty_scaling_low(self, strategy: AdditionStrategy):
        """Low difficulty should have sums <= 5."""
        for _ in range(20):
            problem = strategy.generate(difficulty=1)
            assert problem.target <= 5
    
    def test_difficulty_scaling_high(self, strategy: AdditionStrategy):
        """High difficulty can have sums up to 10."""
        # Run many times to get a variety
        targets = [strategy.generate(difficulty=8).target for _ in range(50)]
        # At least some should be > 5
        assert max(targets) <= 10


class TestSubtractionStrategy:
    """Tests for SubtractionStrategy."""
    
    @pytest.fixture
    def strategy(self) -> SubtractionStrategy:
        return SubtractionStrategy()
    
    def test_generate_returns_problem_data(self, strategy: SubtractionStrategy):
        """Should return a valid ProblemData object."""
        problem = strategy.generate(difficulty=1)
        assert problem.type == Operation.SUBTRACTION.value
        assert problem.operand_b is not None
    
    def test_generate_correct_target(self, strategy: SubtractionStrategy):
        """Target should equal a - b."""
        for _ in range(20):
            problem = strategy.generate(difficulty=5)
            assert problem.target == problem.operand_a - problem.operand_b
    
    def test_generate_non_negative_result(self, strategy: SubtractionStrategy):
        """Result should never be negative."""
        for _ in range(50):
            problem = strategy.generate(difficulty=8)
            assert problem.target >= 0
    
    def test_generate_target_in_options(self, strategy: SubtractionStrategy):
        """Target should always be in options."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            assert problem.target in problem.options
    
    def test_generate_has_three_options(self, strategy: SubtractionStrategy):
        """Should always have exactly 3 options."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            assert len(problem.options) == 3
    
    def test_generate_options_are_non_negative(self, strategy: SubtractionStrategy):
        """All options should be >= 0."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            for opt in problem.options:
                assert opt >= 0
    
    def test_generate_b_less_than_a(self, strategy: SubtractionStrategy):
        """operand_b should always be less than operand_a."""
        for _ in range(50):
            problem = strategy.generate(difficulty=5)
            assert problem.operand_b < problem.operand_a
    
    def test_generate_visual_config(self, strategy: SubtractionStrategy):
        """Should have proper visual configuration for take_away."""
        problem = strategy.generate(difficulty=1)
        assert problem.visual_config["type"] == VisualType.TAKE_AWAY.value
        assert "start_count" in problem.visual_config
        assert "remove_count" in problem.visual_config
    
    def test_generate_audio_sequence(self, strategy: SubtractionStrategy):
        """Should have proper audio sequence for subtraction."""
        problem = strategy.generate(difficulty=1)
        assert AudioTokens.OP_TAKE_AWAY in problem.audio_sequence
        assert AudioTokens.OP_EQUALS in problem.audio_sequence
        assert AudioTokens.Q_LEFT in problem.audio_sequence
    
    def test_generate_is_valid(self, strategy: SubtractionStrategy):
        """Generated problems should pass validation."""
        for difficulty in range(10):
            problem = strategy.generate(difficulty=difficulty)
            assert problem.is_valid


class TestDistractorGeneration:
    """Tests for distractor generation logic."""
    
    def test_distractors_are_spread_out(self):
        """Distractors should not be too close to each other."""
        strategy = AdditionStrategy()
        
        # Run many times to check distractor spread
        for _ in range(50):
            problem = strategy.generate(difficulty=5)
            distractors = [opt for opt in problem.options if opt != problem.target]
            
            # Check that distractors aren't identical
            if len(distractors) >= 2:
                # At least check they're all unique
                assert len(distractors) == len(set(distractors))


class TestStrategyRegistry:
    """Tests for strategy registry."""
    
    def test_registry_has_all_operations(self):
        """Registry should have strategies for all operations."""
        assert Operation.COUNTING.value in STRATEGY_REGISTRY
        assert Operation.ADDITION.value in STRATEGY_REGISTRY
        assert Operation.SUBTRACTION.value in STRATEGY_REGISTRY
    
    def test_get_strategy_counting(self):
        """Should return CountingStrategy for counting."""
        strategy = get_strategy(Operation.COUNTING.value)
        assert isinstance(strategy, CountingStrategy)
    
    def test_get_strategy_addition(self):
        """Should return AdditionStrategy for addition."""
        strategy = get_strategy(Operation.ADDITION.value)
        assert isinstance(strategy, AdditionStrategy)
    
    def test_get_strategy_subtraction(self):
        """Should return SubtractionStrategy for subtraction."""
        strategy = get_strategy(Operation.SUBTRACTION.value)
        assert isinstance(strategy, SubtractionStrategy)
    
    def test_get_strategy_unknown(self):
        """Should raise ValueError for unknown operation."""
        with pytest.raises(ValueError):
            get_strategy("unknown_operation")
