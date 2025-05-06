from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid, empty_score, calculate_heuristic, smoothness_score, monotonicity_score
import numpy as np
import random
import math
import json
import os

@register_agent('td_learning')
class TDLearningAgent(Agent):
    """Agent using Temporal Difference Learning (TD(0)) with a linear value function."""
    def __init__(self, game, learning_rate=0.001, discount_factor=0.99, epsilon=0.2, weights_file='td_weights.json'):
        super().__init__(game)
        self.learning_rate = learning_rate       # alpha
        self.discount_factor = discount_factor   # gamma
        self.epsilon = epsilon                   # For epsilon-greedy exploration during training
        self.weights_file = weights_file

        # Initialize weights (e.g., based on number of features)
        # self.num_features = (4*4) + 1
        # self.num_features = 1
        self.num_features = 20

        self.weights = np.zeros(self.num_features)
        is_training = False ################## # Change this to False for evaluation
        if not is_training:
            self.load_weights()            
    
        self.last_state_features = None
        self.last_state_value = 0.0
        self.last_reward = 0.0

    def _extract_features(self, grid):
        """ Extracts features from the grid state. Normalize or scale features appropriately. """
        def potential_merge_bonus(g, weight=2.0):
            """Bonus for adjacent tiles with same value (potential merges)"""
            bonus = 0
            for i in range(4):
                for j in range(4):
                    if g[i][j] == 0:
                        continue
                    # Check right neighbor
                    if j < 3 and g[i][j] == g[i][j+1]:
                        bonus += g[i][j]
                    # Check bottom neighbor
                    if i < 3 and g[i][j] == g[i+1][j]:
                        bonus += g[i][j]
            return weight * bonus
        
        features = np.zeros(self.num_features)
        idx = 0
        
        W = [
            [2**15, 2**14, 2**13, 2**12],
            [2**8,  2**9,  2**10, 2**11],
            [2**7,  2**6,   2**5,  2**4],
            [2**0,  2**1,   2**2,  2**3]
        ]
        for i in range(4):
            for j in range(4):
                features[idx] = grid[i][j] * W[i][j]
                idx += 1
        
        features[idx] = empty_score(grid)  # Empty cell bonus
        idx += 1

        features[idx] = smoothness_score(grid)  # Smoothness score
        idx += 1

        features[idx] = monotonicity_score(grid)
        idx += 1

        features[idx] = potential_merge_bonus(grid)
        idx += 1

        return features

    def _get_value(self, grid):
        """ Estimates the value of a state using the linear function approximator. """
        features = self._extract_features(grid)
        return np.dot(self.weights, features)

    def get_move(self, training=False):
        """ Chooses the best move based on the estimated value of the next state. """
        valid_moves = self.get_valid_moves()
        
        # If there are no valid moves, the game should be over
        if not valid_moves:
            raise ValueError("No valid moves available - game should be over")
            
        best_move = None
        best_value = -float('inf')
        current_grid = self.game.grid
        
        # Epsilon-greedy policy for training
        if training and random.random() < self.epsilon:
            choice = random.choice(valid_moves)
            sim_grid, score, _ = simulate_move_on_grid(current_grid, choice)
            max_tile = max(max(row) for row in sim_grid)
            self.last_reward = math.log2(max_tile) + (0.01 * calculate_heuristic(sim_grid))
            return choice
        
        # Greedy action selection: choose the move that leads to the highest value state
        for move in valid_moves:
            sim_grid, score, _ = simulate_move_on_grid(current_grid, move)
            value = self._get_value(sim_grid)
            if value > best_value:
                best_value = value
                best_move = move
                max_tile = max(max(row) for row in sim_grid)
                best_reward = math.log2(max_tile) + (0.01 * calculate_heuristic(sim_grid))
            
        self.last_reward = best_reward
        return best_move

    def update_weights(self, current_grid_features):
        """
        Perform the TD(0) update after a move has been made and the next state is observed.
        Requires the features of the state *before* the move (`current_grid_features`),
        the reward received (`self.last_reward`), and the estimated value of the 
        state *after* the move (`self.last_state_value`).
        
        NOTE: This needs to be called externally during a training loop.
        The value `self.last_state_value` is the V(s') part.
        The value V(s) needs to be calculated from `current_grid_features`.
        """
        if self.last_state_features is None or current_grid_features is None:
            print("Skipping TD update: Missing state features.") # Debug print
            return # Not enough info for update

        v_s = np.dot(self.weights, current_grid_features) 
        v_s_prime = np.dot(self.weights, self.last_state_features) 
        td_err   = self.last_reward + self.discount_factor*v_s_prime - v_s
        
        # Update weights: w = w + alpha * delta * grad(V(s))
        # For linear function, grad(V(s)) is just the feature vector s
        self.weights += self.learning_rate * td_err * current_grid_features
        
        # Optional: Clip weights or check for NaN/Inf
        if np.isnan(self.weights).any() or np.isinf(self.weights).any():
            print("Warning: NaN or Inf detected in weights. Resetting problematic weights?")
            # Handle reset or stop training
            self.weights = np.nan_to_num(self.weights) # Example: Replace NaN/Inf with zero

    def save_weights(self):
        """Saves the learned weights to a file."""
        try:
            with open(self.weights_file, 'w') as f:
                json.dump(self.weights.tolist(), f)
            # print(f"Weights saved to {self.weights_file}") # Less frequent print
        except Exception as e:
            print(f"Error saving weights: {e}")

    def load_weights(self):
        """Loads weights from a file if it exists."""
        if os.path.exists(self.weights_file):
            try:
                with open(self.weights_file, 'r') as f:
                    loaded_weights = np.array(json.load(f))
                    if loaded_weights.shape == self.weights.shape:
                        self.weights = loaded_weights
                        print(f"Weights loaded from {self.weights_file}")
                    else:
                         print(f"Warning: Loaded weights shape mismatch ({loaded_weights.shape} vs {self.weights.shape}). Ignoring file.")
            except Exception as e:
                print(f"Error loading weights: {e}. Using zeros.")
        else:
            print("Weights file not found. Using zero weights.") 
            try:
                with open(self.weights_file, 'w') as f:
                    json.dump(self.weights.tolist(), f)
            except Exception as e:
                print(f"Error creating new weights file: {e}")