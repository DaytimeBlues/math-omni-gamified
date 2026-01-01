# tests/test_problem_factory.py
"""Tests for the Problem Factory."""
import pytest
from core.problem_factory import ProblemFactory
from core.problems import ProblemData


@pytest.fixture
def factory():
    return ProblemFactory()


def test_generate_returns_problem_data(factory: ProblemFactory):
    """Generated problems should return ProblemData dataclass."""
    problem = factory.generate(0)
    assert isinstance(problem, ProblemData)
    
    # Check required attributes exist
    assert hasattr(problem, 'correct_answer')
    assert hasattr(problem, 'prompt_text')
    assert hasattr(problem, 'options')
    assert hasattr(problem, 'item_name')


def test_generate_target_in_options(factory: ProblemFactory):
    """The target answer should always be in the options."""
    for level in range(10):
        problem = factory.generate(level)
        assert problem.correct_answer in problem.options, f"Target not in options at level {level}"


def test_generate_has_three_options(factory: ProblemFactory):
    """Should always generate exactly 3 options."""
    for level in range(10):
        problem = factory.generate(level)
        assert len(problem.options) == 3


def test_generate_options_are_unique(factory: ProblemFactory):
    """All options should be unique."""
    for level in range(10):
        problem = factory.generate(level)
        assert len(problem.options) == len(set(problem.options))


def test_generate_target_is_positive(factory: ProblemFactory):
    """Target should always be >= 1 for counting."""
    for level in range(10):
        problem = factory.generate(level)
        assert problem.correct_answer >= 1


def test_generate_options_are_positive(factory: ProblemFactory):
    """All options should be >= 1 for counting."""
    for level in range(10):
        problem = factory.generate(level)
        for opt in problem.options:
            assert opt >= 1, f"Option {opt} is not positive at level {level}"


def test_generate_difficulty_scaling(factory: ProblemFactory):
    """Higher levels should have larger max numbers (on average)."""
    level_0_targets = [factory.generate(0).correct_answer for _ in range(50)]
    level_9_targets = [factory.generate(9).correct_answer for _ in range(50)]
    
    avg_level_0 = sum(level_0_targets) / len(level_0_targets)
    avg_level_9 = sum(level_9_targets) / len(level_9_targets)
    
    # Level 9 should have higher average targets
    assert avg_level_9 > avg_level_0, "Higher levels should have larger numbers on average"


def test_generate_level_0_max_is_3(factory: ProblemFactory):
    """Level 0 should have max target of 3."""
    for _ in range(20):
        problem = factory.generate(0)
        assert problem.correct_answer <= 3, "Level 0 target should be <= 3"


def test_generate_item_name_is_string(factory: ProblemFactory):
    """Item name should be a non-empty string."""
    problem = factory.generate(0)
    assert isinstance(problem.item_name, str)
    assert len(problem.item_name) > 0


def test_generate_prompt_contains_item_name(factory: ProblemFactory):
    """Prompt should ask about counting something."""
    problem = factory.generate(0)
    assert "How many" in problem.prompt_text


def test_registry_pattern(factory: ProblemFactory):
    """Test the dynamic registry pattern."""
    # Check available modes
    assert "counting" in factory.available_modes
    assert "addition" in factory.available_modes
    assert "subtraction" in factory.available_modes


def test_set_mode(factory: ProblemFactory):
    """Test mode switching."""
    factory.set_mode("addition")
    assert factory.current_mode == "addition"
    
    factory.set_mode("subtraction")
    assert factory.current_mode == "subtraction"


def test_invalid_mode_raises(factory: ProblemFactory):
    """Invalid mode should raise ValueError."""
    with pytest.raises(ValueError):
        factory.set_mode("invalid_mode")
