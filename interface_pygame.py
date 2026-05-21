"""
Interface graphique Pygame pour le jeu d'Awalé.

Permet de jouer au jeu d'Awalé contre une IA MCTS ou contre un autre joueur.
Offre une expérience visuelle riche avec animations et effets graphiques.
"""

import pygame
import sys
import threading
import math
from enum import Enum
from typing import Optional, Tuple, List
from mcts import MCTS
from awale import awale


class Etat(Enum):
    """États possibles du jeu."""
    MENU = 1
    SELECTIONNER_MODE = 2
    SELECTIONNER_JOUEUR = 3
    EN_JEU = 4
    FIN_PARTIE = 5


class Couleurs:
    """Palette de couleurs."""
    NOIR = (15, 15, 20)
    BLANC = (255, 255, 255)
    BLEU_PRINCIPAL = (45, 156, 219)
    ORANGE_ACCENT = (243, 156, 18)
    GRIS_CLAIR = (200, 200, 200)
    GRIS_FONCE = (50, 50, 60)
    VERT_SUCCES = (46, 204, 113)
    ROUGE_ERREUR = (231, 76, 60)
    FOND_CASE = (42, 42, 50)
    SURBRILLANCE = (255, 193, 7)


class Bouton:
    """Classe pour gérer les boutons."""
    
    def __init__(self, x: int, y: int, largeur: int, hauteur: int, 
                 texte: str, couleur: Tuple[int, int, int], 
                 couleur_hover: Tuple[int, int, int], 
                 font: pygame.font.Font):
        """
        Crée un bouton.
        
        Args:
            x: Position x
            y: Position y
            largeur: Largeur du bouton
            hauteur: Hauteur du bouton
            texte: Texte du bouton
            couleur: Couleur du bouton
            couleur_hover: Couleur au survol
            font: Police d'écriture
        """
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.couleur = couleur
        self.couleur_hover = couleur_hover
        self.couleur_actuelle = couleur
        self.font = font
        self.survole = False
    
    def dessiner(self, surface: pygame.Surface):
        """Dessine le bouton."""
        # Ombre
        ombre_rect = self.rect.copy()
        ombre_rect.y += 3
        pygame.draw.rect(surface, (0, 0, 0), ombre_rect, border_radius=8)
        
        # Bouton
        pygame.draw.rect(surface, self.couleur_actuelle, self.rect, border_radius=8)
        pygame.draw.rect(surface, Couleurs.BLANC, self.rect, 2, border_radius=8)
        
        # Texte
        texte_surface = self.font.render(self.texte, True, Couleurs.BLANC)
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        surface.blit(texte_surface, texte_rect)
    
    def est_clique(self, pos: Tuple[int, int]) -> bool:
        """Vérifie si le bouton est cliqué."""
        return self.rect.collidepoint(pos)
    
    def mettre_a_jour(self, pos_souris: Tuple[int, int]):
        """Met à jour l'état du bouton."""
        self.survole = self.rect.collidepoint(pos_souris)
        self.couleur_actuelle = self.couleur_hover if self.survole else self.couleur


