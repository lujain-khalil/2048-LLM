import math
import random
import copy 
# --- Static Game Logic Helpers ---

def merge_row_left_static(row):
    """Static helper to merge a row left. Returns new row and score increase."""
    filtered = [num for num in row if num != 0]
    merged_row = []
    score_increase = 0
    skip = False
    for i in range(len(filtered)):
        if skip:
            skip = False
            continue
        if i + 1 < len(filtered) and filtered[i] == filtered[i+1]:
            merged_value = filtered[i] * 2
            merged_row.append(merged_value)
            score_increase += merged_value
            skip = True
        else:
            merged_row.append(filtered[i])
    merged_row.extend([0] * (4 - len(merged_row)))
    return merged_row, score_increase

def simulate_move_on_grid(grid, direction):
    """
    Static helper to simulate a move on a given grid state without modifying it.
    Returns the new grid, the score difference, and whether the grid changed.
    """
    original_grid = [r[:] for r in grid] # Deep copy the provided grid
    new_grid = [r[:] for r in grid] # Copy to modify
    move_score = 0
    changed = False

    if direction == "LEFT":
        temp_grid = []
        for i in range(4):
            new_row, score = merge_row_left_static(new_grid[i])
            temp_grid.append(new_row)
            move_score += score
        new_grid = temp_grid
    elif direction == "RIGHT":
        temp_grid = []
        for i in range(4):
            reversed_row = list(reversed(new_grid[i]))
            merged_reversed, score = merge_row_left_static(reversed_row)
            temp_grid.append(list(reversed(merged_reversed)))
            move_score += score
        new_grid = temp_grid
    elif direction == "UP":
        transposed = [list(x) for x in zip(*new_grid)]
        new_transposed = []
        for i in range(4):
            new_row, score = merge_row_left_static(transposed[i])
            new_transposed.append(new_row)
            move_score += score
        new_grid = [list(x) for x in zip(*new_transposed)]
    elif direction == "DOWN":
        transposed = [list(x) for x in zip(*new_grid)]
        new_transposed = []
        for i in range(4):
            reversed_row = list(reversed(transposed[i]))
            merged_reversed, score = merge_row_left_static(reversed_row)
            new_transposed.append(list(reversed(merged_reversed)))
            move_score += score
        new_grid = [list(x) for x in zip(*new_transposed)]
    else:
        # Invalid direction, return original state
        return original_grid, 0, False

    changed = new_grid != original_grid
    return new_grid, move_score, changed

import math

def calculate_heuristic(grid, score=None):
    """
    Composite 2048 heuristic:
      • empty‐cell bonus (decaying)
      • snake‐pattern gradient
    """
    empty_term = empty_score(grid, 100)
    snake_term = snake_weight_score(grid)

    return empty_term + snake_term


def empty_score(grid, weight=1):
    """Weight x number of zeros; weight shrinks as tiles grow."""
    empty = sum(1 for row in grid for cell in row if cell == 0)
    return weight * empty


def snake_weight_score(grid, weight=1):
    """
    Apply snake-shaped positional weights.
    """
    W = [
        [2**15, 2**14, 2**13, 2**12],
        [2**8,  2**9,  2**10, 2**11],
        [2**7,  2**6,   2**5,  2**4],
        [2**0,  2**1,   2**2,  2**3]
    ]
    score = 0
    for i in range(4):
        for j in range(4):
            score += grid[i][j] * W[i][j]
    return score * weight


def get_empty_cells(grid):
    """ Returns a list of (row, col) tuples for empty cells. """
    return [(r, c) for r in range(4) for c in range(4) if grid[r][c] == 0]

def is_terminal(grid):
    """ Static check if a grid state is terminal (no valid moves). """
    if any(0 in row for row in grid):
        return False
    for r in range(4):
        for c in range(4):
            if c + 1 < 4 and grid[r][c] == grid[r][c+1]: return False
            if r + 1 < 4 and grid[r][c] == grid[r+1][c]: return False
    return True 