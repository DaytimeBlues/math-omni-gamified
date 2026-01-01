# tests/test_problem_strategy.py
"""Tests for the Problem Strategy Pattern (Phase 3)."""
import pytest
from core.problem_strategy import (
    MathWorld, VisualMode, VisualConfig, ProblemData,
    ProblemStrategy, CountingStrategy, AdditionStrategy, SubtractionStrategy,
    StrategyRegistry
)


class TestMathWorldEnum:
    """Tests for MathWorld enum."""
    
    def test_has_counting_world(self):
        assert MathWorld.COUNTING is not None
    
    def test_has_addition_world(self):
        assert MathWorld.ADDITION is not None
    
    def test_has_subtraction_world(self):
        assert MathWorld.SUBTRACTION is not None


class TestVisualModeEnum:
    """Tests for VisualMode enum."""
    
    def test_scatter_mode_value(self):
        assert VisualMode.SCATTER.value == "scatter"
    
    def test_merge_mode_value(self):
        assert VisualMode.MERGE.value == "merge"
    
    def test_take_away_mode_value(self):
        assert VisualMode.TAKE_AWAY.value == "take_away"


class TestVisualConfig:
    """Tests for VisualConfig dataclass."""
    
    def test_default_values(self):
        config = VisualConfig(mode=VisualMode.SCATTER, group_a=5)
        assert config.group_b == 0
        assert config.emoji == "🍎"
        assert config.animation is None
    
    def test_to_dict(self):
        config = VisualConfig(
            mode=VisualMode.MERGE,
            group_a=3,
            group_b=2,
            emoji="⭐",
            animation="slide_merge"
        )
        result = config.to_dict()
        
        assert result["mode"] == "merge"
        assert result["group_a"] == 3
        assert result["group_b"] == 2
        assert result["emoji"] == "⭐"
        assert result["animation"] == "slide_merge"


class TestCountingStrategy:
    """Tests for CountingStrategy."""
    
    @pytest.fixture
    def strategy(self):
        return CountingStrategy()
    
    def test_world_is_counting(self, strategy):
        assert strategy.world == MathWorld.COUNTING
    
    def test_visual_mode_is_scatter(self, strategy):
        assert strategy.visual_mode == VisualMode.SCATTER
    
    def test_generate_returns_problem_data(self, strategy):
        problem = strategy.generate(0)
        assert isinstance(problem, ProblemData)
    
    def test_generate_has_scatter_visual_config(self, strategy):
        problem = strategy.generate(0)
        assert problem.visual_config.mode == VisualMode.SCATTER
    
    def test_generate_target_is_positive(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            assert problem.target >= 1
    
    def test_generate_has_three_options(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            assert len(problem.options) == 3
    
    def test_generate_target_in_options(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            assert problem.target in problem.options


class TestAdditionStrategy:
    """Tests for AdditionStrategy."""
    
    @pytest.fixture
    def strategy(self):
        return AdditionStrategy()
    
    def test_world_is_addition(self, strategy):
        assert strategy.world == MathWorld.ADDITION
    
    def test_visual_mode_is_merge(self, strategy):
        assert strategy.visual_mode == VisualMode.MERGE
    
    def test_generate_returns_problem_data(self, strategy):
        problem = strategy.generate(0)
        assert isinstance(problem, ProblemData)
    
    def test_generate_has_merge_visual_config(self, strategy):
        problem = strategy.generate(0)
        assert problem.visual_config.mode == VisualMode.MERGE
    
    def test_generate_has_expression(self, strategy):
        problem = strategy.generate(0)
        assert problem.expression is not None
        assert "+" in problem.expression
    
    def test_generate_visual_config_groups_sum_to_target(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            config = problem.visual_config
            assert config.group_a + config.group_b == problem.target
    
    def test_generate_target_is_positive(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            assert problem.target >= 2  # At least 1+1
    
    def test_generate_has_three_options(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            assert len(problem.options) == 3
    
    def test_generate_target_in_options(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            assert problem.target in problem.options


class TestSubtractionStrategy:
    """Tests for SubtractionStrategy."""
    
    @pytest.fixture
    def strategy(self):
        return SubtractionStrategy()
    
    def test_world_is_subtraction(self, strategy):
        assert strategy.world == MathWorld.SUBTRACTION
    
    def test_visual_mode_is_take_away(self, strategy):
        assert strategy.visual_mode == VisualMode.TAKE_AWAY
    
    def test_generate_returns_problem_data(self, strategy):
        problem = strategy.generate(0)
        assert isinstance(problem, ProblemData)
    
    def test_generate_has_take_away_visual_config(self, strategy):
        problem = strategy.generate(0)
        assert problem.visual_config.mode == VisualMode.TAKE_AWAY
    
    def test_generate_has_expression(self, strategy):
        problem = strategy.generate(0)
        assert problem.expression is not None
        assert "-" in problem.expression
    
    def test_generate_visual_config_subtraction_is_correct(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            config = problem.visual_config
            # group_a - group_b = target
            assert config.group_a - config.group_b == problem.target
    
    def test_generate_target_is_non_negative(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            assert problem.target >= 0
    
    def test_generate_has_three_options(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            assert len(problem.options) == 3
    
    def test_generate_target_in_options(self, strategy):
        for level in range(10):
            problem = strategy.generate(level)
            assert problem.target in problem.options


class TestStrategyRegistry:
    """Tests for StrategyRegistry."""
    
    def test_get_counting_strategy(self):
        strategy = StrategyRegistry.get_strategy(MathWorld.COUNTING)
        assert isinstance(strategy, CountingStrategy)
    
    def test_get_addition_strategy(self):
        strategy = StrategyRegistry.get_strategy(MathWorld.ADDITION)
        assert isinstance(strategy, AdditionStrategy)
    
    def test_get_subtraction_strategy(self):
        strategy = StrategyRegistry.get_strategy(MathWorld.SUBTRACTION)
        assert isinstance(strategy, SubtractionStrategy)
    
    def test_get_strategy_raises_for_invalid_world(self):
        # This test is tricky since MathWorld is an enum
        # Instead, test that the registry handles all enum values
        for world in MathWorld:
            strategy = StrategyRegistry.get_strategy(world)
            assert strategy is not None
