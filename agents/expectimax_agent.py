from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic, get_empty_cells, is_terminal
import random
import math

@register_agent('expectimax')
class ExpectimaxAgent(Agent):
    """Agent using the Expectimax algorithm to handle randomness."""
    def __init__(self, game, depth=3):
        super().__init__(game)
        self.search_depth = depth

    def get_move(self):
        best_move = None
        best_value = -float('inf')
        possible_moves = ["UP", "DOWN", "LEFT", "RIGHT"]

        current_grid = self.game.grid
        current_score = self.game.score

        for move in possible_moves:
            sim_grid, score_increase, changed = simulate_move_on_grid(current_grid, move)
            if not changed:
                continue

            value = self._chance_node(sim_grid, current_score + score_increase, self.search_depth)

            if value > best_value:
                best_value = value
                best_move = move

        # Fallback
        if best_move is None:
            for move in possible_moves:
                 _, _, changed = simulate_move_on_grid(current_grid, move)
                 if changed:
                     best_move = move
                     break
            if best_move is None:
                 best_move = "UP"
        
        return best_move

    def _max_node(self, grid, score, depth):
        """ Represents the player's turn (maximizing node). """
        if depth == 0 or is_terminal(grid):
            return calculate_heuristic(grid, score)

        max_value = -float('inf')
        possible_moves = ["UP", "DOWN", "LEFT", "RIGHT"]

        for move in possible_moves:
            sim_grid, score_increase, changed = simulate_move_on_grid(grid, move)
            if changed:
                # After the player moves, it's the environment's turn (CHANCE node)
                max_value = max(max_value, self._chance_node(sim_grid, score + score_increase, depth - 1))
            else:
                # If a move is invalid, consider its value based on the current state's heuristic?
                # Or treat it as very bad? For simplicity, we can ignore invalid moves if at least one valid move exists.
                # If NO valid move exists from this state, the _is_terminal check should handle it.
                pass
        
        # If no move changed the board (should be caught by _is_terminal)
        if max_value == -float('inf'):
            return calculate_heuristic(grid, score)
            
        return max_value

    def _chance_node(self, grid, score, depth):
        """ Represents the environment's turn (random tile spawn). """
        if depth == 0 or is_terminal(grid): # Terminal check might be redundant if called after valid move
            return calculate_heuristic(grid, score)

        empty_cells = get_empty_cells(grid)
        if not empty_cells:
             # If no empty cells after a move, shouldn't happen in standard 2048 unless game over
             return calculate_heuristic(grid, score) 

        expected_value = 0
        num_empty = len(empty_cells)

        # Consider placing a 2 (90% probability)
        prob_2 = 0.9 / num_empty
        for r, c in empty_cells:
            grid_with_2 = [row[:] for row in grid]
            grid_with_2[r][c] = 2
            # Next node is the player's turn (MAX node)
            expected_value += prob_2 * self._max_node(grid_with_2, score, depth) # Depth doesn't decrease here, MAX node will decrease it

        # Consider placing a 4 (10% probability)
        prob_4 = 0.1 / num_empty
        for r, c in empty_cells:
            grid_with_4 = [row[:] for row in grid]
            grid_with_4[r][c] = 4
            # Next node is the player's turn (MAX node)
            expected_value += prob_4 * self._max_node(grid_with_4, score, depth)

        return expected_value

    # Removed local _is_terminal, using imported version 