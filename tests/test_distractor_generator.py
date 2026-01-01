# tests/test_distractor_generator.py
"""Tests for the Distractor Generator - comprehensive 1000-iteration suite."""
import pytest
import random
from typing import List, Set

import sys
sys.path.insert(0, '.')

from core.problems.distractor_generator import (
    AdditionDistractorGenerator, 
    generate_addition_distractors
)


@pytest.fixture
def generator():
    """Create a fresh generator instance for each test."""
    return AdditionDistractorGenerator()


def test_basic_requirements():
    """Test that basic requirements are met for various targets."""
    test_cases = [
        (5, "Sum=5 (special case)"),
        (3, "Small sum (<10)"),
        (8, "Medium sum (<10)"),
        (12, "Two-digit sum"),
        (25, "Larger sum"),
        (100, "Three-digit sum"),
    ]
    
    for target, description in test_cases:
        result = generate_addition_distractors(target)
        
        assert len(result) == 3, f"{description}: Expected 3 numbers, got {len(result)}"
        assert len(set(result)) == 3, f"{description}: Numbers not unique: {result}"
        assert target in result, f"{description}: Target {target} not in result {result}"


def test_educational_distractors(generator):
    """Test that distractors are educationally challenging (close to target)."""
    test_targets = [7, 15, 22, 48]
    
    for target in test_targets:
        result = generator.generate_distractors(target)
        distractors = [n for n in result if n != target]
        
        # At least one distractor should be close (±1 or ±2)
        close_distractors = [d for d in distractors if abs(d - target) <= 2]
        assert len(close_distractors) >= 1, \
            f"No close distractors for target {target}. Got: {distractors}"
        
        assert distractors[0] != distractors[1], \
            f"Distractors are identical: {distractors}"


def test_constraint_sums_under_10():
    """Test that distractors are never negative for sums under 10."""
    for target in range(1, 10):
        result = generate_addition_distractors(target)
        
        for num in result:
            assert num >= 0, f"Negative distractor {num} for target {target} in {result}"


def test_special_case_sum_5():
    """Test special constraint for sum=5 (avoid 50)."""
    for _ in range(100):
        result = generate_addition_distractors(5)
        assert 50 not in result, f"Found 50 in result: {result}"
        assert 5 in result, f"Target 5 missing in result: {result}"


def test_variety_in_distractors(generator):
    """Ensure distractors have variety across multiple generations."""
    target = 8
    distractor_pairs = set()
    
    for _ in range(50):
        result = generator.generate_distractors(target)
        distractors = tuple(sorted([n for n in result if n != target]))
        distractor_pairs.add(distractors)
    
    assert len(distractor_pairs) > 5, \
        f"Insufficient variety: only {len(distractor_pairs)} unique pairs"


def test_deterministic_with_seed():
    """Test that generator produces same results with same seed."""
    seed = 42
    target = 12
    
    gen1 = AdditionDistractorGenerator(seed=seed)
    result1 = gen1.generate_distractors(target)
    
    gen2 = AdditionDistractorGenerator(seed=seed)
    result2 = gen2.generate_distractors(target)
    
    assert result1 == result2, "Results differ with same seed"


def test_1000_iterations_no_violations():
    """Run 1000 iterations to check for constraint violations."""
    violations = []
    generator = AdditionDistractorGenerator()
    
    targets = list(range(1, 101)) * 10
    random.shuffle(targets)
    
    for i, target in enumerate(targets[:1000]):
        try:
            result = generator.generate_distractors(target)
            
            assert len(result) == 3, f"Iteration {i}: Expected 3 numbers"
            assert len(set(result)) == 3, f"Iteration {i}: Duplicate numbers"
            assert target in result, f"Iteration {i}: Target {target} not in {result}"
            
            if target < 10:
                for num in result:
                    if num < 0:
                        violations.append(f"Iteration {i}: Negative for target {target}")
            
            if target == 5 and 50 in result:
                violations.append(f"Iteration {i}: Found 50 for target 5")
            
        except AssertionError as e:
            violations.append(str(e))
        except Exception as e:
            violations.append(f"Iteration {i}: Unexpected error: {str(e)}")
    
    assert len(violations) == 0, f"Found {len(violations)} constraint violations"


def test_error_handling():
    """Test error handling for invalid inputs."""
    generator = AdditionDistractorGenerator()
    
    with pytest.raises(ValueError):
        generator.generate_distractors("not a number")
    
    with pytest.raises(ValueError):
        generator.generate_distractors(3.14)
    
    with pytest.raises(ValueError):
        generator.generate_distractors(None)
