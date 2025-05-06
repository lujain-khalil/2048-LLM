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
    Composite 2048 heuristic.
    """
    empty_term = empty_score(grid, 50)
    snake_term = snake_weight_score(grid, 1)
    mono_term = monotonicity_score(grid, 1.5) 
    smooth_term = smoothness_score(grid, 0.3) 

    return empty_term + snake_term + mono_term + smooth_term


# def empty_score(grid, weight=100):
#     """Weight x number of zeros; weight shrinks as tiles grow."""
#     empty = sum(1 for row in grid for cell in row if cell == 0)
#     return weight * empty

def empty_score(grid, weight=50):
    """
    Rewards empty cells, with a weight that decays as the game progresses (more non-empty cells).
    This encourages keeping space for future moves, especially early in the game.
    """
    empty_cells = sum(1 for row in grid for cell in row if cell == 0)
    non_empty_cells = 16 - empty_cells
    decay_factor = 0.9 ** non_empty_cells # Exponential decay
    return weight * empty_cells * decay_factor


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

def monotonicity_score(grid, weight=1.5):
    """
    Compute the monotonicity score of a 4x4 grid.
    The score is the maximum number of non-increasing adjacent pairs (horizontally or vertically)
    over all four rotations of the board.
    """
    best = -1

    # Repeat for each of the 4 orientations
    for _ in range(4):
        current = 0

        # Horizontal checks: each row, compare col and col+1
        for row in range(4):
            for col in range(3):
                if grid[row][col] >= grid[row][col + 1]:
                    current += 1

        # Vertical checks: each column, compare row and row+1
        for col in range(4):
            for row in range(3):
                if grid[row][col] >= grid[row + 1][col]:
                    current += 1

        # Keep the maximum over all rotations
        best = max(best, current)

        # Rotate the board 90° clockwise for the next iteration
        n = len(grid)
        grid = [[grid[n-1-j][i] for j in range(n)] for i in range(n)]

    return best * weight

def smoothness_score(grid, weight=0.3):
    """Penalizes adjacent tiles with large differences"""
    penalty = 0
    for i in range(4):
        for j in range(4):
            if grid[i][j] != 0:
                val = grid[i][j]
                # Check right neighbor
                if j < 3 and grid[i][j+1] != 0:
                    penalty += abs(val - grid[i][j+1])
                # Check bottom neighbor
                if i < 3 and grid[i+1][j] != 0:
                    penalty += abs(val - grid[i+1][j])
    return -weight * penalty

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