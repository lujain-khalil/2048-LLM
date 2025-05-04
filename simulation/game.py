import random
from agents.registry import get_agent, get_agent_with_params, list_agents
from simulation.game_utils import simulate_move_on_grid, get_empty_cells, is_terminal as is_terminal_static
import traceback

class Game:
    def __init__(self):
        # Default to random agent if available
        default_agent_name = 'random'
        agent_class = get_agent(default_agent_name)
        if not agent_class:
            # Fallback: try to find *any* agent if random isn't registered yet
            all_agents = list_agents() 
            if all_agents:
                 default_agent_name = all_agents[0]
                 agent_class = get_agent(default_agent_name)
                 print(f"Warning: Default agent 'random' not found. Using '{default_agent_name}' instead.")
            else:
                 # This case should ideally not happen if registry works
                 raise ImportError("No agents found in registry. Cannot initialize Game.")
        
        self.agent_class = agent_class
        self.agent_name = default_agent_name
        self.agent_params = None
        self.agent = None
        self.reset_grid()

    def reset_grid(self):
        """Reset the grid, clear last move, and instantiate the current agent."""
        self.grid = [[0 for _ in range(4)] for _ in range(4)]
        self.last_move = ""
        self.score = 0
        self.add_random_tile()
        self.add_random_tile()
        # Ensure agent is instantiated *after* the grid is initialized
        if self.agent_class:
            # Use centralized parameter handling
            self.agent = get_agent_with_params(self.agent_name, self, self.agent_params)
            if not self.agent:
                raise Exception(f"Failed to instantiate agent '{self.agent_name}' with params {self.agent_params}")
        else:
             # This indicates a problem during __init__
             raise Exception("Agent class not set during Game initialization.")

    def add_random_tile(self):
        """Add a new tile (2 or 4) at a random empty cell."""
        # Use the utility function
        empty_cells = get_empty_cells(self.grid)
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4

    def move_grid(self, direction):
        """
        Move the grid in the given direction using the utility function.
        Returns True if the grid changed, False otherwise.
        Updates the game score.
        """
        # Use the utility function for simulation
        new_grid, score_increase, changed = simulate_move_on_grid(self.grid, direction)
        if changed:
            self.grid = new_grid
            self.score += score_increase
            return True
        else:
            return False

    def is_game_over(self):
        """Check if no more moves are possible using the static utility function."""
        # Use the utility function for the check
        return is_terminal_static(self.grid)

    def get_max_tile(self):
        """Return the value of the highest tile on the board."""
        max_tile = 0
        # Optimize slightly by avoiding max on empty row
        for row in self.grid:
             if any(row):
                  max_tile = max(max_tile, max(row))
        return max_tile

    def simulate_move(self):
        """Get a move from the agent, execute it, add tile if moved, check game over."""
        if not self.agent:
             # This might happen if agent fails to instantiate in reset_grid
             raise Exception("Agent not initialized! Cannot simulate move.")

        # First check if the game is already over (no valid moves)
        if self.is_game_over():
            self.last_move = "GAME OVER - No valid moves"
            return None, False, True, self.score

        try:
            move = self.agent.get_move()
            
            # Ensure move is valid
            if move not in ["UP", "DOWN", "LEFT", "RIGHT"]:
                error_msg = f"Invalid move '{move}' returned by agent"
                self.last_move = f"ERROR: {error_msg}"
                game_over = self.is_game_over()
                return None, False, game_over, self.score
                
            moved = self.move_grid(move)

            if moved:
                self.add_random_tile()
                self.last_move = move
            else:
                # This should not happen anymore with our improved logic,
                # but we keep it as a safeguard
                self.last_move = f"{move} (invalid - no change in grid)"

            game_over = self.is_game_over()
            return move, moved, game_over, self.score
            
        except Exception as e:
            # Log the error
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            print(f"Agent error: {error_msg}")
            print(traceback_str)
            
            # Set error as last move for UI display
            self.last_move = f"ERROR: {error_msg[:50]}..."
            
            # Return error state without moving
            game_over = self.is_game_over()
            return None, False, game_over, self.score

    def set_agent(self, agent_name, agent_params=None):
        """Set the agent class by name using the registry."""
        self.agent_name = agent_name
        self.agent_params = agent_params
        self.agent_class = get_agent(agent_name)
        
        if self.agent_class:
            print(f"Agent class set to: {agent_name} with params: {agent_params}")
            # Agent instance will be created/updated on next reset_grid()
            return True
        else:
            print(f"Error: Agent class '{agent_name}' not found in registry: {list_agents()}")
            return False