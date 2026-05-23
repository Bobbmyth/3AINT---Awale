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
        if joueur_actif == 1:
            cases = range(0, 6)
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
    
    def _peut_nourrir(self, plateau: List[int], case: int, joueur_actif: int) -> bool:
        graines = plateau[case]
        pos = case
        a_semer = graines
        while a_semer > 0:
            pos = (pos + 1) % 12
            if pos == case:
                pos = (pos + 1) % 12
            if joueur_actif == 1 and pos >= 6:
                return True
            if joueur_actif == 2 and pos < 6:
                return True
            a_semer -= 1
        return False

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
            if case_courante == coup:
                case_courante = (case_courante + 1) % 12            
            nouveau_plateau[case_courante] += 1
            graine -= 1
        cases_a_recolter = []
        if joueur_actif == 1:
            pos = case_courante
            while pos >= 6 and (nouveau_plateau[pos] == 2 or nouveau_plateau[pos] == 3):
                cases_a_recolter.append(pos)
                pos -= 1
            # Vérif anti-affamement
            adversaire_apres = [nouveau_plateau[i] for i in range(6, 12)]
            for p in cases_a_recolter:
                adversaire_apres[p - 6] = 0
            if sum(adversaire_apres) > 0:
                for p in cases_a_recolter:
                    nouveaux_scores[0] += nouveau_plateau[p]
                    nouveau_plateau[p] = 0
        else:
            pos = case_courante
            while pos <= 5 and (nouveau_plateau[pos] == 2 or nouveau_plateau[pos] == 3):
                cases_a_recolter.append(pos)
                pos -= 1
            adversaire_apres = [nouveau_plateau[i] for i in range(0, 6)]
            for p in cases_a_recolter:
                adversaire_apres[p] = 0
            if sum(adversaire_apres) > 0:
                for p in cases_a_recolter:
                    nouveaux_scores[1] += nouveau_plateau[p]
                    nouveau_plateau[p] = 0

        joueur_suivant = 2 if joueur_actif == 1 else 1
        return nouveau_plateau, nouveaux_scores, joueur_suivant

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
        coup = self._selectionner_coup_final(racine)
        if joueur_actif == 2 and coup < 6:
            coups = self.coups_legaux(plateau, joueur_actif)
            return coups[0] if coups else 0
        return coup

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
                nouveau_plateau, nouveaux_scores, joueur_suivant = self.jouer_coup(courant.plateau, courant.scores, courant.joueur_actif, coup)
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
            if not coups_legaux:
                break
            coup = random.choice(coups_legaux)
            plateau_sim, scores_sim, joueur_sim = self.jouer_coup(plateau_sim, scores_sim, joueur_sim, coup)
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
            coups = self.coups_legaux(racine.plateau, racine.joueur_actif)
            return coups[0] if coups else 0
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