from copy import deepcopy
import pygame
from awale import awale
from gui import GUI
from human import Human
from stupidBot import StupidBot
from mcts import MCTS
from minmax import MinMax
from glouton import GloutonBot

jeu = awale("Alice", "Bot")
gui = GUI(jeu)

mode = gui.start_menu()

joueur1 = Human(jeu)
if mode == "pvp":
    joueur2 = Human(jeu)
elif mode == "glouton":
    joueur2 = GloutonBot(jeu, 2)  
else:
    joueur2 = StupidBot(jeu, 2)
mcts = MCTS(iterations_max=500) if mode == "mcts" else None
minmax = MinMax(profondeur=5)      if mode == "minmax" else None

running = True
clock = pygame.time.Clock()

while running:
    gui.dessiner()
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if jeu.joueur_actif == 1:
                coup = joueur1.get_move(event.pos, gui.trous)
            elif jeu.joueur_actif == 2 and mode == "pvp":
                coup = joueur2.get_move(event.pos, gui.trous)
            else:
                coup = None
                
            if coup is not None:
                if not jeu.tour_jeu(coup): 
                    running = False
        
    
    if jeu.joueur_actif == 2 and running and mode in ("bot", "mcts", "minmax", "glouton"):
        print(f"Bot joue, plateau: {jeu.plateau}, joueur: {jeu.joueur_actif}")
        pygame.time.wait(500)  
        
        coup = None  
        
        if mode == "bot":
            coup = joueur2.get_move()
            print(f"Coup choisi (StupidBot): {coup}")
        elif mode == "glouton":
            coup = joueur2.get_move()
            print(f"Coup choisi (Glouton): {coup}")
        elif mode == "mcts":
            coup = mcts.determiner_coup(
                deepcopy(jeu.plateau),
                deepcopy(jeu.score),
                jeu.joueur_actif
            )
            print(f"Coup choisi (MCTS): {coup}")
        elif mode == "minmax":
            coup = minmax.determiner_coup(
                deepcopy(jeu.plateau),
                deepcopy(jeu.score),
                jeu.joueur_actif,
            )
            print(f"Coup choisi (MinMax): {coup}")
            
        if coup is not None:
            print(f"Application du coup {coup} sur le plateau.")
            if not jeu.tour_jeu(coup):
                running = False

    clock.tick(60)

gui.ecran_fin(jeu.gagnant())
pygame.quit()