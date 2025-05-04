import os
from abc import abstractmethod
from agents.agent import Agent
from simulation.game_utils import simulate_move_on_grid

class LLMBaseAgent(Agent):
    """
    Base class for LLM-based agents to play 2048.
    Subclasses must implement the call_llm method.
    """
    
    def __init__(self, game):
        """Initialize the agent with a reference to the game instance."""
        super().__init__(game)
    
    @abstractmethod
    def call_llm(self, prompt):
        """
        Call the specific LLM with the given prompt.
        Must be implemented by child classes.
        Returns the LLM's raw response.
        Raises an exception if the API call fails.
        """
        pass
    
    def get_valid_moves(self):
        """
        Determine which moves are valid in the current game state.
        A move is valid if it would change the grid.
        """
        valid_moves = []
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]
        
        for direction in directions:
            # Use the game's utility function to see if the move would change the grid
            _, _, changed = simulate_move_on_grid(self.game.grid, direction)
            if changed:
                valid_moves.append(direction)
                
        return valid_moves
    
    def get_grid_representation(self):
        """Convert the current grid to a string representation for the LLM."""
        grid_str = ""
        for row in self.game.grid:
            grid_str += " ".join([str(cell) if cell != 0 else "_" for cell in row]) + "\n"
        return grid_str
    
    def create_prompt(self):
        """Create a prompt for the LLM including the game state and valid moves."""
        grid_str = self.get_grid_representation()
        valid_moves = self.get_valid_moves()
        
        # If there are no valid moves, game would be over but prompt should still have a response format
        valid_moves_str = ", ".join(valid_moves) if valid_moves else "UP, DOWN, LEFT, RIGHT (though none will change the grid)"
        
        prompt = f"""You are controlling a 2048 game. Here's the current grid:

{grid_str}

Current score: {self.game.score}

Valid moves (that will change the grid): {valid_moves_str}

Analyze the grid and choose the best move from the valid options.
Respond with exactly one of these words: {valid_moves_str}.
"""
        return prompt
    
    def get_move(self):
        """Get the next move by querying the LLM, ensuring only valid moves are used."""
        valid_moves = self.get_valid_moves()
        
        # If no moves are valid, the game should be over, but we'll return a default move
        # This shouldn't happen in practice since the game checks for game over before asking for moves
        if not valid_moves:
            raise ValueError("No valid moves available - game should be over")
        
        # Create prompt that specifies only valid moves
        prompt = self.create_prompt()
        response = self.call_llm(prompt)
        
        # Extract move from response
        response = response.strip().upper()
        
        # If response is exactly one of the valid moves, return it
        if response in valid_moves:
            return response
        
        # Otherwise, try to extract a valid move from the response
        for move in valid_moves:
            if move in response:
                return move
        
        # If we can't determine a valid move from the response, use the first valid move
        # This ensures we never make an invalid move
        first_valid_move = valid_moves[0]
        raise ValueError(f"LLM response '{response}' did not contain a valid move. Defaulting to {first_valid_move} would be necessary.") 