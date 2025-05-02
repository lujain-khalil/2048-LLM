import random
from agents.random_agent import agent_instance as default_agent

class Game:
    def __init__(self):
        self.reset_grid()
        self.agent = default_agent
        self.new_tile_position = None

    def reset_grid(self):
        """Reset the grid with two new random tiles and clear last move."""
        self.grid = [[0 for _ in range(4)] for _ in range(4)]
        self.last_move = "NONE"
        self.score = 0  # Initialize score
        self.new_tile_position = None
        self.add_random_tile()
        self.add_random_tile()

    def add_random_tile(self):
        """Add a new tile (2 or 4) at a random empty cell."""
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4
            self.new_tile_position = [i, j]  # Track position of new tile

    def merge_row_left(self, row):
        """
        Merge a single row to the left following 2048 rules:
        slide numbers to the left and merge same adjacent tiles.
        """
        filtered = [num for num in row if num != 0]
        merged = []
        skip = False
        for i in range(len(filtered)):
            if skip:
                skip = False
                continue
            if i + 1 < len(filtered) and filtered[i] == filtered[i+1]:
                merged_value = filtered[i] * 2
                merged.append(merged_value)
                self.score += merged_value  # Add merged value to score
                skip = True
            else:
                merged.append(filtered[i])
        merged.extend([0] * (4 - len(merged)))
        return merged

    def move_grid(self, direction):
        """
        Move the grid in the given direction ("up", "down", "left", "right")
        following the 2048 game rules.
        """
        new_grid = None
        if direction == "LEFT":
            new_grid = [self.merge_row_left(row) for row in self.grid]
        elif direction == "RIGHT":
            new_grid = [list(reversed(self.merge_row_left(list(reversed(row))))) for row in self.grid]
        elif direction == "UP":
            transposed = [list(x) for x in zip(*self.grid)]
            new_transposed = [self.merge_row_left(row) for row in transposed]
            new_grid = [list(x) for x in zip(*new_transposed)]
        elif direction == "DOWN":
            transposed = [list(x) for x in zip(*self.grid)]
            new_transposed = [list(reversed(self.merge_row_left(list(reversed(row))))) for row in transposed]
            new_grid = [list(x) for x in zip(*new_transposed)]
        if new_grid is not None:
            self.grid = new_grid

    def simulate_move(self):
        """Simulate a move using the random agent, update the grid and record the move."""
        move = self.agent.get_move()
        self.move_grid(move)
        self.add_random_tile()
        self.last_move = move
        return move
    
    def set_agent(self, agent_module):
        self.agent = agent_module

game = Game()