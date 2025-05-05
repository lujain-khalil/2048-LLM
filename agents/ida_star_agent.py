import random
from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic

@register_agent('ida_star')
class IDAStartAgent(Agent):
    """An iterative deepening A* (IDA*) agent with bounded depth."""
    def __init__(self, game, depth_limit=4):
        super().__init__(game)
        self.moves = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.depth_limit = depth_limit

    def get_move(self):
        valid = self.get_valid_moves()
        if not valid:
            raise ValueError("No valid moves available")

        base_grid = self.game.grid
        base_g = max(max(row) for row in base_grid)
        # initial A* bound = g(root) + h(root)
        threshold = base_g + calculate_heuristic(base_grid)

        while True:
            # for this iteration
            self.next_threshold = float('inf')
            self.best_f = float('-inf')
            self.best_moves = []

            # try each one-ply successor
            for m in valid:
                g_delta, changed, grid0 = self._simulate_and_cost(base_grid, m, base_g)
                if not changed:
                    continue
                self._search(grid0, g_delta, depth=1, first_move=m, threshold=threshold)

            # if any leaf under this threshold produced a best_f, pick among them
            if self.best_moves:
                return random.choice(self.best_moves)

            # otherwise increase threshold to the smallest f that exceeded it
            if self.next_threshold == float('inf'):
                # no more nodes to try – fallback
                return random.choice(valid)
            threshold = self.next_threshold

    def _search(self, grid, g_total, depth, first_move, threshold):
        """Recursive DFS with f-cost pruning and tracking of best leafs."""
        h = calculate_heuristic(grid)
        f = g_total + h

        # f-cost exceeds our current bound → remember for next iteration
        if f > threshold:
            if f < self.next_threshold:
                self.next_threshold = f
            return

        # at depth limit: record as a candidate
        if depth >= self.depth_limit:
            if f > self.best_f:
                self.best_f = f
                self.best_moves = [first_move]
            elif f == self.best_f:
                self.best_moves.append(first_move)
            return

        # otherwise expand children
        parent_g = max(max(row) for row in grid)
        for m in self.moves:
            g_delta, changed, grid1 = self._simulate_and_cost(grid, m, parent_g)
            if not changed:
                continue
            self._search(grid1, g_total + g_delta, depth + 1, first_move, threshold)

    def _simulate_and_cost(self, grid, move, prev_g):
        """Same cost helper as in AStarAgent."""
        new_grid, _, changed = simulate_move_on_grid(grid, move)
        if not changed:
            return 0, False, grid

        new_g = max(max(row) for row in new_grid)
        g_delta = (new_g - prev_g) * 10
        return g_delta, True, new_grid