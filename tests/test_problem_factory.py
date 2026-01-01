# tests/test_problem_factory.py
"""Tests for the Problem Factory."""
import pytest
from core.problem_factory import ProblemFactory
from core.contracts import (
    Operation, 
    ProblemData, 
    MathWorld, 
    WorldID,
    VisualType,
    get_operation_for_world,
)


@pytest.fixture
def factory():
    return ProblemFactory()


# =============================================================================
# LEGACY API TESTS (Backward Compatibility)
# =============================================================================

def test_generate_returns_required_keys(factory: ProblemFactory):
    """Generated problems should have all required keys."""
    problem = factory.generate(0)
    
    required_keys = ['level', 'target', 'options', 'prompt', 'emoji', 'host']
    for key in required_keys:
        assert key in problem, f"Missing key: {key}"


def test_generate_target_in_options(factory: ProblemFactory):
    """The target answer should always be in the options."""
    for level in range(10):
        problem = factory.generate(level)
        assert problem['target'] in problem['options'], f"Target not in options at level {level}"


def test_generate_has_three_options(factory: ProblemFactory):
    """Should always generate exactly 3 options."""
    for level in range(10):
        problem = factory.generate(level)
        assert len(problem['options']) == 3


def test_generate_options_are_unique(factory: ProblemFactory):
    """All options should be unique."""
    for level in range(10):
        problem = factory.generate(level)
        assert len(problem['options']) == len(set(problem['options']))


def test_generate_target_is_positive(factory: ProblemFactory):
    """Target should always be >= 1."""
    for level in range(10):
        problem = factory.generate(level)
        assert problem['target'] >= 1


def test_generate_options_are_positive(factory: ProblemFactory):
    """All options should be >= 1."""
    for level in range(10):
        problem = factory.generate(level)
        for opt in problem['options']:
            assert opt >= 1, f"Option {opt} is not positive at level {level}"


def test_generate_difficulty_scaling(factory: ProblemFactory):
    """Higher levels should have larger max numbers (on average)."""
    # Generate many problems to check statistical trend
    level_0_targets = [factory.generate(0)['target'] for _ in range(50)]
    level_9_targets = [factory.generate(9)['target'] for _ in range(50)]
    
    avg_level_0 = sum(level_0_targets) / len(level_0_targets)
    avg_level_9 = sum(level_9_targets) / len(level_9_targets)
    
    # Level 9 should have higher average targets
    assert avg_level_9 > avg_level_0, "Higher levels should have larger numbers on average"


def test_generate_level_0_max_is_3(factory: ProblemFactory):
    """Level 0 should have max target of 3."""
    for _ in range(20):
        problem = factory.generate(0)
        assert problem['target'] <= 3, "Level 0 target should be <= 3"


def test_generate_level_is_correct(factory: ProblemFactory):
    """Level in output should match input + 1."""
    for level_idx in range(10):
        problem = factory.generate(level_idx)
        assert problem['level'] == level_idx + 1


def test_generate_emoji_is_string(factory: ProblemFactory):
    """Emoji should be a non-empty string."""
    problem = factory.generate(0)
    assert isinstance(problem['emoji'], str)
    assert len(problem['emoji']) > 0


def test_generate_prompt_contains_item_name(factory: ProblemFactory):
    """Prompt should ask about counting something."""
    problem = factory.generate(0)
    assert "How many" in problem['prompt']


# =============================================================================
# NEW API TESTS (Strategy Pattern)
# =============================================================================

class TestGenerateProblem:
    """Tests for the new generate_problem method."""
    
    def test_generate_problem_counting(self, factory: ProblemFactory):
        """Should generate counting problems."""
        problem = factory.generate_problem(Operation.COUNTING.value, difficulty=1)
        assert isinstance(problem, ProblemData)
        assert problem.type == Operation.COUNTING.value
        assert problem.is_valid
    
    def test_generate_problem_addition(self, factory: ProblemFactory):
        """Should generate addition problems."""
        problem = factory.generate_problem(Operation.ADDITION.value, difficulty=3)
        assert isinstance(problem, ProblemData)
        assert problem.type == Operation.ADDITION.value
        assert problem.operand_b is not None
        assert problem.target == problem.operand_a + problem.operand_b
        assert problem.is_valid
    
    def test_generate_problem_subtraction(self, factory: ProblemFactory):
        """Should generate subtraction problems."""
        problem = factory.generate_problem(Operation.SUBTRACTION.value, difficulty=3)
        assert isinstance(problem, ProblemData)
        assert problem.type == Operation.SUBTRACTION.value
        assert problem.operand_b is not None
        assert problem.target == problem.operand_a - problem.operand_b
        assert problem.is_valid
    
    def test_generate_problem_unknown_operation(self, factory: ProblemFactory):
        """Should raise ValueError for unknown operation."""
        with pytest.raises(ValueError):
            factory.generate_problem("unknown_op", difficulty=1)


