# agents/random_agent.py
import random
from agents.agent import Agent

class RandomAgent(Agent):
    def get_move(self):
        return random.choice(["up", "down", "left", "right"])

# Create an instance for registration.
agent_instance = RandomAgent()
