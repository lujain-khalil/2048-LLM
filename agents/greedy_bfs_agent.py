from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic
import copy

@register_agent('greedy_bfs')
class GreedyBFSAgent(Agent):
    """Agent that chooses the move leading to the best state based on a heuristic (1-ply lookahead)."""

    def get_move(self):
        valid_moves = self.get_valid_moves()
        
        # If there are no valid moves, the game should be over
        if not valid_moves:
            raise ValueError("No valid moves available - game should be over")
            
        best_move = None
        best_heuristic_value = -float('inf')

        current_grid = self.game.grid
        current_score = self.game.score

        for move in valid_moves:
            # Simulate the move using the utility function
            simulated_grid, score_increase, _ = simulate_move_on_grid(current_grid, move)
            
            # Calculate the heuristic value for this move
            heuristic_value = calculate_heuristic(simulated_grid, current_score + score_increase)

            if heuristic_value > best_heuristic_value:
                best_heuristic_value = heuristic_value
                best_move = move

        # If no move improves the heuristic (all moves lead to worse states),
        # just return the first valid move
        if best_move is None and valid_moves:
            best_move = valid_moves[0]

        return best_move 