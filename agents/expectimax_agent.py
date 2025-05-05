from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic, get_empty_cells, is_terminal

@register_agent('expectimax')
class ExpectimaxAgent(Agent):
    """Agent using the Expectimax algorithm to handle randomness."""
    def __init__(self, game, depth=4):
        super().__init__(game)
        self.search_depth = depth

    def get_move(self):
        valid_moves = self.get_valid_moves()
        
        # If there are no valid moves, the game should be over
        if not valid_moves:
            raise ValueError("No valid moves available - game should be over")
            
        best_move = None
        best_value = -float('inf')

        current_grid = self.game.grid
        current_score = self.game.score

        for move in valid_moves:
            sim_grid, score_increase, _ = simulate_move_on_grid(current_grid, move)
            value = self._chance_node(sim_grid, current_score + score_increase, self.search_depth)

            if value > best_value:
                best_value = value
                best_move = move

        # Fallback if no move is found (shouldn't happen since we checked for valid moves)
        if best_move is None and valid_moves:
            best_move = valid_moves[0]
        
        return best_move

    def _max_node(self, grid, score, depth):
        """ Represents the player's turn (maximizing node). """
        if depth == 0 or is_terminal(grid):
            return calculate_heuristic(grid, score)

        max_value = -float('inf')
        
        # Get valid moves for this grid state
        valid_moves = []
        for move in ["UP", "DOWN", "LEFT", "RIGHT"]:
            _, _, changed = simulate_move_on_grid(grid, move)
            if changed:
                valid_moves.append(move)
        
        # If no valid moves, this is a terminal state
        if not valid_moves:
            return calculate_heuristic(grid, score)

        for move in valid_moves:
            sim_grid, score_increase, _ = simulate_move_on_grid(grid, move)
            # After the player moves, it's the environment's turn (CHANCE node)
            max_value = max(max_value, self._chance_node(sim_grid, score + score_increase, depth - 1))
            
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