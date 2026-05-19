import random

class StupidBot:
    def __init__(self, awale, player_id):
        self._awale = awale
        self._player_id = player_id
        
    def get_move(self):
        valid_moves = self.get_valid_moves(self._player_id)
        return random.choice(valid_moves)