# tests/test_contracts.py
"""Tests for the shared interface contracts."""
import pytest
from core.contracts import (
    ProblemData,
    WorldID,
    Operation,
    CPAStage,
    VisualType,
    AudioTokens,
    LevelConfig,
    make_level_id,
    parse_level_id,
    get_level_config,
    WORLD_2_LEVELS,
    WORLD_3_LEVELS,
)


class TestWorldID:
    """Tests for WorldID enum."""
    
    def test_world_ids_exist(self):
        """All world IDs should be defined."""
        assert WorldID.W1.value == "W1"
        assert WorldID.W2.value == "W2"
        assert WorldID.W3.value == "W3"


class TestOperation:
    """Tests for Operation enum."""
    
    def test_operations_exist(self):
        """All operations should be defined."""
        assert Operation.COUNTING.value == "counting"
        assert Operation.ADDITION.value == "addition"
        assert Operation.SUBTRACTION.value == "subtraction"


class TestCPAStage:
    """Tests for CPAStage enum."""
    
    def test_cpa_stages_exist(self):
        """All CPA stages should be defined."""
        assert CPAStage.CONCRETE.value == "concrete"
        assert CPAStage.PICTORIAL.value == "pictorial"
        assert CPAStage.ABSTRACT.value == "abstract"


class TestLevelID:
    """Tests for level ID functions."""
    
    def test_make_level_id(self):
        """Should create valid level IDs."""
        assert make_level_id(WorldID.W2, 1) == "W2-L01"
        assert make_level_id(WorldID.W2, 10) == "W2-L10"
        assert make_level_id(WorldID.W3, 5) == "W3-L05"
    
    def test_parse_level_id(self):
        """Should parse level IDs correctly."""
        world, level = parse_level_id("W2-L01")
        assert world == WorldID.W2
        assert level == 1
        
        world, level = parse_level_id("W3-L10")
        assert world == WorldID.W3
        assert level == 10
    
    def test_parse_invalid_level_id(self):
        """Should raise ValueError for invalid IDs."""
        with pytest.raises(ValueError):
            parse_level_id("")
        
        with pytest.raises(ValueError):
            parse_level_id("invalid")
        
        with pytest.raises(ValueError):
            parse_level_id("W2L01")  # Missing dash


class TestAudioTokens:
    """Tests for AudioTokens helper class."""
    
    def test_number_token(self):
        """Should generate correct number tokens."""
        assert AudioTokens.number(0) == "numbers_0"
        assert AudioTokens.number(10) == "numbers_10"
        assert AudioTokens.number(20) == "numbers_20"
    
    def test_number_token_invalid(self):
        """Should raise ValueError for out of range numbers."""
        with pytest.raises(ValueError):
            AudioTokens.number(-1)
        
        with pytest.raises(ValueError):
            AudioTokens.number(21)
    
    def test_operator_tokens(self):
        """Should have correct operator tokens."""
        assert AudioTokens.OP_PLUS == "op_plus"
        assert AudioTokens.OP_TAKE_AWAY == "op_take_away"
        assert AudioTokens.OP_EQUALS == "op_equals"
    
    def test_question_tokens(self):
        """Should have correct question tokens."""
        assert AudioTokens.Q_ALTOGETHER == "q_altogether"
        assert AudioTokens.Q_LEFT == "q_left"
        assert AudioTokens.Q_HOW_MANY == "q_how_many"


