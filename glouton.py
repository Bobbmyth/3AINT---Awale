import random
from awale import awale

class GloutonBot:
    def __init__(self, awale_instance, player_id: int):
        """
        Initialise le bot glouton.
        Contient obligatoirement une instance d'Awalé pour respecter la consigne.
        """
        self._awale = awale_instance  
        self._player_id = player_id

    def get_move(self) -> int:
        # Détermination des cases du camp du bot (0-5 pour Joueur 1, 6-11 pour Joueur 2)
        camp = range(6) if self._player_id == 1 else range(6, 12)
        
        # Filtrage des coups strictement autorisés par les règles de TON moteur awale
        coups_legaux = [c for c in camp if self._awale.est_valide(c)]
        
        # Sécurité anti-blocage : si aucun coup légal n'est trouvé, renvoyer la première case par défaut
        if not coups_legaux:
            return 0 if self._player_id == 1 else 6

        meilleur_coup = coups_legaux[0]
        max_capture = -1

        # Analyse gloutonne : on simule chaque coup légal sur une copie locale du plateau
        for coup in coups_legaux:
            graines = self._awale.plateau[coup]
            if graines == 0:
                continue
                
            # Duplication de l'état du plateau pour la simulation en un coup
            plat_temp = self._awale.plateau.copy()
            plat_temp[coup] = 0
            pos = coup
            
            # Étape 1 : Semage des graines
            while graines > 0:
                pos = (pos + 1) % 12
                if pos == coup:  # On saute la case de départ si on fait un tour complet
                    pos = (pos + 1) % 12
                plat_temp[pos] += 1
                graines -= 1
            
            # Étape 2 : Évaluation des captures potentielles générées
            capture = 0
            if self._player_id == 1:
                # Le joueur 1 capture dans le camp du joueur 2 (cases 6 à 11)
                while pos >= 6 and plat_temp[pos] in (2, 3):
                    capture += plat_temp[pos]
                    pos -= 1
            else:
                # Le joueur 2 (le bot par défaut dans main) capture chez le joueur 1 (cases 0 à 5)
                while pos <= 5 and plat_temp[pos] in (2, 3):
                    capture += plat_temp[pos]
                    pos -= 1
            
            # Si ce coup capture plus que les précédents, il devient notre favori
            if capture > max_capture:
                max_capture = capture
                meilleur_coup = coup

        # On retourne un entier pur (ex: 6, 7, 8, 9, 10 ou 11) que main.py va pouvoir exécuter
        return meilleur_coup