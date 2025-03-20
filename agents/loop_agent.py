from agents.agent import Agent

class LoopAgent(Agent):
    _moves = ["UP", "RIGHT", "DOWN", "LEFT"]
    _current_index = 0

    def get_move(self):
        move = self._moves[self._current_index]
        self._current_index = (self._current_index + 1) % len(self._moves)
        return move

# Create an instance for registration.
agent_instance = LoopAgent()
