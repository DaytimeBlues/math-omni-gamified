"""
Distractor Generator - Educationally Sound Wrong Answer Generation

Generates distractors (wrong answers) that are:
1. Close to the target (challenging)
2. Never negative for sums under 10
3. Never include 50 when target is 5
4. Unique and varied

Gemini Audit Fixes:
- Added SubtractionDistractorGenerator for subtraction-specific edge cases
- Handles zero-result (N-N=0) and identity (N-0=N) cases
- Includes operational confusion distractors (addition instead of subtraction)
"""

import random
from typing import List, Optional


class AdditionDistractorGenerator:
    """
    Generates pedagogically appropriate distractors for addition problems.
    
    Distractors are "close" to the target to be educationally challenging,
    but avoid common constraint violations (negatives, special cases).
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the generator.
        
        Args:
            seed: Optional random seed for reproducibility
        """
        self._rng = random.Random(seed) if seed is not None else random.Random()
    
    def generate_distractors(self, target: int) -> List[int]:
        """
        Generate 3 numbers: the target + 2 distractors.
        
        Args:
            target: The correct answer
            
        Returns:
            List of 3 unique integers including the target
            
        Raises:
            ValueError: If target is not an integer
        """
        # Input validation
        if not isinstance(target, int):
            raise ValueError(f"Target must be an integer, got {type(target).__name__}")
        
        # Special constraints
        min_val = 0 if target < 10 else max(0, target - 20)
        avoid = {50} if target == 5 else set()
        
        # Generate distractors
        distractors = self._generate_close_distractors(target, min_val, avoid)
        
        # Combine with target and shuffle
        result = [target] + distractors
        self._rng.shuffle(result)
        
        return result
    
    def _generate_close_distractors(
        self, 
        target: int, 
        min_val: int, 
        avoid: set
    ) -> List[int]:
        """Generate 2 close distractors."""
        distractors = []
        
        # Preferred offsets: close to target for educational value
        preferred_offsets = [-1, 1, -2, 2]
        fallback_offsets = [-3, 3, -4, 4, -5, 5]
        
        # Try preferred offsets first
        self._rng.shuffle(preferred_offsets)
        for offset in preferred_offsets:
            candidate = target + offset
            if self._is_valid_distractor(candidate, target, distractors, min_val, avoid):
                distractors.append(candidate)
                if len(distractors) >= 2:
                    break
        
        # Use fallback if needed
        if len(distractors) < 2:
            self._rng.shuffle(fallback_offsets)
            for offset in fallback_offsets:
                candidate = target + offset
                if self._is_valid_distractor(candidate, target, distractors, min_val, avoid):
                    distractors.append(candidate)
                    if len(distractors) >= 2:
                        break
        
        # Last resort: random generation
        attempts = 0
        while len(distractors) < 2 and attempts < 50:
            candidate = self._rng.randint(min_val, max(target + 10, 20))
            if self._is_valid_distractor(candidate, target, distractors, min_val, avoid):
                distractors.append(candidate)
            attempts += 1
        
        return distractors[:2]
    
    def _is_valid_distractor(
        self, 
        candidate: int, 
        target: int, 
        existing: List[int],
        min_val: int,
        avoid: set
    ) -> bool:
        """Check if a candidate distractor is valid."""
        # Must not be target
        if candidate == target:
            return False
        
        # Must not already exist
        if candidate in existing:
            return False
        
        # Must not be in avoid set
        if candidate in avoid:
            return False
        
        # Must be >= min_val
        if candidate < min_val:
            return False
        
        return True


class SubtractionDistractorGenerator:
    """
    Generates pedagogically appropriate distractors for subtraction problems.
    
    Gemini Audit Implementation:
    - Handles zero-result (N-N=0): Avoids -1, uses operands as distractors
    - Handles identity (N-0=N): Includes 0 as plausible confusion
    - Includes operational confusion (a+b instead of a-b)
    """
    
    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed) if seed is not None else random.Random()
    
    def generate_distractors(
        self, 
        target: int, 
        group_a: int, 
        group_b: int,
        history_errors: Optional[List[int]] = None
    ) -> List[int]:
        """
        Generate distractors for subtraction: group_a - group_b = target.
        
        Args:
            target: The correct answer (a - b)
            group_a: The minuend (starting amount)
            group_b: The subtrahend (amount removed)
            history_errors: Optional list of past wrong answers from StudentProfile
            
        Returns:
            List of 3 unique integers including the target
        """
        distractors = set()
        
        # 1. Personalized Injection from history
        if history_errors:
            for err in history_errors:
                if err != target and err >= 0:
                    distractors.add(err)
                    if len(distractors) >= 2:
                        break
        
        # 2. Operational Confusion: a + b instead of a - b
        # Critical for "5 - 5 = 0" case -> Generates 10
        op_confusion = group_a + group_b
        if op_confusion != target and op_confusion >= 0:
            distractors.add(op_confusion)
        
        # 3. Component Confusion: answering with operands
        # For "5 - 0 = 5" -> includes 0 as distractor
        if group_b != target and group_b >= 0:
            distractors.add(group_b)
        if group_a != target and group_a >= 0:
            distractors.add(group_a)
        
        # 4. "Always One" Error: belief that subtraction leaves something
        if target == 0 and 1 not in distractors:
            distractors.add(1)
        
        # 5. Neighbors (Target +/- 1) with NON-NEGATIVE constraint
        # Critical for "5 - 5 = 0" case -> Prevents -1
        neighbor_candidates = [target + 1, target + 2]
        if target > 0:
            neighbor_candidates.append(target - 1)
        if target > 1:
            neighbor_candidates.append(target - 2)
        
        for c in neighbor_candidates:
            if c >= 0 and c != target and c not in distractors:
                distractors.add(c)
        
        # 6. Fill to required count with random valid values
        attempts = 0
        max_val = max(group_a + group_b, 10)
        while len(distractors) < 2 and attempts < 50:
            candidate = self._rng.randint(0, max_val)
            if candidate != target and candidate not in distractors:
                distractors.add(candidate)
            attempts += 1
        
        # Convert to list, limit to 2, combine with target, shuffle
        distractor_list = list(distractors)[:2]
        result = [target] + distractor_list
        self._rng.shuffle(result)
        
        return result


def generate_addition_distractors(target: int) -> List[int]:
    """
    Convenience function to generate addition distractors.
    
    Args:
        target: The correct answer
        
    Returns:
        List of 3 unique integers including the target
    """
    generator = AdditionDistractorGenerator()
    return generator.generate_distractors(target)


def generate_subtraction_distractors(
    target: int, 
    group_a: int, 
    group_b: int,
    history_errors: Optional[List[int]] = None
) -> List[int]:
    """
    Convenience function to generate subtraction distractors.
    
    Args:
        target: The correct answer (a - b)
        group_a: The minuend
        group_b: The subtrahend
        history_errors: Optional past wrong answers
        
    Returns:
        List of 3 unique integers including the target
    """
    generator = SubtractionDistractorGenerator()
    return generator.generate_distractors(target, group_a, group_b, history_errors)

