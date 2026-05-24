import time
import random
from awale import awale
from stupidBot import StupidBot
from minmax import MinMax
from mcts import MCTS
from glouton import GloutonBot

class Concours:
    def __init__(self, nb_parties: int = 100):
        self.nb_parties = nb_parties

    def simuler_match(self, type_agent1, type_agent2) -> int:
        partie = awale("Machine 1", "Machine 2")
        
        bot1 = type_agent1(partie, 1) if type_agent1 in (StupidBot, GloutonBot) else type_agent1(iterations_max=100) if type_agent1 == MCTS else type_agent1(profondeur=4)
        bot2 = type_agent2(partie, 2) if type_agent2 in (StupidBot, GloutonBot) else type_agent2(iterations_max=100) if type_agent2 == MCTS else type_agent2(profondeur=4)
        jeu_continue = True
        
        while jeu_continue:
            camp = range(6) if partie.joueur_actif == 1 else range(6, 12)
            coups_legaux = [c for c in camp if partie.est_valide(c)]
            
            if not coups_legaux:
                break

            if partie.joueur_actif == 1:
                coup = bot1.get_move() if type_agent1 in (StupidBot, GloutonBot) else bot1.determiner_coup(partie.plateau, partie.score, 1)
            else:
                coup = bot2.get_move() if type_agent2 in (StupidBot, GloutonBot) else bot2.determiner_coup(partie.plateau, partie.score, 2)

            if coup not in coups_legaux:
                coup = random.choice(coups_legaux)

            jeu_continue = partie.tour_jeu(coup)

        if partie.score[0] > partie.score[1]:
            return 1
        elif partie.score[1] > partie.score[0]:
            return 2
        else:
            return 0

    def lancer_tournoi(self, nom_a: str, type_a, nom_b: str, type_b):
        print(f"\n" + "="*60)
        print(f"CONCOURS : {nom_a} VS {nom_b} ({self.nb_parties} parties)")
        print("="*60)

        victoires_a, victoires_b, egalites, premier_gagne = 0, 0, 0, 0
        debut = time.time()

        for i in range(self.nb_parties):
            if i % 2 == 0:
                res = self.simuler_match(type_a, type_b)
                if res == 1: victoires_a += 1; premier_gagne += 1
                elif res == 2: victoires_b += 1
                else: egalites += 1
            else:
                res = self.simuler_match(type_b, type_a)
                if res == 1: victoires_b += 1; premier_gagne += 1
                elif res == 2: victoires_a += 1
                else: egalites += 1

        duree = time.time() - debut
        print(f"Simulations terminées en {duree:.2f}s.")
        print(f" -> Victoires {nom_a} : {victoires_a} ({(victoires_a/self.nb_parties)*100:.1f}%)")
        print(f" -> Victoires {nom_b} : {victoires_b} ({(victoires_b/self.nb_parties)*100:.1f}%)")
        print(f" -> Égalités : {egalites} ({(egalites/self.nb_parties)*100:.1f}%)")
        print(f" -> Avantage premier joueur : {premier_gagne}/{self.nb_parties} victoires ({(premier_gagne/self.nb_parties)*100:.1f}%)")


if __name__ == "__main__":
    gestionnaire = Concours(nb_parties=10)
    
    # Tournoi 1 : MinMax VS StupidBot
    gestionnaire.lancer_tournoi("MinMax (Prof 4)", MinMax, "StupidBot", StupidBot)
    
    # Tournoi 2 : StupidBot VS GloutonBot (Requis par le sujet section 2.8)
    gestionnaire.lancer_tournoi("StupidBot", StupidBot, "GloutonBot", GloutonBot)
    
    # Tournoi 3 : MCTS VS MinMax
    gestionnaire.lancer_tournoi("MCTS (100 iter)", MCTS, "MinMax (Prof 4)", MinMax)