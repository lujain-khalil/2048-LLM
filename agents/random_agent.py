import random
from agents.agent import Agent
from agents.registry import register_agent

@register_agent('random')
class RandomAgent(Agent):
    # __init__ is inherited from Agent, so self.game is available

    def get_move(self):
        # The game state (self.game.grid) isn't needed for random moves,
        # but other agents will use it.
        return random.choice(["UP", "RIGHT", "DOWN", "LEFT"])

# Removed the instance creation here. Instantiation will happen
# when the simulation selects the agent.
