"""Module MCTS - Conforme aux consignes (Politique de simulation aléatoire)"""
import math
import random
from typing import List, Tuple
from sommet import Sommet

class MCTS:
    def __init__(self, iterations_max=1000, temps_max=None, temperature=1.0, c=math.sqrt(2)):
        self.iterations_max = iterations_max
        self.temps_max = temps_max
        self.temperature = temperature
        self.c = c

    def _peut_nourrir(self, plateau: List[int], case: int, joueur_actif: int) -> bool:
        graines = plateau[case]
        if graines == 0:
            return False
        pos = case
        for _ in range(graines):
            pos = (pos + 1) % 12
            if pos == case:
                pos = (pos + 1) % 12
            if joueur_actif == 1 and pos >= 6:
                return True
            if joueur_actif == 2 and pos < 6:
                return True
        return False

    def coups_legaux(self, plateau: List[int], joueur_actif: int) -> List[int]:
        coups = []
        if joueur_actif == 1:
            cases = range(6)
            adversaire_vide = sum(plateau[6:12]) == 0
        else:
            cases = range(6, 12)
            adversaire_vide = sum(plateau[0:6]) == 0

        for case in cases:
            if plateau[case] == 0:
                continue
            if adversaire_vide and not self._peut_nourrir(plateau, case, joueur_actif):
                continue
            coups.append(case)
        return coups

    def jouer_coup(self, plateau: List[int], scores: List[int], joueur_actif: int, coup: int) -> Tuple[List[int], List[int]]:
        nouveau_plateau = plateau.copy()
        nouveaux_scores = scores.copy()

        graines = nouveau_plateau[coup]
        nouveau_plateau[coup] = 0
        case_courante = coup
        
        while graines > 0:
            case_courante = (case_courante + 1) % 12
            if case_courante == coup:
                case_courante = (case_courante + 1) % 12
            nouveau_plateau[case_courante] += 1
            graines -= 1

        cases_a_recolter = []
        if joueur_actif == 1:
            pos = case_courante
            while pos >= 6 and nouveau_plateau[pos] in (2, 3):
                cases_a_recolter.append(pos)
                pos -= 1
            adversaire_apres = [nouveau_plateau[i] for i in range(6, 12)]
            for p in cases_a_recolter:
                adversaire_apres[p - 6] = 0
            if sum(adversaire_apres) > 0:
                for p in cases_a_recolter:
                    nouveaux_scores[0] += nouveau_plateau[p]
                    nouveau_plateau[p] = 0
        else:
            pos = case_courante
            while pos <= 5 and nouveau_plateau[pos] in (2, 3):
                cases_a_recolter.append(pos)
                pos -= 1
            adversaire_apres = [nouveau_plateau[i] for i in range(6)]
            for p in cases_a_recolter:
                adversaire_apres[p] = 0
            if sum(adversaire_apres) > 0:
                for p in cases_a_recolter:
                    nouveaux_scores[1] += nouveau_plateau[p]
                    nouveau_plateau[p] = 0

        return nouveau_plateau, nouveaux_scores

    def partie_terminee(self, plateau: List[int]) -> bool:
        return sum(plateau) <= 3 or sum(plateau[0:6]) == 0 or sum(plateau[6:12]) == 0

    def determiner_coup(self, plateau: List[int], scores: List[int], joueur_actif: int) -> int:
        legaux = self.coups_legaux(plateau, joueur_actif)
        if not legaux:
            return 0 if joueur_actif == 1 else 6
        if len(legaux) == 1:
            return legaux[0]

        self.joueur_racine = joueur_actif
        racine = Sommet(plateau, scores, joueur_actif)
        iterations = 0
        
        while iterations < self.iterations_max:
            feuille = self._selectionner_et_developper(racine)
            score = self._simuler(feuille)
            feuille.retropropager(score)
            iterations += 1
            
        return self._selectionner_coup_final(racine)

    def _selectionner_et_developper(self, sommet: Sommet) -> Sommet:
        courant = sommet
        while not self.partie_terminee(courant.plateau):
            coups_legaux = self.coups_legaux(courant.plateau, courant.joueur_actif)
            if not coups_legaux:
                break
                
            if courant.tous_coups_explores(coups_legaux):
                _, enfant = courant.meilleur_enfant(self.c)
                courant = enfant
            else:
                coup = random.choice([c for c in coups_legaux if c not in courant.coups_tries])
                courant.coups_tries.add(coup)
                
                n_plat, n_sc = self.jouer_coup(courant.plateau, courant.scores, courant.joueur_actif, coup)
                prochain_joueur = 2 if courant.joueur_actif == 1 else 1
                
                enfant = courant.ajouter_enfant(coup, n_plat, n_sc, prochain_joueur)
                return enfant
        return courant

    def _simuler(self, sommet: Sommet) -> float:
        plat_sim = sommet.plateau.copy()
        sc_sim = sommet.scores.copy()
        joueur_sim = sommet.joueur_actif
        
        coups_max = 50
        nb_coups = 0
        
        while not self.partie_terminee(plat_sim) and nb_coups < coups_max:
            legaux = self.coups_legaux(plat_sim, joueur_sim)
            if not legaux:
                break
                
            coup = random.choice(legaux) # <-- Hasard pur exigé par la consigne
            plat_sim, sc_sim = self.jouer_coup(plat_sim, sc_sim, joueur_sim, coup)
            joueur_sim = 2 if joueur_sim == 1 else 1
            nb_coups += 1
            
        return self._evaluer_position(sc_sim)

    def _evaluer_position(self, scores: List[int]) -> float:

        mon_score = scores[self.joueur_racine - 1]
        autre_score = scores[2 - self.joueur_racine]
        
        if mon_score > autre_score:
            return 1.0
        elif mon_score < autre_score:
            return 0.0
        else:
            return 0.5

    def _selectionner_coup_final(self, racine: Sommet) -> int:
        if not racine.enfants:
            coups = self.coups_legaux(racine.plateau, racine.joueur_actif)
            return coups[0] if coups else (0 if racine.joueur_actif == 1 else 6)
            
        coups = list(racine.enfants.keys())
        visites = [racine.enfants[coup].visites for coup in coups]
        return coups[visites.index(max(visites))]