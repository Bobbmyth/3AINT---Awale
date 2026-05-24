"""
Module Sommet - Classe représentant un nœud de l'arborescence de jeu pour MCTS.
La classe Sommet modélise un état du jeu Awalé avec ses statistiques MCTS.
Version optimisée (0% deepcopy sur les propriétés).
"""

import math
from typing import Optional, List, Tuple


class Sommet:
    """Représente un nœud (sommet) de l'arborescence de jeu pour MCTS."""
    
    def __init__(self, plateau: List[int], scores: List[int], joueur_actif: int, 
                 parent: Optional['Sommet'] = None):
        """Initialise un nouveau sommet."""
        # On garde les copies à l'initialisation pour la sécurité de l'arbre
        self.__plateau = plateau.copy()
        self.__scores = scores.copy()
        self.__joueur_actif = joueur_actif
        self.__parent = parent
        self.__enfants = {}
        self.__visites = 0
        self.__victoires = 0.0
        self.__coups_tries = set()
    
    @property
    def plateau(self) -> List[int]:
        """Retourne une copie rapide du plateau sans deepcopy."""
        return self.__plateau.copy()
    
    @property
    def scores(self) -> List[int]:
        """Retourne une copie rapide des scores sans deepcopy."""
        return self.__scores.copy()
    
    @property
    def joueur_actif(self) -> int:
        """Retourne le joueur actif (1 ou 2)."""
        return self.__joueur_actif
    
    @property
    def parent(self) -> Optional['Sommet']:
        """Retourne le sommet parent (None si racine)."""
        return self.__parent
    
    @property
    def enfants(self) -> dict:
        """Retourne une copie du dictionnaire des enfants."""
        return dict(self.__enfants)
    
    @property
    def visites(self) -> int:
        """Retourne le nombre de visites."""
        return self.__visites
    
    @property
    def victoires(self) -> float:
        """Retourne le cumul de victoires."""
        return self.__victoires
    
    @property
    def coups_tries(self) -> set:
        """Retourne l'ensemble des coups essayés (modifiable pour MCTS)."""
        return self.__coups_tries
    
    def ajouter_enfant(self, coup: int, plateau: List[int], scores: List[int], 
                       joueur_actif: int) -> 'Sommet':
        """Ajoute un enfant pour un coup donné."""
        enfant = Sommet(plateau, scores, joueur_actif, parent=self)
        self.__enfants[coup] = enfant
        return enfant
    
    def est_feuille(self) -> bool:
        """Vérifie si ce sommet est une feuille."""
        return len(self.__enfants) == 0
    
    def tous_coups_explores(self, coups_legaux: List[int]) -> bool:
        """Vérifie si tous les coups légaux ont été explorés."""
        return len(self.__coups_tries) == len(coups_legaux)
    
    def ucb1(self, c: float = math.sqrt(2)) -> float:
        """Calcule la valeur UCB1 pour ce sommet."""
        if self.__parent is None:
            raise ValueError("Impossible de calculer UCB1 pour la racine")
        
        if self.__visites == 0:
            return float('inf')
        
        exploitation = self.__victoires / self.__visites
        exploration = c * math.sqrt(math.log(self.__parent._Sommet__visites) / self.__visites)
        return exploitation + exploration
    
    def meilleur_enfant(self, c: float = 0) -> Tuple[int, 'Sommet']:
        """Retourne le meilleur enfant selon UCB1."""
        if not self.__enfants:
            raise ValueError("Aucun enfant disponible")
        
        meilleur = None
        meilleure_valeur = -float('inf')
        meilleur_coup = None
        
        for coup, enfant in self.__enfants.items():
            if c == 0:
                valeur = enfant._Sommet__victoires / enfant._Sommet__visites if enfant._Sommet__visites > 0 else 0
            else:
                valeur = enfant.ucb1(c)
            
            if valeur > meilleure_valeur:
                meilleure_valeur = valeur
                meilleur = enfant
                meilleur_coup = coup
        
        return meilleur_coup, meilleur
    
    def retropropager(self, score: float):
        """Rétropropage le résultat d'une simulation jusqu'à la racine."""
        self.__visites += 1
        self.__victoires += score
        
        if self.__parent is not None:
            self.__parent.retropropager(score)
    
    def est_racine(self) -> bool:
        """Vérifie si ce sommet est la racine."""
        return self.__parent is None
    
    def profondeur(self) -> int:
        """Calcule la profondeur de ce sommet."""
        if self.__parent is None:
            return 0
        return 1 + self.__parent.profondeur()
    
    def nombre_enfants(self) -> int:
        """Retourne le nombre d'enfants explorés."""
        return len(self.__enfants)
    
    def taux_victoires(self) -> float:
        """Retourne le taux de victoires."""
        if self.__visites == 0:
            return 0.0
        return self.__victoires / self.__visites
    
    def __str__(self) -> str:
        """Représentation texte du sommet."""
        return (f"Sommet(joueur={self.__joueur_actif}, "
                f"visites={self.__visites}, "
                f"victoires={self.__victoires:.2f}, "
                f"taux={self.taux_victoires():.2%})")
    
    def __repr__(self) -> str:
        """Représentation Python du sommet."""
        return self.__str__()