from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic
import copy

@register_agent('greedy_bfs')
class GreedyBFSAgent(Agent):
    """Agent that chooses the move leading to the best state based on a heuristic (1-ply lookahead)."""

    def get_move(self):
        best_move = None
        best_heuristic_value = -float('inf')
        possible_moves = ["UP", "DOWN", "LEFT", "RIGHT"]

        current_grid = self.game.grid # No need to deep copy here yet
        current_score = self.game.score

        for move in possible_moves:
            # Use the utility function
            simulated_grid, score_increase, changed = simulate_move_on_grid(current_grid, move)

            # Only consider valid moves that change the board state
            if changed:
                # Use the utility function
                heuristic_value = calculate_heuristic(simulated_grid, current_score + score_increase)

                if heuristic_value > best_heuristic_value:
                    best_heuristic_value = heuristic_value
                    best_move = move

        # If no move improves the heuristic (e.g., all moves are invalid or lead to worse states),
        # fallback to a default move (e.g., the first valid one found, or random).
        if best_move is None:
            # Find the first valid move if no improvement was found
            for move in possible_moves:
                 # Use the utility function
                 _, _, changed = simulate_move_on_grid(current_grid, move)
                 if changed:
                     best_move = move
                     break
            # If still no valid move (shouldn't happen unless game is over), default to UP
            if best_move is None:
                 best_move = "UP"

        return best_move 