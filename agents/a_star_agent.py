import random
import copy
from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic, empty_score

@register_agent('a_star')
class AStarAgent(Agent):
    """Agent that evaluates moves based on heuristics including empty tiles and monotonicity."""
    def __init__(self, game, depth_limit=None):
        super().__init__(game)
        self.moves = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.depth_limit = depth_limit if depth_limit is not None else 3

    def get_move(self):
        """Use heuristic evaluation to find the best move."""
        valid_moves = self.get_valid_moves()
        
        # If there are no valid moves, the game should be over
        if not valid_moves:
            raise ValueError("No valid moves available - game should be over")
        
        best_moves = []
        best_f = float('-inf')
        current_grid = self.game.grid

        # Try each valid move
        for move in valid_moves:
            # Simulate the move using the utility function
            sim_grid, score_inc, changed = simulate_move_on_grid(current_grid, move)
            if not changed:
                continue
            
            g_so_far = empty_score(sim_grid) - empty_score(current_grid)
            # For deeper search
            if self.depth_limit > 1:
                # Use path tracking for cycle detection
                path = {(tuple(map(tuple, sim_grid)))}
                f_val = self._depth_limited_search(
                    sim_grid,
                    g_so_far=g_so_far,
                    depth=1,
                    depth_limit=self.depth_limit,
                    path=path
                )
            else:
                # Original single-ply evaluation
                f_val = calculate_heuristic(sim_grid) + g_so_far
            
            if f_val > best_f:
                best_f = f_val
                best_moves = [move]
            elif best_f == f_val:
                best_moves.append(move)

        if best_moves:
            return random.choice(best_moves)
        else:
            random.choice(valid_moves)
            
    def _depth_limited_search(self, grid, g_so_far, depth, depth_limit, path):
        """Recursive depth-limited search for multi-ply lookahead."""
        # Get the heuristic value for the current state
        h_val = calculate_heuristic(grid)
        f_current = g_so_far + h_val

        # If we've reached the depth limit, return the heuristic
        if depth >= depth_limit:
            return f_current
            
        best_f = f_current
        
        # Try each possible move from here
        for move in self.moves:
            next_grid, score_inc, changed = simulate_move_on_grid(grid, move)
            g_so_far += empty_score(next_grid) - empty_score(grid)
            if not changed:
                continue
                
            tup = tuple(map(tuple, next_grid))
            if tup in path:
                continue

            path.add(tup)
            f_child = self._depth_limited_search(
                next_grid,
                g_so_far + score_inc,
                depth + 1,
                depth_limit,
                path
            )
            path.remove(tup)                
            if f_child > best_f:
                best_f = f_child

        return best_f