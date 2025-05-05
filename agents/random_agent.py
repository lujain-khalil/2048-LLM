import random
from agents.agent import Agent
from agents.registry import register_agent

@register_agent('random')
class RandomAgent(Agent):
    # __init__ is inherited from Agent, so self.game is available

    def get_move(self):
        """
        Return a random valid move.
        Only considers moves that would change the grid.
        """
        valid_moves = self.get_valid_moves()
        
        # If there are no valid moves, the game should be over
        if not valid_moves:
            raise ValueError("No valid moves available - game should be over")
            
        return random.choice(valid_moves)