from agents.agent import Agent
from agents.registry import register_agent

@register_agent('loop') # Register the agent
class LoopAgent(Agent):
    # No need to override __init__ if we just need self.game
    # The base Agent class __init__ handles storing self.game

    _moves = ["UP", "RIGHT", "DOWN", "LEFT"]
    _current_index = 0 # This should ideally be instance state, not class state

    def __init__(self, game):
        """Initialize LoopAgent, calling super and resetting index."""
        super().__init__(game) # Call base class init
        self.current_index = 0 # Use instance variable for index

    def get_move(self):
        """ Cycles through moves UP, RIGHT, DOWN, LEFT. """
        move = self._moves[self.current_index]
        self.current_index = (self.current_index + 1) % len(self._moves)
        return move

# Remove instance creation - registry handles classes
# agent_instance = LoopAgent()
