from agents.agent import Agent
from agents.registry import register_agent
from simulation.game_utils import simulate_move_on_grid
import numpy as np
import random
import math
import json
import os

@register_agent('td_learning')
class TDLearningAgent(Agent):
    """Agent using Temporal Difference Learning (TD(0)) with a linear value function."""
    def __init__(self, game, learning_rate=0.01, discount_factor=0.95, epsilon=0.1, weights_file='td_weights.json'):
        super().__init__(game)
        self.learning_rate = learning_rate       # alpha
        self.discount_factor = discount_factor   # gamma
        self.epsilon = epsilon                   # For epsilon-greedy exploration during training
        self.weights_file = weights_file
        # Initialize weights (e.g., based on number of features)
        self.num_features = 16 + 4 + 1 # Example: 16 log2 tiles + 4 mono scores + 1 empty count
        self.weights = np.zeros(self.num_features)
        self.load_weights()
        self.last_state_features = None
        self.last_state_value = 0
        self.last_reward = 0 # Add missing initialization

    def _extract_features(self, grid):
        """ Extracts features from the grid state. Normalize or scale features appropriately. """
        features = np.zeros(self.num_features)
        idx = 0
        empty_count = 0
        # Log2 of tile values (or 0 for empty) - 16 features
        for r in range(4):
            for c in range(4):
                val = grid[r][c]
                features[idx] = math.log2(val) if val > 0 else 0
                if val == 0: empty_count += 1
                idx += 1
        
        # Monotonicity features (simple difference based) - 4 features
        mono_score_lr = 0
        mono_score_ud = 0
        for r in range(4):
            for c in range(3):
                diff = features[r*4 + c+1] - features[r*4 + c]
                mono_score_lr += diff # Penalize decreases more?
        for c in range(4):
             for r in range(3):
                  diff = features[(r+1)*4 + c] - features[r*4 + c]
                  mono_score_ud += diff
        features[idx] = mono_score_lr / 16 # Normalize roughly
        features[idx+1] = -mono_score_lr / 16 # Try opposite direction too?
        features[idx+2] = mono_score_ud / 16
        features[idx+3] = -mono_score_ud / 16
        idx += 4
        
        # Empty cell count - 1 feature
        features[idx] = empty_count / 16.0 # Normalize
        idx += 1

        # --- Add more features: --- 
        # Smoothness (adjacent diffs)
        # Max tile position (corner bias?)
        # Number of merges possible?
        
        # Bias term (can be added as a constant feature if needed)
        # features = np.append(features, 1.0) # Add bias if self.weights includes bias weight

        # Ensure the number of features matches self.num_features
        assert idx == self.num_features, f"Feature count mismatch: {idx} vs {self.num_features}"
        
        return features

    def _get_value(self, grid):
        """ Estimates the value of a state using the linear function approximator. """
        features = self._extract_features(grid)
        return np.dot(self.weights, features)

    def get_move(self, is_training=False):
        """ Chooses the best move based on the estimated value of the next state. """
        
        possible_moves = ["UP", "DOWN", "LEFT", "RIGHT"]
        best_move = None
        best_value = -float('inf')
        current_grid = self.game.grid # The actual grid state

        if is_training and random.random() < self.epsilon:
            valid_moves = []
            for move in possible_moves:
                 # Use util function
                 _, _, changed = simulate_move_on_grid(current_grid, move)
                 if changed: valid_moves.append(move)
            best_move = random.choice(valid_moves) if valid_moves else random.choice(possible_moves)
            # Need to calculate value even for random move for TD update
            sim_grid, score_increase, _ = simulate_move_on_grid(current_grid, best_move)
            best_value = self._get_value(sim_grid)
            
        else:
            # Greedy action selection
            next_states_values = {}
            found_valid = False
            for move in possible_moves:
                 # Use util function
                sim_grid, score_increase, changed = simulate_move_on_grid(current_grid, move)
                if changed:
                    found_valid = True
                    value = self._get_value(sim_grid) 
                    next_states_values[move] = value 
                    if value > best_value:
                        best_value = value
                        best_move = move
            
            if best_move is None:
                if found_valid: 
                     best_move = random.choice(list(next_states_values.keys()))
                     # Recalculate best_value for the randomly chosen valid move
                     sim_grid, _, _ = simulate_move_on_grid(current_grid, best_move)
                     best_value = self._get_value(sim_grid)
                else: 
                     best_move = random.choice(possible_moves)
                     # Estimate value even if move is likely invalid (game over state)
                     sim_grid, _, _ = simulate_move_on_grid(current_grid, best_move)
                     best_value = self._get_value(sim_grid)
        
         # Use util function
        next_grid_after_move, next_score_increase, _ = simulate_move_on_grid(current_grid, best_move)
        self.last_state_features = self._extract_features(next_grid_after_move)
        self.last_state_value = self._get_value(next_grid_after_move) # Re-calculate value for s'
        self.last_reward = next_score_increase

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
            # print("Skipping TD update: Missing state features.") # Debug print
            return # Not enough info for update

        v_s = np.dot(self.weights, current_grid_features) # Value of the state *before* the move
        v_s_prime = self.last_state_value # Value of the state *after* the move (estimated by get_move)
        reward = self.last_reward # Immediate reward from the move
        
        # TD Error: delta = reward + gamma * V(s') - V(s)
        td_error = reward + self.discount_factor * v_s_prime - v_s
        
        # Update weights: w = w + alpha * delta * grad(V(s))
        # For linear function, grad(V(s)) is just the feature vector s
        update = self.learning_rate * td_error * current_grid_features
        self.weights += update
        
        # Optional: Clip weights or check for NaN/Inf
        if np.isnan(self.weights).any() or np.isinf(self.weights).any():
            print("Warning: NaN or Inf detected in weights. Resetting problematic weights?")
            # Handle reset or stop training
            # self.weights = np.nan_to_num(self.weights) # Example: Replace NaN/Inf with zero

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