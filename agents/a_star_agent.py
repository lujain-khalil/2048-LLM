from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic
import heapq
import copy
import math

@register_agent('a_star')
class AStarAgent(Agent):
    """Agent that uses A* search to find the best move sequence within a limited depth."""
    def __init__(self, game, depth_limit=3):
        super().__init__(game)
        self.depth_limit = depth_limit # Max number of moves to look ahead

    def get_move(self):
        initial_grid = self.game.grid
        initial_score = self.game.score
        
        valid_moves = self.get_valid_moves()
        
        # If there are no valid moves, the game should be over
        if not valid_moves:
            raise ValueError("No valid moves available - game should be over")

        best_move = None
        best_value = -float('inf')

        # A* search for each initial valid move
        for first_move in valid_moves:
            sim_grid, sim_score_increase, _ = simulate_move_on_grid(initial_grid, first_move)
            
            # Use negative heuristic because heapq is a min-heap
            # Start A* from the state resulting from the first move
            start_node_value = -calculate_heuristic(sim_grid, initial_score + sim_score_increase)
            # state = (grid, current_score, depth, current_move_sequence)
            start_node = (start_node_value, tuple(map(tuple, sim_grid)), initial_score + sim_score_increase, 1, [first_move])
            
            final_value = self._a_star_search(start_node)
            
            # Remember the first move that led to the best outcome found by A*
            if -final_value > best_value: # Compare positive heuristic values
                best_value = -final_value
                best_move = first_move

        # Fallback if no improving move is found (all moves lead to worse states)
        if best_move is None and valid_moves:
            best_move = valid_moves[0]

        return best_move

    def _a_star_search(self, start_node):
        """ Performs A* search starting from a node representing the state after the first move. """
        # Priority queue stores: (f_cost, grid, score, depth, path)
        # f_cost = g + h, where g is -(current_score) or depth, h is -heuristic
        # We'll use g = depth for simplicity here.
        open_set = [start_node] # Use list as min-heap via heapq
        closed_set = set() # Stores tuples of grids to avoid cycles
        
        best_terminal_heuristic = -float('inf')

        while open_set:
            f_cost_neg, current_grid_tuple, current_score, depth, path = heapq.heappop(open_set)
            
            # grid tuple is already frozen from initial node and loop below
            if current_grid_tuple in closed_set:
                continue
            closed_set.add(current_grid_tuple)
            
            # Convert back to list of lists for heuristic calculation
            current_grid_list = [list(row) for row in current_grid_tuple]
            # Use util function
            current_heuristic = calculate_heuristic(current_grid_list, current_score)
            best_terminal_heuristic = max(best_terminal_heuristic, current_heuristic)

            if depth >= self.depth_limit:
                continue # Stop searching deeper

            # Get valid moves for this grid state
            for move in ["UP", "DOWN", "LEFT", "RIGHT"]:
                # Use util function
                next_grid_list, score_increase, changed = simulate_move_on_grid(current_grid_list, move)
                if not changed:
                    continue

                next_grid_tuple = tuple(map(tuple, next_grid_list))
                if next_grid_tuple in closed_set:
                     continue

                next_score = current_score + score_increase
                # Use util function
                h_cost_neg = -calculate_heuristic(next_grid_list, next_score)
                g_cost = depth + 1 # Cost increases with depth
                f_cost_neg = g_cost + h_cost_neg # A* cost function (using negative h)

                heapq.heappush(open_set, (f_cost_neg, next_grid_tuple, next_score, depth + 1, path + [move]))
                
        # The search explores possibilities starting from the first move.
        # Return the best heuristic value found at any terminal node reached from that starting move.
        return -best_terminal_heuristic # Return positive heuristic value 