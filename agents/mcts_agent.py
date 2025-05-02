from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, calculate_heuristic, get_empty_cells, is_terminal
import random
import math
import time
import copy

class MCTSNode:
    def __init__(self, grid, score, move=None, parent=None):
        self.grid = grid # Expects tuple representation
        self.score = score
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_moves = self._get_possible_moves()

    def _get_possible_moves(self):
        moves = []
        list_grid = [list(row) for row in self.grid] # Convert tuple grid to list for simulation
        for move in ["UP", "DOWN", "LEFT", "RIGHT"]:
            # Use util function
            _, _, changed = simulate_move_on_grid(list_grid, move)
            if changed:
                moves.append(move)
        random.shuffle(moves)
        return moves

    def ucb1(self, exploration_constant=1.414):
        if self.visits == 0:
            return float('inf') # Ensure unvisited nodes are selected
        # UCB1 formula: Average value + exploration term
        # Add small epsilon to visits to prevent division by zero if parent visits = 0 (shouldn't happen)
        avg_value = self.value / self.visits
        exploration = exploration_constant * math.sqrt(math.log(self.parent.visits + 1e-6) / self.visits)
        return avg_value + exploration

    def select_child(self):
        """Selects the best child node based on UCB1 score."""
        best_score = -float('inf')
        best_child = None
        for child in self.children:
            score = child.ucb1()
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def expand(self):
        if not self.untried_moves:
            return None 
        
        move = self.untried_moves.pop()
        list_grid = [list(row) for row in self.grid]
         # Use util function
        sim_grid_list, score_increase, _ = simulate_move_on_grid(list_grid, move)
        
        list_sim_grid = sim_grid_list # Already a list
        # Use util function
        empty_cells = get_empty_cells(list_sim_grid)
        if empty_cells:
            r, c = random.choice(empty_cells)
            list_sim_grid[r][c] = 2 if random.random() < 0.9 else 4
        
        child_grid_tuple = tuple(map(tuple, list_sim_grid))
        new_score = self.score + score_increase 
        
        # Optional: Check if child state already exists (could be simplified)
        # for child in self.children:
        #      if child.grid == child_grid_tuple:
        #           return child 
                  
        child_node = MCTSNode(child_grid_tuple, new_score, move=move, parent=self)
        self.children.append(child_node)
        return child_node

    def is_terminal(self):
        # Use util function
         return is_terminal([list(row) for row in self.grid])

@register_agent('mcts')
class MCTSAgent(Agent):
    """Agent using Monte Carlo Tree Search."""
    def __init__(self, game, iterations=100, rollout_depth=10):
        super().__init__(game)
        self.iterations = iterations # Number of MCTS iterations per move
        self.rollout_depth = rollout_depth

    def get_move(self):
        start_time = time.time()
        current_grid_tuple = tuple(map(tuple, self.game.grid))
        root = MCTSNode(current_grid_tuple, self.game.score)

        if not root.untried_moves and not root.children and root.is_terminal():
             return random.choice(["UP", "DOWN", "LEFT", "RIGHT"]) 

        for _ in range(self.iterations):
            node = self._select(root)
            if node is None: continue 
            
            # Expand only if not terminal AND has untried moves
            if node.untried_moves and not node.is_terminal():
                 expanded_node = node.expand()
                 if expanded_node: # If expansion succeeded (didn't hit existing child maybe)
                     node = expanded_node # Simulate from the newly expanded node
                 # else: simulate from the node itself if expansion failed?
            
            # Simulate from the selected/expanded node
            reward = self._simulate(node)
            self._backpropagate(node, reward)

        best_move = None
        most_visits = -1
        if not root.children:
             if root.untried_moves:
                  # If no children after iterations, but moves exist, pick one
                  # This can happen if iterations is very low
                  best_move = random.choice(root.untried_moves) 
             else: 
                  # No children, no untried moves - game must be over or stuck
                  best_move = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        else:
             # Select based on visits
             for child in root.children:
                 # print(f" Child Move: {child.move}, Visits: {child.visits}, Value: {child.value:.2f}") # Debug print
                 if child.visits > most_visits:
                     most_visits = child.visits
                     best_move = child.move

        # print(f"MCTS chose {best_move} after {self.iterations} iterations ({time.time() - start_time:.2f}s)")
        return best_move if best_move else random.choice(["UP", "DOWN", "LEFT", "RIGHT"])

    def _select(self, node):
        while not node.is_terminal():
            if node.untried_moves:
                return node 
            else:
                if not node.children:
                     return node # Terminal leaf node
                node = node.select_child()
                if node is None: return node.parent 
        return node 

    def _simulate(self, node):
        current_grid_list = [list(row) for row in node.grid]
        current_score = node.score
        depth = 0
        
        while depth < self.rollout_depth:
            possible_moves = []
             # Use util function
            for move in ["UP", "DOWN", "LEFT", "RIGHT"]:
                _, _, changed = simulate_move_on_grid(current_grid_list, move)
                if changed:
                    possible_moves.append(move)
            
            if not possible_moves:
                break 
            
            move = random.choice(possible_moves)
             # Use util function
            current_grid_list, score_increase, _ = simulate_move_on_grid(current_grid_list, move)
            current_score += score_increase
            
             # Use util function
            empty_cells = get_empty_cells(current_grid_list)
            if empty_cells:
                r, c = random.choice(empty_cells)
                current_grid_list[r][c] = 2 if random.random() < 0.9 else 4
            else:
                break 
                
            depth += 1
        
         # Use util function
        return calculate_heuristic(current_grid_list, current_score) 

    def _backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent 