import random
from agents.agent import Agent

class RandomAgent(Agent):
    def get_move(self):
        return random.choice(["UP", "RIGHT", "DOWN", "LEFT"])

# Create an instance for registration.
agent_instance = RandomAgent()
