from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic, get_empty_cells, is_terminal
import random
import math
import time

class _MCTSNode:
    def __init__(self, grid, move=None, parent=None, is_chance=False, score=None):
        self.grid = [row[:] for row in grid]
        self.parent = parent
        self.move = move
        self.is_chance = is_chance
        self.children = []
        self.visits = 0
        self.value = 0.0
        if not self.is_chance:
            self.untried_moves = self._get_valid_moves()
        else:
            self.untried_moves = None

    def _get_valid_moves(self):
        """Get valid moves that would change the grid state."""
        moves = []
        for move in ["UP", "DOWN", "LEFT", "RIGHT"]:
            # Use util function
            _, _, changed = simulate_move_on_grid(self.grid, move)
            if changed:
                moves.append(move)
        random.shuffle(moves)
        return moves
    
    def is_fully_expanded(self):
        if self.is_chance:
            return False
        return len(self.untried_moves) == 0

    def expand(self):
        # if not self.untried_moves:
        #     return None 
        if not self.is_chance:
            move = self.untried_moves.pop()
            new_grid, _, _ = simulate_move_on_grid(self.grid, move)
            child = _MCTSNode(new_grid, move=move, parent=self, is_chance=True)
        else:
        # Add random tile 
            empty_cells = get_empty_cells(self.grid)
            if not empty_cells:
                return None
            
            r, c = random.choice(empty_cells)
            new_grid = [row[:] for row in self.grid]
            tile = 2 if random.random() < 0.9 else 4
            new_grid[r][c] = tile
            child = _MCTSNode(new_grid, move=(r, c, tile), parent=self, is_chance=False) 
        
        self.children.append(child)
        return child
    
    def best_uct_child(self, c):
        """ Select child with highest UCT value. """
        log_parent = math.log(self.visits)
        def uct(n):
            return n.value / n.visits + c * math.sqrt(log_parent / n.visits)
        return max(self.children, key=uct)

    # def best_child(self):
    #     """ After simulations, choose the move visited most often. """
    #     return max(self.children, key=lambda n: n.visits)

    def backpropagate(self, reward):
        node = self
        while node:
            node.visits += 1
            node.value += reward
            node = node.parent

class RolloutPolicy:
    @staticmethod
    def select_move(grid):
        """
        Greedy heuristic rollout: pick the move whose resulting grid
        scores highest under calculate_heuristic.
        """
        best_move, best_score = None, -float("inf")
        for move in ("UP", "DOWN", "LEFT", "RIGHT"):
            new_grid, _, changed = simulate_move_on_grid(grid, move)
            if not changed:
                continue
            h = calculate_heuristic(new_grid)
            if h > best_score:
                best_score, best_move = h, move
        return best_move

@register_agent('mcts')
class MCTSAgent(Agent):
    """Agent using Monte Carlo Tree Search."""
    def __init__(self, game, iterations=1000, rollout_depth=15):
        super().__init__(game)
        self.iterations = iterations
        self.rollout_depth = rollout_depth
        self.c = math.sqrt(2)

    def get_move(self):
        root = _MCTSNode(self.game.grid)

        valid_moves = self.get_valid_moves()
        if not valid_moves:
            raise ValueError("No valid moves available - game should be over")
            
        start_time = time.time()

        # Run the MCTS iterations
        for _ in range(self.iterations):
            node = root

            while True:
                if is_terminal(node.grid):
                    break
                if not node.is_fully_expanded():
                    node = node.expand() or node
                    break            
                else:
                    if node.is_chance:
                        # At chance nodes, sample an outcome
                        node = node.expand() or node
                        break
                    else:
                        # At decision nodes, pick UCT child
                        node = node.best_uct_child(self.c)
                        
            reward = self._rollout(node.grid)
            node.backpropagate(reward)            
        
        if not root.children:
            raise RuntimeError("MCTS failed to expand any root children — check your iteration count or terminal logic")

        best_child = max(root.children, key=lambda n: n.visits)
        return best_child.move
 
    def _rollout(self, grid):
        """Simulate up to rollout_depth steps, return max tile seen."""
        sim_grid = [row[:] for row in grid]
        max_tile = max(cell for row in sim_grid for cell in row)
        for _ in range(self.rollout_depth):
            if is_terminal(sim_grid):
                break
            move = RolloutPolicy.select_move(sim_grid)
            if move is None:
                break
            sim_grid, _, _ = simulate_move_on_grid(sim_grid, move)

            # Add random tile 
            empty_cells = get_empty_cells(sim_grid)
            if empty_cells:
                r, c = random.choice(empty_cells)
                sim_grid[r][c] = 2 if random.random() < 0.9 else 4

            max_tile = max(max_tile, max(cell for row in sim_grid for cell in row))
        bonus = calculate_heuristic(sim_grid) * 0.001
        return max_tile + bonus