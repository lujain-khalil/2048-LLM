from abc import ABC, abstractmethod
from simulation.game_utils import simulate_move_on_grid

class Agent(ABC):
    def __init__(self, game):
        """Initialize the agent with a reference to the game instance."""
        self.game = game

    def get_valid_moves(self):
        """
        Determine which moves are valid in the current game state.
        A move is valid if it would change the grid.
        
        Returns:
            list: A list of valid moves ('UP', 'DOWN', 'LEFT', 'RIGHT')
        """
        valid_moves = []
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]
        
        for direction in directions:
            # Use the game's utility function to see if the move would change the grid
            _, _, changed = simulate_move_on_grid(self.game.grid, direction)
            if changed:
                valid_moves.append(direction)
                
        return valid_moves

    @abstractmethod
    def get_move(self):
        """Return the next move as a string ('UP', 'DOWN', 'LEFT', or 'RIGHT')."""
        pass