class TestGenerateForLevel:
    """Tests for the generate_for_level method."""
    
    def test_generate_for_level_w2_l01(self, factory: ProblemFactory):
        """Should generate addition for W2-L01."""
        problem = factory.generate_for_level("W2-L01")
        assert problem.type == Operation.ADDITION.value
        assert problem.is_valid
    
    def test_generate_for_level_w3_l05(self, factory: ProblemFactory):
        """Should generate subtraction for W3-L05."""
        problem = factory.generate_for_level("W3-L05")
        assert problem.type == Operation.SUBTRACTION.value
        assert problem.is_valid
    
    def test_generate_for_level_unknown(self, factory: ProblemFactory):
        """Should raise ValueError for unknown level."""
        with pytest.raises(ValueError):
            factory.generate_for_level("W99-L01")


class TestGenerateAsDict:
    """Tests for the generate_as_dict method."""
    
    def test_generate_as_dict_addition(self, factory: ProblemFactory):
        """Should return dict format for addition."""
        result = factory.generate_as_dict(
            operation=Operation.ADDITION.value,
            difficulty=3,
            level_idx=2
        )
        assert isinstance(result, dict)
        assert result['type'] == Operation.ADDITION.value
        assert result['level'] == 3
        assert 'host' in result
    
    def test_generate_as_dict_has_visual_config(self, factory: ProblemFactory):
        """Should include visual_config in dict output."""
        result = factory.generate_as_dict(
            operation=Operation.SUBTRACTION.value,
            difficulty=5,
            level_idx=4
        )
        assert 'visual_config' in result
        assert 'audio_sequence' in result


class TestGenerateForWorld:
    """Tests for the generate_for_world method (Phase 3)."""
    
    def test_generate_for_world_counting(self, factory: ProblemFactory):
        """Should generate counting problems for W1."""
        result = factory.generate_for_world(MathWorld.W1, level_in_world=3)
        assert isinstance(result, dict)
        assert result['type'] == Operation.COUNTING.value
        assert result['level'] == 3
    
    def test_generate_for_world_addition(self, factory: ProblemFactory):
        """Should generate addition problems for W2."""
        result = factory.generate_for_world(MathWorld.W2, level_in_world=5)
        assert result['type'] == Operation.ADDITION.value
        assert result['level'] == 5
        assert 'visual_config' in result
        assert result['visual_config']['type'] == VisualType.MERGE.value
    
    def test_generate_for_world_subtraction(self, factory: ProblemFactory):
        """Should generate subtraction problems for W3."""
        result = factory.generate_for_world(MathWorld.W3, level_in_world=7)
        assert result['type'] == Operation.SUBTRACTION.value
        assert result['level'] == 7
        assert 'visual_config' in result
        assert result['visual_config']['type'] == VisualType.TAKE_AWAY.value
    
    def test_generate_for_world_has_required_keys(self, factory: ProblemFactory):
        """Should have all required keys for game manager."""
        result = factory.generate_for_world(MathWorld.W2, level_in_world=1)
        required_keys = [
            'type', 'level', 'target', 'options', 'prompt',
            'emoji', 'item_name', 'host', 'visual_config', 'audio_sequence'
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"


class TestMathWorldHelpers:
    """Tests for MathWorld enum and helpers."""
    
    def test_math_world_is_alias_for_world_id(self):
        """MathWorld should be an alias for WorldID."""
        assert MathWorld is WorldID
        assert MathWorld.W1 == WorldID.W1
    
    def test_get_operation_for_world_counting(self):
        """W1 should map to counting."""
        assert get_operation_for_world(MathWorld.W1) == Operation.COUNTING.value
    
    def test_get_operation_for_world_addition(self):
        """W2 should map to addition."""
        assert get_operation_for_world(MathWorld.W2) == Operation.ADDITION.value
    
    def test_get_operation_for_world_subtraction(self):
        """W3 should map to subtraction."""
        assert get_operation_for_world(MathWorld.W3) == Operation.SUBTRACTION.value
