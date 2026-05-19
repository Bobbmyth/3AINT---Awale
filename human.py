import pygame
import awale

class Human:
    def __init__(self, awale, player_id):
        self._awale = awale
        self._player_id = player_id
    
    def get_move(self):
        valid_moves = self._awale.est_valide(self._player_id)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    move = self._awale.coords_to_move(x, y, self._player_id)
                    if move is not None and move in valid_moves:
                        return move
                    