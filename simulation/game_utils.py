import math
import random

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

def calculate_heuristic(grid, score): # Keep score for compatibility if needed, but unused
    """ Calculates a heuristic value for a given grid state. Higher is better. """
    empty_cells = 0
    monotonicity_score = 0
    smoothness_score = 0
    max_tile_val = 0
    max_tile_pos = (0, 0)

    # Precompute log values (log2 of 0 is undefined, use -1 or small value)
    log_grid = [[math.log2(grid[r][c]) if grid[r][c] > 0 else 0 for c in range(4)] for r in range(4)]

    for r in range(4):
        for c in range(4):
            if grid[r][c] == 0:
                empty_cells += 1
            else:
                # Find max tile value and position
                if grid[r][c] > max_tile_val:
                    max_tile_val = grid[r][c]
                    max_tile_pos = (r, c)

                # Smoothness (difference between adjacent tiles)
                current_log_val = log_grid[r][c]
                if c + 1 < 4 and grid[r][c+1] != 0:
                    neighbor_log_val = log_grid[r][c+1]
                    smoothness_score -= abs(current_log_val - neighbor_log_val)
                if r + 1 < 4 and grid[r+1][c] != 0:
                    neighbor_log_val = log_grid[r+1][c]
                    smoothness_score -= abs(current_log_val - neighbor_log_val)

    # Monotonicity: Penalize increases from left->right and top->bottom
    mono_penalty_lr = 0
    mono_penalty_ud = 0
    for r in range(4):
        for c in range(3):
            if log_grid[r][c+1] > log_grid[r][c]:
                mono_penalty_lr += log_grid[r][c+1] - log_grid[r][c]
    for c in range(4):
         for r in range(3):
             if log_grid[r+1][c] > log_grid[r][c]:
                mono_penalty_ud += log_grid[r+1][c] - log_grid[r][c]

    # Max tile bonus
    max_tile_log = math.log2(max_tile_val) if max_tile_val > 0 else 0
    corner_bonus = 0
    if max_tile_pos == (0, 0):
        corner_bonus = max_tile_log * 0.5

    w_empty = 2.7
    w_smooth = 0.2
    w_mono = 1.0
    w_max_tile = 1.0
    w_corner = 2.0

    heuristic = (
        empty_cells * w_empty +
        smoothness_score * w_smooth -
        (mono_penalty_lr + mono_penalty_ud) * w_mono +
        max_tile_log * w_max_tile +
        corner_bonus * w_corner
    )
    return heuristic

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