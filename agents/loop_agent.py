from agents.agent import Agent
from agents.registry import register_agent

@register_agent('loop') # Register the agent
class LoopAgent(Agent):
    # No need to override __init__ if we just need self.game
    # The base Agent class __init__ handles storing self.game

    _moves = ["UP", "RIGHT", "DOWN", "LEFT"]
    
    def __init__(self, game):
        """Initialize LoopAgent, calling super and resetting index."""
        super().__init__(game) # Call base class init
        self.current_index = 0 # Use instance variable for index
        self.last_valid_move = None

    def get_move(self):
        """ 
        Cycles through moves UP, RIGHT, DOWN, LEFT but only returns valid moves.
        If the next move in the sequence is invalid, it will try the next one,
        and so on until a valid move is found.
        """
        valid_moves = self.get_valid_moves()
        
        # If there are no valid moves, the game should be over
        if not valid_moves:
            raise ValueError("No valid moves available - game should be over")
        
        # Try up to 4 moves (the full cycle) to find a valid one
        for _ in range(len(self._moves)):
            move = self._moves[self.current_index]
            self.current_index = (self.current_index + 1) % len(self._moves)
            
            if move in valid_moves:
                self.last_valid_move = move
                return move
        
        # If we couldn't find a valid move in the cycle, return any valid move
        # (this should never happen as we checked for valid moves at the start)
        return valid_moves[0]

# Remove instance creation - registry handles classes
