"""
Module Sommet - Classe représentant un nœud de l'arborescence de jeu pour MCTS.

La classe Sommet modélise un état du jeu Awalé avec ses statistiques MCTS.
"""

import math
from typing import Optional, List, Tuple
from copy import deepcopy


class Sommet:
    """
    Représente un nœud (sommet) de l'arborescence de jeu pour l'algorithme MCTS.
    
    Chaque sommet contient un état du jeu et maintient des statistiques
    de visite et de victoires pour l'exploration de l'arborescence.
    
    Attributes:
        plateau: État du plateau (liste de 12 cases)
        scores: Scores des deux joueurs [joueur1, joueur2]
        joueur_actif: Le joueur qui doit jouer (1 ou 2)
        parent: Référence au sommet parent (None si racine)
        enfants: Dictionnaire {coup: Sommet} des enfants
        visites: Nombre de fois que ce sommet a été visité
        victoires: Score cumulé des simulations (peut être fractionnaire)
        coups_tries: Ensemble des coups qui ont été explorés
    """
    
    def __init__(self, plateau: List[int], scores: List[int], joueur_actif: int, 
                 parent: Optional['Sommet'] = None):
        """
        Initialise un nouveau sommet.
        
        Args:
            plateau: État du plateau (liste de 12 cases)
            scores: Scores des deux joueurs [joueur1, joueur2]
            joueur_actif: Le joueur à qui c'est de jouer (1 ou 2)
            parent: Le sommet parent dans l'arborescence (None si racine)
        """
        self.plateau = deepcopy(plateau)
        self.scores = deepcopy(scores)
        self.joueur_actif = joueur_actif
        self.parent = parent
        self.enfants = {}  # {coup: Sommet}
        self.visites = 0
        self.victoires = 0.0
        self.coups_tries = set()
    
    def ajouter_enfant(self, coup: int, plateau: List[int], scores: List[int], 
                       joueur_actif: int) -> 'Sommet':
        """
        Ajoute un enfant pour un coup donné.
        
        Args:
            coup: Le coup joué (0-5)
            plateau: État du plateau après le coup
            scores: Scores après le coup
            joueur_actif: Le joueur actif après le coup
            
        Returns:
            Le nouveau sommet enfant créé
        """
        enfant = Sommet(plateau, scores, joueur_actif, parent=self)
        self.enfants[coup] = enfant
        return enfant
    
    def est_feuille(self) -> bool:
        """
        Vérifie si ce sommet est une feuille (pas d'enfants explorés).
        
        Returns:
            True si le sommet n'a pas d'enfants
        """
        return len(self.enfants) == 0
    
    def tous_coups_explores(self, coups_legaux: List[int]) -> bool:
        """
        Vérifie si tous les coups légaux ont été explorés au moins une fois.
        
        Args:
            coups_legaux: Liste des coups licites depuis cet état
            
        Returns:
            True si tous les coups ont au moins un enfant
        """
        return len(self.coups_tries) == len(coups_legaux)
    
    def ucb1(self, c: float = math.sqrt(2)) -> float:
        """
        Calcule la valeur UCB1 pour ce sommet.
        
        La formule UCB1 balance exploitation et exploration:
        UCB1 = (victoires/visites) + c * sqrt(ln(parent.visites) / visites)
        
        Args:
            c: Constante d'exploration (par défaut sqrt(2) ≈ 1.414)
            
        Returns:
            La valeur UCB1 du sommet
            
        Raises:
            ValueError: Si ce sommet n'a pas de parent
        """
        if self.parent is None:
            raise ValueError("Impossible de calculer UCB1 pour la racine")
        
        if self.visites == 0:
            return float('inf')
        
        exploitation = self.victoires / self.visites
        exploration = c * math.sqrt(math.log(self.parent.visites) / self.visites)
        return exploitation + exploration
    
    def meilleur_enfant(self, c: float = 0) -> Tuple[int, 'Sommet']:
        """
        Retourne le meilleur enfant selon UCB1 (ou moyenne si c=0).
        
        Args:
            c: Constante d'exploration
              - 0 : mode exploitation pure (enfant le plus visité)
              - > 0 : mode UCB1 (balance exploitation/exploration)
            
        Returns:
            Tuple (coup, sommet) du meilleur enfant
            
        Raises:
            ValueError: Si aucun enfant n'existe
        """
        if not self.enfants:
            raise ValueError("Aucun enfant disponible")
        
        meilleur = None
        meilleure_valeur = -float('inf')
        meilleur_coup = None
        
        for coup, enfant in self.enfants.items():
            if c == 0:
                # Mode exploitation : enfant le plus visité
                valeur = enfant.victoires / enfant.visites if enfant.visites > 0 else 0
            else:
                # Mode UCB1 : balance exploitation/exploration
                valeur = enfant.ucb1(c)
            
            if valeur > meilleure_valeur:
                meilleure_valeur = valeur
                meilleur = enfant
                meilleur_coup = coup
        
        return meilleur_coup, meilleur
    
    def retropropager(self, score: float):
        """
        Rétropropage le résultat d'une simulation jusqu'à la racine.
        
        Cette méthode remonte l'arborescence en incrémentant le compteur
        de visites et en accumulant les scores de chaque nœud.
        
        Args:
            score: Le score obtenu par la simulation (entre 0 et 1)
                  1.0 = victoire, 0.0 = défaite, 0.5 = nul
        """
        self.visites += 1
        self.victoires += score
        
        if self.parent is not None:
            self.parent.retropropager(score)
    
    def est_racine(self) -> bool:
        """
        Vérifie si ce sommet est la racine de l'arborescence.
        
        Returns:
            True si ce sommet n'a pas de parent
        """
        return self.parent is None
    
    def profondeur(self) -> int:
        """
        Calcule la profondeur de ce sommet dans l'arborescence.
        
        Returns:
            La profondeur (0 pour la racine)
        """
        if self.parent is None:
            return 0
        return 1 + self.parent.profondeur()
    
    def nombre_enfants(self) -> int:
        """
        Retourne le nombre d'enfants explorés.
        
        Returns:
            Le nombre d'enfants
        """
        return len(self.enfants)
    
    def taux_victoires(self) -> float:
        """
        Calcule le taux de victoires (victoires / visites).
        
        Returns:
            Un float entre 0 et 1, ou 0 si le sommet n'a pas été visité
        """
        if self.visites == 0:
            return 0.0
        return self.victoires / self.visites
    
    def __str__(self) -> str:
        """Représentation texte du sommet."""
        return (f"Sommet(joueur={self.joueur_actif}, "
                f"visites={self.visites}, "
                f"victoires={self.victoires:.2f}, "
                f"taux={self.taux_victoires():.2%})")
    
    def __repr__(self) -> str:
        """Représentation Python du sommet."""
        return self.__str__()