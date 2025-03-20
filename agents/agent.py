from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def get_move(self):
        """Return the next move as a string ('up', 'down', 'left', or 'right')."""
        pass