class TestProblemData:
    """Tests for ProblemData dataclass."""
    
    def test_addition_prompt_text(self):
        """Addition problems should show correct prompt."""
        problem = ProblemData(
            type="addition",
            operand_a=3,
            operand_b=2,
            target=5,
            options=[4, 5, 6],
        )
        assert problem.prompt_text == "3 + 2 = ?"
    
    def test_subtraction_prompt_text(self):
        """Subtraction problems should show correct prompt."""
        problem = ProblemData(
            type="subtraction",
            operand_a=5,
            operand_b=2,
            target=3,
            options=[2, 3, 4],
        )
        assert problem.prompt_text == "5 - 2 = ?"
    
    def test_counting_prompt_text(self):
        """Counting problems should show correct prompt."""
        problem = ProblemData(
            type="counting",
            operand_a=5,
            operand_b=None,
            target=5,
            options=[4, 5, 6],
            visual_config={"item_name": "apples"},
        )
        assert problem.prompt_text == "How many apples?"
    
    def test_counting_prompt_text_default(self):
        """Counting problems should use default item name."""
        problem = ProblemData(
            type="counting",
            operand_a=5,
            operand_b=None,
            target=5,
            options=[4, 5, 6],
        )
        assert problem.prompt_text == "How many items?"
    
    def test_is_valid_with_valid_problem(self):
        """Valid problems should pass validation."""
        problem = ProblemData(
            type="addition",
            operand_a=3,
            operand_b=2,
            target=5,
            options=[4, 5, 6],
        )
        assert problem.is_valid is True
    
    def test_is_valid_target_not_in_options(self):
        """Should be invalid if target not in options."""
        problem = ProblemData(
            type="addition",
            operand_a=3,
            operand_b=2,
            target=5,
            options=[4, 6, 7],  # 5 is missing!
        )
        assert problem.is_valid is False
    
    def test_is_valid_duplicate_options(self):
        """Should be invalid if options have duplicates."""
        problem = ProblemData(
            type="addition",
            operand_a=3,
            operand_b=2,
            target=5,
            options=[5, 5, 6],  # Duplicate 5
        )
        assert problem.is_valid is False
    
    def test_is_valid_addition_without_operand_b(self):
        """Addition should be invalid without operand_b."""
        problem = ProblemData(
            type="addition",
            operand_a=3,
            operand_b=None,
            target=5,
            options=[4, 5, 6],
        )
        assert problem.is_valid is False
    
    def test_is_valid_negative_options(self):
        """Should be invalid if any option is negative."""
        problem = ProblemData(
            type="subtraction",
            operand_a=5,
            operand_b=2,
            target=3,
            options=[-1, 3, 4],  # -1 is negative
        )
        assert problem.is_valid is False
    
    def test_to_dict_has_required_keys(self):
        """to_dict should include all required keys."""
        problem = ProblemData(
            type="addition",
            operand_a=3,
            operand_b=2,
            target=5,
            options=[4, 5, 6],
            visual_config={"item_name": "apples", "emoji": "🍎"},
            audio_sequence=["numbers_3", "op_plus", "numbers_2"],
        )
        result = problem.to_dict()
        
        required_keys = [
            "type", "level", "target", "options", "prompt",
            "emoji", "item_name", "host", "operand_a", "operand_b",
            "visual_config", "audio_sequence"
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"


class TestLevelConfig:
    """Tests for curriculum level configurations."""
    
    def test_world_2_has_10_levels(self):
        """World 2 should have exactly 10 levels."""
        assert len(WORLD_2_LEVELS) == 10
    
    def test_world_3_has_10_levels(self):
        """World 3 should have exactly 10 levels."""
        assert len(WORLD_3_LEVELS) == 10
    
    def test_world_2_levels_are_addition(self):
        """All World 2 levels should be addition."""
        for level in WORLD_2_LEVELS:
            assert level.operation == Operation.ADDITION
            assert level.world == WorldID.W2
    
    def test_world_3_levels_are_subtraction(self):
        """All World 3 levels should be subtraction."""
        for level in WORLD_3_LEVELS:
            assert level.operation == Operation.SUBTRACTION
            assert level.world == WorldID.W3
    
    def test_get_level_config(self):
        """Should retrieve correct level config."""
        config = get_level_config("W2-L01")
        assert config is not None
        assert config.level_number == 1
        assert config.operation == Operation.ADDITION
        
        config = get_level_config("W3-L05")
        assert config is not None
        assert config.level_number == 5
        assert config.operation == Operation.SUBTRACTION
    
    def test_get_level_config_unknown(self):
        """Should return None for unknown level."""
        assert get_level_config("W99-L01") is None
        assert get_level_config("invalid") is None
