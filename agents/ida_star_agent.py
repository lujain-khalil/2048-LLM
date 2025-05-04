from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic
import copy
import math

@register_agent('ida_star')
class IDAStarAgent(Agent):
    """Agent that uses Iterative Deepening A* search."""
    def __init__(self, game, initial_depth_limit=None, max_overall_depth=None):
        super().__init__(game)
        # Note: IDA* doesn't strictly use depth limit like A*, but cost limit.
        # We simulate depth limits for simplicity, but a true IDA* uses f-cost limit.
        self.initial_depth_limit = initial_depth_limit if initial_depth_limit is not None else 1
        self.max_overall_depth = max_overall_depth if max_overall_depth is not None else 5  # Safety limit

    def get_move(self):
        initial_grid = self.game.grid
        initial_score = self.game.score
        possible_moves = ["UP", "DOWN", "LEFT", "RIGHT"]

        best_move = None
        best_overall_heuristic = -float('inf')

        # We essentially run DFS with increasing depth limits
        # for each potential first move.
        for first_move in possible_moves:
            sim_grid, sim_score_increase, changed = simulate_move_on_grid(initial_grid, first_move)
            if not changed:
                continue

            start_state_heuristic = calculate_heuristic(sim_grid, initial_score + sim_score_increase)
            
            # Start DFS from depth 1 up to max depth for this initial move
            best_heuristic_for_move = -float('inf')
            for depth_limit in range(self.initial_depth_limit, self.max_overall_depth + 1):
                # path = [(grid, score)] # Keep track of visited states in current path for cycle detection
                path = [(tuple(map(tuple, sim_grid)), initial_score + sim_score_increase)]
                result_heuristic = self._depth_limited_search(sim_grid, initial_score + sim_score_increase, 1, depth_limit, path)
                
                best_heuristic_for_move = max(best_heuristic_for_move, result_heuristic)
                # In a true IDA*, we'd update a cost bound here based on pruned nodes.
                # Here, we just rely on the increasing depth limit.

            if best_heuristic_for_move > best_overall_heuristic:
                best_overall_heuristic = best_heuristic_for_move
                best_move = first_move

        # Fallback
        if best_move is None:
            for move in possible_moves:
                 _, _, changed = simulate_move_on_grid(initial_grid, move)
                 if changed:
                     best_move = move
                     break
            if best_move is None:
                 best_move = "UP"

        return best_move

    def _depth_limited_search(self, current_grid, current_score, depth, depth_limit, path):
        """ Recursive DFS function for IDA*. Returns best heuristic found. """
        
        current_heuristic = calculate_heuristic(current_grid, current_score)

        if depth >= depth_limit:
            return current_heuristic # Return heuristic at depth limit

        max_heuristic_found = current_heuristic # Start with current node's heuristic
        
        for move in ["UP", "DOWN", "LEFT", "RIGHT"]:
            next_grid, score_increase, changed = simulate_move_on_grid(current_grid, move)
            if not changed:
                continue
            
            next_grid_tuple = tuple(map(tuple, next_grid))
            next_score = current_score + score_increase
            
            # Simple cycle detection: check if state is already in the current path
            if any(state[0] == next_grid_tuple for state in path):
                 continue

            # Pruning step (like A*): f = g + h. Here g = depth.
            # If g + h > bound (where bound implicitly increases with depth_limit), prune.
            # This is simplified here; a real IDA* uses explicit f-cost bound.
            # h = Game.calculate_heuristic(next_grid, next_score)
            # f = depth + 1 + h # Estimate future cost
            # if f > some_bound: continue # Skip if estimated cost exceeds bound
            
            path.append((next_grid_tuple, next_score))
            result_heuristic = self._depth_limited_search(next_grid, next_score, depth + 1, depth_limit, path)
            path.pop() # Backtrack
            
            max_heuristic_found = max(max_heuristic_found, result_heuristic)
            
        return max_heuristic_found 