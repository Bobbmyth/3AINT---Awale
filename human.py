class Human:
    def __init__(self, awale):
        self._awale = awale
    
    def get_move(self, pos, trous):
        x, y = pos
        for case, rect in trous.items():
            if rect.collidepoint(x, y):
                if self._awale.est_valide(case):
                    return case
        return None