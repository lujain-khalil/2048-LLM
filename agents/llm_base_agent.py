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
        """Create a prompt for the LLM including the game state, valid moves, 
        and high-level strategy guidance based on the 2048 heuristics paper."""
        grid_str = self.get_grid_representation()
        valid_moves = self.get_valid_moves()
        valid_moves_str = ", ".join(valid_moves) if valid_moves else "UP, DOWN, LEFT, RIGHT"
        
        prompt = f"""
You are a 2048 agent, an expert AI that plays the 2048 puzzle.

GAME RULES
- The board is a 4 x 4 grid of numbers (powers of 2).  
- Each turn the player chooses one move: **UP, DOWN, LEFT, or RIGHT**.
- After all tiles slide and merge per 2048 rules, a new tile (2 or 4) spawns in a random empty cell.  
- The game is won when any tile reaches **2048**.  
- The game is lost when no legal moves remain.

OBJECTIVE
Your goal is to win the game by creating a 2048 tile. 
If you reach 2048, keep playing the game with the goal to reach higher maximum tiles, until no legal moves remain.
You should try to follow the following strategies:
1. **Moves with empty tiles**: Make moves that create empty tiles, especially earlier in the game.
2. **Create a snake pattern**: Try to create a snake-like pattern in the grid, with the highest value starting in the upper left corner of the grid.

Here is the current grid (0s shown as “_”):

{grid_str}

Valid moves: {valid_moves_str}

Given these guidelines, pick **exactly one** of the valid moves (UP, DOWN, LEFT, or RIGHT) and reply with that word only.
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