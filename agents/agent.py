from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, game):
        """Initialize the agent with a reference to the game instance."""
        self.game = game

    @abstractmethod
    def get_move(self):
        """Return the next move as a string ('UP', 'DOWN', 'LEFT', or 'RIGHT')."""
        pass