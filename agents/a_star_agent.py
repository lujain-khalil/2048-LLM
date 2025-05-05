import heapq
import random
import math
from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic

@register_agent('a_star')
class AStarAgent(Agent):
    """A true best‐first (A*) agent with bounded depth."""
    def __init__(self, game, depth_limit=4):
        super().__init__(game)
        self.moves = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.depth_limit = depth_limit

    def get_move(self):
        valid = self.get_valid_moves()
        if not valid:
            raise ValueError("No valid moves available")

        # A priority queue of (–f, g, grid, depth, first_move)
        # we negate f because heapq is a min‐heap but we want max‐f first
        open_heap = []
        closed = {}  # grid‐tuple → best g seen

        # Seed the heap with each one‐ply successor
        base_g = max(max(row) for row in self.game.grid)
        for m in valid:
            g_delta, changed, grid0 = self._simulate_and_cost(self.game.grid, m, base_g)
            if not changed:
                continue
            g0 = g_delta
            h0 = calculate_heuristic(grid0)
            f0 = g0 + h0
            tup0 = tuple(map(tuple, grid0))
            closed[tup0] = g0
            # store depth=1 and remember the initial move
            heapq.heappush(open_heap, (-f0, g0, grid0, 1, m))

        best_f = float('-inf')
        best_moves = []

        # Expand until frontier empty or we've drained our budget
        while open_heap:
            neg_f, g_total, grid, depth, first_move = heapq.heappop(open_heap)
            f = -neg_f

            # record if this leaf is the best we've seen
            if f > best_f:
                best_f, best_moves = f, [first_move]
            elif f == best_f:
                best_moves.append(first_move)

            # don't expand past depth limit
            if depth >= self.depth_limit:
                continue

            # otherwise expand children
            parent_g = max(max(row) for row in grid)
            for m in self.moves:
                g_delta, changed, grid1 = self._simulate_and_cost(grid, m, parent_g)
                if not changed:
                    continue
                
                g1 = g_total + g_delta
                tup1 = tuple(map(tuple, grid1))

                if tup1 in closed and closed[tup1] >= g1:
                    continue

                closed[tup1] = g1
                h1 = calculate_heuristic(grid1)
                f1 = g1 + h1
                heapq.heappush(open_heap, (-f1, g1, grid1, depth + 1, first_move))

        # pick randomly among the top-scoring first moves
        if best_moves:
            return random.choice(best_moves)
        else:
            return random.choice(valid)

    def _simulate_and_cost(self, grid, move, prev_g):
        """Helper: simulate move, return (g_delta, changed, new_grid).
        """
        new_grid, _, changed = simulate_move_on_grid(grid, move)
        if not changed:
            return 0, False, grid
        
        new_g = max(max(row) for row in new_grid)
        g_delta = (new_g - prev_g) * 10
        
        return g_delta, True, new_grid
