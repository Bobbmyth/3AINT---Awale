"""Module MCTS - Implémentation de Monte Carlo Tree Search"""
import math, random, time
from typing import Optional, List, Tuple
from copy import deepcopy
from sommet import Sommet

class MCTS:
    def __init__(self, iterations_max=1000, temps_max=None, temperature=1.0, c=math.sqrt(2)):
        self.iterations_max = iterations_max
        self.temps_max = temps_max
        self.temperature = temperature
        self.c = c

    def coups_legaux(self, plateau: List[int], joueur_actif: int) -> List[int]:
        """
        Retourne les coups légaux (0-5) pour le joueur actif.
        Le joueur actif a TOUJOURS ses cases en [0:6], l'adversaire en [6:12].
        """
        coups = []
        adversaire_vide = sum(plateau[6:12]) == 0
        for case in range(6):
            if plateau[case] == 0:
                continue
            # Règle anti-famine : si l'adversaire n'a plus de graines,
            # on ne joue que les coups qui lui en donnent
            if adversaire_vide and plateau[case] <= 5 - case:
                continue
            coups.append(case)
        return coups

    def jouer_coup(self, plateau: List[int], scores: List[int], joueur_actif: int, coup: int) -> Tuple[List[int], List[int]]:
        """
        Joue un coup et retourne le nouveau plateau et les nouveaux scores.
        Convention : le joueur actif a TOUJOURS ses cases en [0:6].
        Après le coup, le plateau est tourné pour que le joueur suivant
        ait ses cases en [0:6].
        """
        nouveau_plateau = deepcopy(plateau)
        nouveaux_scores = deepcopy(scores)

        # Le joueur actif joue toujours une case en [0:6]
        graine = nouveau_plateau[coup]
        nouveau_plateau[coup] = 0
        case_courante = coup
        while graine > 0:
            case_courante = (case_courante + 1) % 12
            nouveau_plateau[case_courante] += 1
            graine -= 1

        # Récolte : si la dernière graine atterrit du côté adverse [6:11]
        # avec 2 ou 3 graines, on récolte en remontant
        score = 0
        index = case_courante
        while index >= 6 and (nouveau_plateau[index] == 2 or nouveau_plateau[index] == 3):
            score += nouveau_plateau[index]
            nouveau_plateau[index] = 0
            index -= 1
        nouveaux_scores[joueur_actif - 1] += score  # score au bon joueur

        # Rotation : le joueur suivant prend sa place en [0:6]
        nouveau_plateau = nouveau_plateau[6:12] + nouveau_plateau[0:6]
        return nouveau_plateau, nouveaux_scores

    def partie_terminee(self, plateau: List[int]) -> bool:
        return sum(plateau) == 0

    def determiner_coup(self, plateau: List[int], scores: List[int], joueur_actif: int) -> int:
        racine = Sommet(plateau, scores, joueur_actif)
        debut = time.time()
        iterations = 0
        while iterations < self.iterations_max:
            if self.temps_max is not None and (time.time() - debut) > self.temps_max:
                break
            feuille = self._selectionner_et_developper(racine)
            score = self._simuler(feuille)
            feuille.retropropager(score)
            iterations += 1
        return self._selectionner_coup_final(racine)

    def _selectionner_et_developper(self, sommet: Sommet) -> Sommet:
        courant = sommet
        while not self.partie_terminee(courant.plateau):
            coups_legaux = self.coups_legaux(courant.plateau, courant.joueur_actif)
            if len(coups_legaux) == 0:
                break
            if courant.tous_coups_explores(coups_legaux):
                coup, enfant = courant.meilleur_enfant(self.c)
                courant = enfant
            else:
                coup = random.choice([c for c in coups_legaux if c not in courant.coups_tries])
                courant.coups_tries.add(coup)
                nouveau_plateau, nouveaux_scores = self.jouer_coup(courant.plateau, courant.scores, courant.joueur_actif, coup)
                joueur_suivant = 2 if courant.joueur_actif == 1 else 1
                enfant = courant.ajouter_enfant(coup, nouveau_plateau, nouveaux_scores, joueur_suivant)
                return enfant
        return courant

    def _simuler(self, sommet: Sommet) -> float:
        plateau_sim = deepcopy(sommet.plateau)
        scores_sim = deepcopy(sommet.scores)
        joueur_sim = sommet.joueur_actif
        iterations_sim = 0
        while not self.partie_terminee(plateau_sim) and iterations_sim < 100:
            coups_legaux = self.coups_legaux(plateau_sim, joueur_sim)
            if len(coups_legaux) == 0:
                break
            coup = random.choice(coups_legaux)
            plateau_sim, scores_sim = self.jouer_coup(plateau_sim, scores_sim, joueur_sim, coup)
            joueur_sim = 2 if joueur_sim == 1 else 1
            iterations_sim += 1
        return self._evaluer_position(scores_sim, sommet.joueur_actif)

    def _evaluer_position(self, scores: List[int], joueur_original: int) -> float:
        mon_score = scores[joueur_original - 1]
        autre_score = scores[2 - joueur_original]
        if mon_score > autre_score:
            return 1.0
        elif mon_score < autre_score:
            return 0.0
        else:
            return 0.5

    def _selectionner_coup_final(self, racine: Sommet) -> int:
        if not racine.enfants:
            return 0
        coups = list(racine.enfants.keys())
        visites = [racine.enfants[coup].visites for coup in coups]
        if self.temperature == 0:
            return coups[visites.index(max(visites))]
        if sum(visites) == 0:
            return random.choice(coups)
        visites_norm = [v / sum(visites) for v in visites]
        temperatures = [v ** (1.0 / self.temperature) for v in visites_norm]
        sum_temp = sum(temperatures)
        if sum_temp == 0:
            return random.choice(coups)
        probabilites = [t / sum_temp for t in temperatures]
        return random.choices(coups, weights=probabilites, k=1)[0]