class CaseAwalé:
    """Classe représentant une case du plateau."""
    
    def __init__(self, x: int, y: int, rayon: int, index: int, font: pygame.font.Font):
        """
        Crée une case.
        
        Args:
            x: Position x du centre
            y: Position y du centre
            rayon: Rayon de la case
            index: Index de la case
            font: Police d'écriture
        """
        self.x = x
        self.y = y
        self.rayon = rayon
        self.index = index
        self.font = font
        self.nombre = 0
        self.cliquable = False
        self.animation = 0
    
    def dessiner(self, surface: pygame.Surface):
        """Dessine la case."""
        # Couleur basée sur le joueur
        if self.index < 6:
            couleur = Couleurs.BLEU_PRINCIPAL
        else:
            couleur = Couleurs.ORANGE_ACCENT
        
        # Surbrillance si cliquable
        if self.cliquable:
            couleur = Couleurs.SURBRILLANCE
            # Animation de pulsation
            self.animation = (self.animation + 0.05) % (2 * math.pi)
            rayon_anime = self.rayon + 5 * math.sin(self.animation)
        else:
            rayon_anime = self.rayon
        
        # Ombre
        pygame.draw.circle(surface, (0, 0, 0), (self.x + 3, self.y + 3), self.rayon)
        
        # Cercle principal
        pygame.draw.circle(surface, couleur, (self.x, self.y), int(rayon_anime))
        pygame.draw.circle(surface, Couleurs.BLANC, (self.x, self.y), int(rayon_anime), 2)
        
        # Nombre
        texte_surface = self.font.render(str(self.nombre), True, Couleurs.BLANC)
        texte_rect = texte_surface.get_rect(center=(self.x, self.y))
        surface.blit(texte_surface, texte_rect)
    
    def est_clique(self, pos: Tuple[int, int]) -> bool:
        """Vérifie si la case est cliquée."""
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance <= self.rayon


