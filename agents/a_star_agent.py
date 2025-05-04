import random
import copy
from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic

@register_agent('a_star')
class AStarAgent(Agent):
    """Agent that evaluates moves based on heuristics including empty tiles and monotonicity."""
    def __init__(self, game, depth_limit=3):
        super().__init__(game)
        self.moves = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.depth_limit = depth_limit

    def get_move(self):
        """Use heuristic evaluation to find the best move."""
        valid_moves = self.get_valid_moves()
        
        # If there are no valid moves, the game should be over
        if not valid_moves:
            raise ValueError("No valid moves available - game should be over")
        
        best_moves = []
        best_score = float('-inf')
        current_grid = self.game.grid
        current_score = self.game.score

        # Try each valid move
        for move in valid_moves:
            # Simulate the move using the utility function
            sim_grid, score_increase, changed = simulate_move_on_grid(current_grid, move)
            if not changed:
                continue
                
            # For deeper search
            if self.depth_limit > 1:
                # Use path tracking for cycle detection
                path = [(tuple(map(tuple, sim_grid)), current_score + score_increase)]
                score = self._depth_limited_search(sim_grid, current_score + score_increase, 1, self.depth_limit, path)
            else:
                # Original single-ply evaluation
                score = self._evaluate_position(sim_grid)
            
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        # If multiple moves have the same score, choose randomly
        if best_moves:
            return random.choice(best_moves)
        else:
            # This should never happen since we checked for valid moves,
            # but return a valid move as a fallback
            return valid_moves[0]
            
    def _depth_limited_search(self, current_grid, current_score, depth, depth_limit, path):
        """Recursive depth-limited search for multi-ply lookahead."""
        # Get the heuristic value for the current state
        current_heuristic = calculate_heuristic(current_grid, current_score)
        
        # If we've reached the depth limit, return the heuristic
        if depth >= depth_limit:
            return current_heuristic
            
        max_heuristic_found = current_heuristic
        
        # Try each possible move from here
        for move in ["UP", "DOWN", "LEFT", "RIGHT"]:
            next_grid, score_increase, changed = simulate_move_on_grid(current_grid, move)
            if not changed:
                continue
                
            next_grid_tuple = tuple(map(tuple, next_grid))
            next_score = current_score + score_increase
            
            # Cycle detection
            if any(state[0] == next_grid_tuple for state in path):
                continue
                
            # Add to path and recurse
            path.append((next_grid_tuple, next_score))
            result_heuristic = self._depth_limited_search(next_grid, next_score, depth + 1, depth_limit, path)
            path.pop()  # Backtrack
            
            max_heuristic_found = max(max_heuristic_found, result_heuristic)
            
        return max_heuristic_found

    def _evaluate_position(self, grid):
        """
        Evaluate the current position using multiple heuristics:
        1. Number of empty tiles
        2. Monotonicity of rows and columns
        """
        # Count empty tiles (weight: 1.0)
        empty_count = sum(1 for row in grid for cell in row if cell == 0)
        empty_score = empty_count

        # Calculate monotonicity score (weight: 2.0)
        monotonicity_score = self._calculate_monotonicity(grid) * 2.0

        return empty_score + monotonicity_score

    def _calculate_monotonicity(self, grid):
        """
        Calculate how monotonic the grid is (either increasing or decreasing)
        both horizontally and vertically.
        """
        total_score = 0
        
        # Check rows
        for row in grid:
            # Check left-to-right monotonicity
            lr_mon = all(row[i] <= row[i+1] for i in range(len(row)-1) if row[i+1] != 0)
            # Check right-to-left monotonicity
            rl_mon = all(row[i] >= row[i+1] for i in range(len(row)-1) if row[i] != 0)
            total_score += 1 if lr_mon or rl_mon else 0

        # Check columns
        for j in range(4):
            column = [grid[i][j] for i in range(4)]
            # Check top-to-bottom monotonicity
            tb_mon = all(column[i] <= column[i+1] for i in range(len(column)-1) if column[i+1] != 0)
            # Check bottom-to-top monotonicity
            bt_mon = all(column[i] >= column[i+1] for i in range(len(column)-1) if column[i] != 0)
            total_score += 1 if tb_mon or bt_mon else 0

        # Additional bonus for highest value in corner
        corners = [grid[0][0], grid[0][3], grid[3][0], grid[3][3]]
        max_val = max(max(row) for row in grid)
        if max_val in corners:
            total_score += 2

        return total_score 