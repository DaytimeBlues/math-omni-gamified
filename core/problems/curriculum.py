"""
Curriculum definitions for Math Omni.
Maps specific levels to curated problem specs.
"""

# World 2: Addition (Curated Levels 1-10)
WORLD_2_CURRICULUM = {
    1: {"a": 1, "b": 1, "target": 2, "item": "apples", "audio": ["level_start", "numbers_01", "op_plus", "numbers_01", "op_equals", "q_altogether"]},
    2: {"a": 1, "b": 1, "target": 2, "item": "cats", "audio": ["level_start", "numbers_01", "op_plus", "numbers_01", "op_equals", "q_altogether"]}, # Different colors in visual in future
    3: {"a": 2, "b": 3, "target": 5, "item": "stars", "audio": ["numbers_02", "op_plus", "numbers_03", "op_equals", "q_altogether"]},
    4: {"a": 0, "b": 5, "target": 5, "item": "apples", "audio": ["numbers_00", "op_plus", "numbers_05", "op_equals", "q_altogether"]},
    5: {"a": 2, "b": 2, "target": 4, "item": "cars", "audio": ["numbers_02", "op_plus", "numbers_02", "op_equals", "q_altogether"]},
    6: {"a": 3, "b": 4, "target": 7, "item": "flowers", "audio": ["numbers_03", "op_plus", "numbers_04", "op_equals", "q_altogether"]},
    7: {"a": 5, "b": 3, "target": 8, "item": "ducks", "audio": ["numbers_05", "op_plus", "numbers_03", "op_equals", "q_altogether"]},
    8: {"a": 5, "b": 5, "target": 10, "item": "hands", "audio": ["numbers_05", "op_plus", "numbers_05", "op_equals", "q_altogether"]},
    9: {"a": 2, "b": 3, "target": 5, "item": "mixed", "audio": ["numbers_02", "op_plus", "numbers_03", "op_equals", "q_altogether"]},
    10: {"a": 4, "b": 6, "target": 10, "item": "stars", "audio": ["numbers_04", "op_plus", "numbers_06", "op_equals", "q_altogether"]},
}

# World 3: Subtraction (Curated Levels 21-30)
# ChatGPT Review Applied:
# - First zero at L23 (small: 2-2=0) after 2 successful non-zeros
# - Second zero at L27 (4-4=0) interleaved, not clustered
# - End on challenge (L30: 10-5=5) not a zero
# - Smaller subtrahends early, building to "within 10" by end
WORLD_3_CURRICULUM = {
    21: {"a": 3, "b": 1, "target": 2, "item": "apples", "audio": ["numbers_03", "w3_takeaway_v01", "numbers_01", "op_equals", "q_left"]},
    22: {"a": 4, "b": 1, "target": 3, "item": "stars", "audio": ["numbers_04", "w3_takeaway_v02", "numbers_01", "op_equals", "q_left"]},
    23: {"a": 2, "b": 2, "target": 0, "item": "cats", "audio": ["numbers_02", "w3_takeaway_v03", "numbers_02", "w3_zero_v01", "q_left"]},  # First zero (small)
    24: {"a": 5, "b": 2, "target": 3, "item": "ducks", "audio": ["numbers_05", "w3_takeaway_v04", "numbers_02", "op_equals", "q_left"]},
    25: {"a": 5, "b": 3, "target": 2, "item": "fish", "audio": ["numbers_05", "w3_takeaway_v05", "numbers_03", "op_equals", "q_left"]},
    26: {"a": 6, "b": 2, "target": 4, "item": "cars", "audio": ["numbers_06", "w3_takeaway_v06", "numbers_02", "op_equals", "q_left"]},
    27: {"a": 4, "b": 4, "target": 0, "item": "hearts", "audio": ["numbers_04", "w3_takeaway_v07", "numbers_04", "w3_zero_v02", "q_left"]},  # Second zero (interleaved)
    28: {"a": 7, "b": 3, "target": 4, "item": "flowers", "audio": ["numbers_07", "w3_takeaway_v08", "numbers_03", "op_equals", "q_left"]},
    29: {"a": 8, "b": 4, "target": 4, "item": "apples", "audio": ["numbers_08", "w3_takeaway_v09", "numbers_04", "op_equals", "q_left"]},
    30: {"a": 10, "b": 5, "target": 5, "item": "stars", "audio": ["numbers_10", "w3_takeaway_v10", "numbers_05", "op_equals", "q_left"]},  # End on challenge, not zero
}