class InterfaceAwalePygame:
    """Interface graphique Pygame pour Awalé."""
    
    def __init__(self, largeur: int = 1200, hauteur: int = 800):
        """
        Initialise l'interface.
        
        Args:
            largeur: Largeur de la fenêtre
            hauteur: Hauteur de la fenêtre
        """
        pygame.init()
        self.largeur = largeur
        self.hauteur = hauteur
        self.surface = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Awalé - Jeu de Stratégie")
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Polices
        self.font_titre = pygame.font.Font(None, 72)
        self.font_grand = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_petit = pygame.font.Font(None, 24)
        
        # État
        self.etat = Etat.MENU
        self.jeu: Optional[awale] = None
        self.mcts: Optional[MCTS] = None
        self.mode_jeu: Optional[str] = None
        self.joueur_ia: Optional[int] = None
        self.ia_en_train_de_jouer = False
        
        # Éléments graphiques
        self.cases: List[CaseAwalé] = []
        self.boutons_menu = []
        self.boutons_selectionneur = []
        self.boutons_joueur = []
        self.boutons_fin = []
        
        self.creer_cases()
        self.creer_boutons()
    
    def creer_cases(self):
        """Crée les cases du plateau."""
        self.cases = []
        rayon = 35
        espacement_x = 100
        espacement_y = 150
        
        start_x = 150
        start_y = 300
        
        # Cases du joueur 1 (bas, gauche à droite)
        for i in range(6):
            x = start_x + i * espacement_x
            y = start_y
            self.cases.append(CaseAwalé(x, y, rayon, i, self.font_normal))
        
        # Cases du joueur 2 (haut, droite à gauche)
        for i in range(6):
            x = start_x + (5 - i) * espacement_x
            y = start_y - espacement_y
            self.cases.append(CaseAwalé(x, y, rayon, 11 - i, self.font_normal))
    
    def creer_boutons(self):
        """Crée tous les boutons."""
        largeur_btn = 200
        hauteur_btn = 50
        
        # Boutons du menu
        self.boutons_menu = [
            Bouton(500, 350, largeur_btn, hauteur_btn, "👥 PvP", 
                   Couleurs.BLEU_PRINCIPAL, Couleurs.SURBRILLANCE, self.font_normal),
            Bouton(500, 430, largeur_btn, hauteur_btn, "🤖 vs IA", 
                   Couleurs.ORANGE_ACCENT, Couleurs.SURBRILLANCE, self.font_normal),
            Bouton(500, 510, largeur_btn, hauteur_btn, "❌ Quitter", 
                   Couleurs.ROUGE_ERREUR, Couleurs.SURBRILLANCE, self.font_normal),
        ]
        
        # Boutons de sélection du mode
        self.boutons_selectionneur = [
            Bouton(300, 350, 280, 50, "Joueur 1 (vous commencez)", 
                   Couleurs.BLEU_PRINCIPAL, Couleurs.SURBRILLANCE, self.font_normal),
            Bouton(620, 350, 280, 50, "Joueur 2 (IA commence)", 
                   Couleurs.ORANGE_ACCENT, Couleurs.SURBRILLANCE, self.font_normal),
            Bouton(460, 450, 280, 50, "Retour", 
                   Couleurs.GRIS_FONCE, Couleurs.SURBRILLANCE, self.font_normal),
        ]
        
        # Boutons de fin
        self.boutons_fin = [
            Bouton(400, 500, 200, 50, "Menu", 
                   Couleurs.BLEU_PRINCIPAL, Couleurs.SURBRILLANCE, self.font_normal),
            Bouton(600, 500, 200, 50, "Quitter", 
                   Couleurs.ROUGE_ERREUR, Couleurs.SURBRILLANCE, self.font_normal),
        ]
    
    def dessiner_menu(self):
        """Dessine le menu principal."""
        self.surface.fill(Couleurs.NOIR)
        
        # Titre
        titre = self.font_titre.render("🎮 AWALÉ 🎮", True, Couleurs.BLEU_PRINCIPAL)
        titre_rect = titre.get_rect(center=(self.largeur // 2, 100))
        self.surface.blit(titre, titre_rect)
        
        # Sous-titre
        sous_titre = self.font_normal.render(
            "Jeu de Stratégie Traditionnel Africain",
            True, Couleurs.ORANGE_ACCENT
        )
        sous_rect = sous_titre.get_rect(center=(self.largeur // 2, 180))
        self.surface.blit(sous_titre, sous_rect)
        
        # Boutons
        for bouton in self.boutons_menu:
            bouton.dessiner(self.surface)
        
        pygame.display.flip()
    
    def dessiner_selectionneur_joueur(self):
        """Dessine l'écran de sélection du joueur IA."""
        self.surface.fill(Couleurs.NOIR)
        
        # Titre
        titre = self.font_grand.render("Choisissez votre position", True, Couleurs.BLEU_PRINCIPAL)
        titre_rect = titre.get_rect(center=(self.largeur // 2, 100))
        self.surface.blit(titre, titre_rect)
        
        # Boutons
        for bouton in self.boutons_selectionneur:
            bouton.dessiner(self.surface)
        
        pygame.display.flip()
    
    def dessiner_plateau(self):
        """Dessine le plateau de jeu."""
        self.surface.fill(Couleurs.NOIR)
        
        # Fond du plateau
        plateau_rect = pygame.Rect(80, 150, self.largeur - 160, 450)
        pygame.draw.rect(self.surface, Couleurs.GRIS_FONCE, plateau_rect, border_radius=20)
        pygame.draw.rect(self.surface, Couleurs.BLANC, plateau_rect, 3, border_radius=20)
        
        # Mettre à jour les cases
        for i, case in enumerate(self.cases):
            case.nombre = self.jeu.plateau[case.index]
            case.cliquable = False
            
            # Marquer les cases cliquables
            if self.jeu.joueur_actif == 1 and i < 6 and self.jeu.plateau[i] > 0:
                case.cliquable = True
            elif self.jeu.joueur_actif == 2 and i >= 6 and self.jeu.plateau[self.cases[i].index] > 0:
                case.cliquable = True
            
            # Désactiver si l'IA joue
            if self.ia_en_train_de_jouer:
                case.cliquable = False
        
        # Dessiner les cases
        for case in self.cases:
            case.dessiner(self.surface)
        
        # Afficher les joueurs
        joueur1_text = self.font_petit.render(
            f"{self.jeu.nom_joueur1}", 
            True, Couleurs.BLEU_PRINCIPAL
        )
        joueur1_rect = joueur1_text.get_rect(center=(120, 320))
        self.surface.blit(joueur1_text, joueur1_rect)
        
        joueur2_text = self.font_petit.render(
            f"{self.jeu.nom_joueur2}", 
            True, Couleurs.ORANGE_ACCENT
        )
        joueur2_rect = joueur2_text.get_rect(center=(120, 200))
        self.surface.blit(joueur2_text, joueur2_rect)
        
        # Afficher les scores
        score_text = self.font_normal.render(
            f"Scores - {self.jeu.nom_joueur1}: {self.jeu.score[0]} | {self.jeu.nom_joueur2}: {self.jeu.score[1]}",
            True, Couleurs.BLANC
        )
        score_rect = score_text.get_rect(center=(self.largeur // 2, 50))
        self.surface.blit(score_text, score_rect)
        
        # Afficher le joueur actuel
        joueur_actuel = self.jeu.nom_joueur1 if self.jeu.joueur_actif == 1 else self.jeu.nom_joueur2
        couleur = Couleurs.BLEU_PRINCIPAL if self.jeu.joueur_actif == 1 else Couleurs.ORANGE_ACCENT
        tour_text = self.font_normal.render(f"À jouer: {joueur_actuel}", True, couleur)
        tour_rect = tour_text.get_rect(center=(self.largeur // 2, 620))
        self.surface.blit(tour_text, tour_rect)
        
        # Bouton menu
        bouton_menu = Bouton(self.largeur - 150, 730, 120, 40, "📋 Menu",
                            Couleurs.GRIS_FONCE, Couleurs.SURBRILLANCE, self.font_petit)
        bouton_menu.dessiner(self.surface)
        
        pygame.display.flip()
    
    def dessiner_fin_partie(self):
        """Dessine l'écran de fin de partie."""
        self.surface.fill(Couleurs.NOIR)
        
        # Titre
        titre = self.font_grand.render("Partie Terminée!", True, Couleurs.VERT_SUCCES)
        titre_rect = titre.get_rect(center=(self.largeur // 2, 150))
        self.surface.blit(titre, titre_rect)
        
        # Résultat
        resultat = self.jeu.gagnant()
        resultat_text = self.font_normal.render(resultat, True, Couleurs.SURBRILLANCE)
        resultat_rect = resultat_text.get_rect(center=(self.largeur // 2, 300))
        self.surface.blit(resultat_text, resultat_rect)
        
        # Scores finaux
        scores_text = self.font_normal.render(
            f"{self.jeu.nom_joueur1}: {self.jeu.score[0]} | {self.jeu.nom_joueur2}: {self.jeu.score[1]}",
            True, Couleurs.BLANC
        )
        scores_rect = scores_text.get_rect(center=(self.largeur // 2, 400))
        self.surface.blit(scores_text, scores_rect)
        
        # Boutons
        for bouton in self.boutons_fin:
            bouton.dessiner(self.surface)
        
        pygame.display.flip()
    
    def gerer_menu(self, pos_souris: Tuple[int, int], clique: bool):
        """Gère les interactions du menu."""
        for i, bouton in enumerate(self.boutons_menu):
            bouton.mettre_a_jour(pos_souris)
            if clique and bouton.est_clique(pos_souris):
                if i == 0:  # PvP
                    self.mode_jeu = "pvp"
                    self.demander_noms_pvp()
                elif i == 1:  # vs IA
                    self.mode_jeu = "pvia"
                    self.etat = Etat.SELECTIONNER_JOUEUR
                elif i == 2:  # Quitter
                    return False
        return True
    
    def gerer_selectionneur_joueur(self, pos_souris: Tuple[int, int], clique: bool):
        """Gère les interactions du sélectionneur de joueur."""
        for i, bouton in enumerate(self.boutons_selectionneur):
            bouton.mettre_a_jour(pos_souris)
            if clique and bouton.est_clique(pos_souris):
                if i == 0:  # Joueur 1
                    self.joueur_ia = 2
                    self.mcts = MCTS(iterations_max=500, temperature=0.1)
                    self.demarrer_pvia()
                elif i == 1:  # Joueur 2
                    self.joueur_ia = 1
                    self.mcts = MCTS(iterations_max=500, temperature=0.1)
                    self.demarrer_pvia()
                elif i == 2:  # Retour
                    self.etat = Etat.MENU
    
    def gerer_plateau(self, pos_souris: Tuple[int, int], clique: bool):
        """Gère les interactions du plateau."""
        if clique:
            # Vérifier si le bouton menu est cliqué
            bouton_menu = pygame.Rect(self.largeur - 150, 730, 120, 40)
            if bouton_menu.collidepoint(pos_souris):
                self.etat = Etat.MENU
                return
            
            # Vérifier si une case est cliquée
            for case in self.cases:
                if case.cliquable and case.est_clique(pos_souris):
                    self.jouer_coup(case.index)
                    return
    
    def gerer_fin_partie(self, pos_souris: Tuple[int, int], clique: bool):
        """Gère les interactions de fin de partie."""
        for i, bouton in enumerate(self.boutons_fin):
            bouton.mettre_a_jour(pos_souris)
            if clique and bouton.est_clique(pos_souris):
                if i == 0:  # Menu
                    self.etat = Etat.MENU
                elif i == 1:  # Quitter
                    return False
        return True
    
    def demander_noms_pvp(self):
        """Demande les noms pour PvP (interface simple)."""
        # Pour simplifier, utiliser des noms par défaut
        self.jeu = awale("Joueur 1", "Joueur 2")
        self.etat = Etat.EN_JEU
    
    def demarrer_pvia(self):
        """Démarre une partie PvIA."""
        self.jeu = awale("Vous", "IA")
        self.etat = Etat.EN_JEU
        
        # Si l'IA commence
        if self.joueur_ia == 1:
            self.jouer_ia()
    
    def jouer_coup(self, index: int):
        """Joue un coup."""
        if self.ia_en_train_de_jouer:
            return
        
        # Convertir l'index global en index local (0-5)
        if self.jeu.joueur_actif == 1:
            coup = index
        else:
            coup = index - 6
        
        if self.jeu.est_valide(coup):
            self.jeu.tour_jeu(coup)
            
            # Vérifier la fin de partie
            if self.jeu.plateau.count(0) == 12:
                self.etat = Etat.FIN_PARTIE
            elif self.mode_jeu == "pvia" and self.jeu.joueur_actif == self.joueur_ia:
                self.jouer_ia()
    
    def jouer_ia(self):
        """L'IA joue son coup."""
        self.ia_en_train_de_jouer = True
        
        def executer_ia():
            coup = self.mcts.determiner_coup(self.jeu.plateau, self.jeu.score, self.jeu.joueur_actif)
            if self.jeu.est_valide(coup):
                self.jeu.tour_jeu(coup)
            
            # Vérifier la fin de partie
            if self.jeu.plateau.count(0) == 12:
                self.etat = Etat.FIN_PARTIE
            
            self.ia_en_train_de_jouer = False
        
        thread = threading.Thread(target=executer_ia, daemon=True)
        thread.start()
    
    def run(self):
        """Boucle principale."""
        running = True
        
        while running:
            pos_souris = pygame.mouse.get_pos()
            clique = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    clique = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.etat = Etat.MENU
            
            # Gérer les états
            if self.etat == Etat.MENU:
                running = self.gerer_menu(pos_souris, clique)
                self.dessiner_menu()
            
            elif self.etat == Etat.SELECTIONNER_JOUEUR:
                self.gerer_selectionneur_joueur(pos_souris, clique)
                self.dessiner_selectionneur_joueur()
            
            elif self.etat == Etat.EN_JEU:
                self.gerer_plateau(pos_souris, clique)
                self.dessiner_plateau()
            
            elif self.etat == Etat.FIN_PARTIE:
                running = self.gerer_fin_partie(pos_souris, clique)
                self.dessiner_fin_partie()
            
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()


def main():
    """Point d'entrée principal."""
    interface = InterfaceAwalePygame(1200, 800)
    interface.run()


if __name__ == "__main__":
    main()