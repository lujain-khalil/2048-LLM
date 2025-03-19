_moves = ["up", "right", "down", "left"]
_current_index = 0

def get_move():
    global _current_index
    move = _moves[_current_index]
    _current_index = (_current_index + 1) % len(_moves)
    return move
