import random

def get_move():
    """Randomly return one of the moves: up, down, left, or right."""
    return random.choice(["up", "down", "left", "right"])