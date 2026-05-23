from awale import awale
import random

class StupidBot:
    def __init__(self, awale, player_id):
        self._awale = awale
        self._player_id = player_id

    def get_move(self):
        if self._player_id == 1:
            cases = range(6)
        else:
            cases = range(6, 12)
        valid_moves = [case for case in cases if self._awale.est_valide(case)]
        return random.choice(valid_moves)