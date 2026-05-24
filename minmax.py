from copy import deepcopy
from typing import List, Tuple, Optional


class MinMax:
   

    def __init__(self, profondeur: int = 5):
      
        self.profondeur = profondeur

    def determiner_coup(
        self,
        plateau: List[int],
        scores: List[int],
        joueur_actif: int,
    ) -> int:
        coups = self._coups_legaux(plateau, joueur_actif)
        if not coups:
            return 0

        meilleur_coup = coups[0]
        meilleure_valeur = float("-inf")

        for coup in coups:
            nouveau_plateau, nouveaux_scores, joueur_suivant = self._jouer_coup(
                plateau, scores, joueur_actif, coup
            )
            valeur = self._minimax(
                nouveau_plateau,
                nouveaux_scores,
                joueur_suivant,
                joueur_actif,          # le joueur qu'on cherche à maximiser
                self.profondeur - 1,
                float("-inf"),
                float("inf"),
            )
            if valeur > meilleure_valeur:
                meilleure_valeur = valeur
                meilleur_coup = coup

        return meilleur_coup


    def _minimax(
        self,
        plateau: List[int],
        scores: List[int],
        joueur_actif: int,
        joueur_maximisant: int,
        profondeur: int,
        alpha: float,
        beta: float,
    ) -> float:
        
        # Condition terminale : profondeur 0 ou partie finie
        if profondeur == 0 or self._partie_terminee(plateau):
            return self._evaluer(scores, plateau, joueur_maximisant)

        coups = self._coups_legaux(plateau, joueur_actif)
        if not coups:
            return self._evaluer(scores, plateau, joueur_maximisant)

        if joueur_actif == joueur_maximisant:
            # Nœud MAX : on cherche le coup le plus favorable
            valeur_max = float("-inf")
            for coup in coups:
                nouveau_plateau, nouveaux_scores, joueur_suivant = self._jouer_coup(
                    plateau, scores, joueur_actif, coup
                )
                valeur = self._minimax(
                    nouveau_plateau, nouveaux_scores, joueur_suivant,
                    joueur_maximisant, profondeur - 1, alpha, beta
                )
                valeur_max = max(valeur_max, valeur)
                alpha = max(alpha, valeur_max)
                if beta <= alpha:
                    break  # Coupure bêta : l'adversaire n'ira pas par ici
            return valeur_max
        else:
            # Nœud MIN : l'adversaire cherche à minimiser notre score
            valeur_min = float("inf")
            for coup in coups:
                nouveau_plateau, nouveaux_scores, joueur_suivant = self._jouer_coup(
                    plateau, scores, joueur_actif, coup
                )
                valeur = self._minimax(
                    nouveau_plateau, nouveaux_scores, joueur_suivant,
                    joueur_maximisant, profondeur - 1, alpha, beta
                )
                valeur_min = min(valeur_min, valeur)
                beta = min(beta, valeur_min)
                if beta <= alpha:
                    break  # Coupure alpha : on ne peut pas faire mieux ici
            return valeur_min


    def _evaluer(
        self,
        scores: List[int],
        plateau: List[int],
        joueur_maximisant: int,
    ) -> float:
      
        idx_bot = joueur_maximisant - 1
        idx_adv = 1 - idx_bot

        # Victoire / défaite nette
        if scores[idx_bot] >= 25:
            return float("inf")
        if scores[idx_adv] >= 25:
            return float("-inf")

        # Différence de score pondérée
        diff_score = scores[idx_bot] - scores[idx_adv]

        # Graines dans le camp adverse (potentiel de capture)
        if joueur_maximisant == 1:
            graines_adversaire = sum(plateau[6:12])
            graines_bot = sum(plateau[0:6])
        else:
            graines_adversaire = sum(plateau[0:6])
            graines_bot = sum(plateau[6:12])

        # Heuristique finale : score + avantage territorial léger
        return diff_score * 10 + graines_adversaire * 0.5 - graines_bot * 0.3


    def _coups_legaux(self, plateau: List[int], joueur_actif: int) -> List[int]:
        """Retourne la liste des coups légaux pour le joueur actif."""
        coups = []
        cases = range(0, 6) if joueur_actif == 1 else range(6, 12)
        adversaire_vide = (
            sum(plateau[6:12]) == 0 if joueur_actif == 1 else sum(plateau[0:6]) == 0
        )

        for case in cases:
            if plateau[case] == 0:
                continue
            if adversaire_vide and not self._peut_nourrir(plateau, case, joueur_actif):
                continue
            coups.append(case)
        return coups

    def _peut_nourrir(
        self, plateau: List[int], case: int, joueur_actif: int
    ) -> bool:
        """Vérifie si semer depuis `case` peut alimenter le camp adverse."""
        graines = plateau[case]
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

    def _jouer_coup(
        self,
        plateau: List[int],
        scores: List[int],
        joueur_actif: int,
        coup: int,
    ) -> Tuple[List[int], List[int], int]:
        nouveau_plateau = deepcopy(plateau)
        nouveaux_scores = deepcopy(scores)

        # Semis
        graines = nouveau_plateau[coup]
        nouveau_plateau[coup] = 0
        case_courante = coup
        while graines > 0:
            case_courante = (case_courante + 1) % 12
            if case_courante == coup:
                case_courante = (case_courante + 1) % 12
            nouveau_plateau[case_courante] += 1
            graines -= 1

        # Récolte
        cases_a_recolter = []
        idx_bot = joueur_actif - 1

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
            adversaire_apres = [nouveau_plateau[i] for i in range(0, 6)]
            for p in cases_a_recolter:
                adversaire_apres[p] = 0
            if sum(adversaire_apres) > 0:
                for p in cases_a_recolter:
                    nouveaux_scores[1] += nouveau_plateau[p]
                    nouveau_plateau[p] = 0

        joueur_suivant = 2 if joueur_actif == 1 else 1
        return nouveau_plateau, nouveaux_scores, joueur_suivant

    def _partie_terminee(self, plateau: List[int]) -> bool:
        """Retourne True si la partie est terminée (plateau vide)."""
        return sum(plateau) == 0
