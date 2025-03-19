# agents/loop_agent.py
from agents.agent import Agent

class LoopAgent(Agent):
    _moves = ["up", "right", "down", "left"]
    _current_index = 0

    def get_move(self):
        move = self._moves[self._current_index]
        self._current_index = (self._current_index + 1) % len(self._moves)
        return move

# Create an instance for registration.
agent_instance = LoopAgent()
